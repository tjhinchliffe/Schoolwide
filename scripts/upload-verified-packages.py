"""Transfer approved binary-only archives; never receive a private repository token.

The temporary manifest holds expiring read-only URLs and GitHub's archive digests.
Native build jobs verify installers before the repository owner supplies the manifest.
The workflow uploads a draft; publication remains a separate owner action.
"""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
import zipfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def transfer(item, directory, version, source_commit):
    platform = item['platform']
    binary = {
        'win32-x64': f'Schoolwide-{version}-Windows-x64-Setup.exe',
        'darwin-arm64': f'Schoolwide-{version}-macOS-arm64.dmg',
        'darwin-x64': f'Schoolwide-{version}-macOS-x64.dmg',
    }[platform]
    report_name = 'windows-packaged.json' if platform == 'win32-x64' else f'macos-{platform.split("-")[1]}-packaged.json'
    url = urllib.parse.urlsplit(item['url'])
    require(url.scheme == 'https' and not url.username and not url.password, 'Invalid transfer URL')
    require(url.hostname.endswith('.blob.core.windows.net') or url.hostname.endswith('.actions.githubusercontent.com'), 'Unapproved artifact host')
    expected = item['digest'].removeprefix('sha256:')
    require(bool(re.fullmatch('[0-9a-f]{64}', expected)), 'Invalid archive digest')
    archive_path = directory / (platform + '.zip')
    digest = hashlib.sha256()
    with urllib.request.urlopen(item['url'], timeout=120) as response, archive_path.open('wb') as output:
        while chunk := response.read(4 * 1024 * 1024):
            digest.update(chunk)
            output.write(chunk)
    require(digest.hexdigest() == expected, 'Archive checksum mismatch')
    with zipfile.ZipFile(archive_path) as archive:
        def member(name):
            matches = [entry for entry in archive.infolist() if Path(entry.filename).name == name and not entry.is_dir()]
            require(len(matches) == 1, 'Expected exactly one ' + name)
            return matches[0]
        report_info = member(report_name)
        require(report_info.file_size < 1024 * 1024, 'Report exceeds size limit')
        report = json.loads(archive.read(report_info))
        require(report['version'] == version and report['platform'] == platform, 'Wrong package version or platform')
        require(report['sourceCommit'] == source_commit, 'Wrong native build source commit')
        require(report['systemPythonUnavailable'] is True, 'Bundled-runtime verification missing')
        require(report.get('installed') is True if platform == 'win32-x64' else report.get('mountedDiskImageVerified') is True, 'Native package verification missing')
        binary_path = directory / binary
        digest = hashlib.sha256()
        with archive.open(member(binary)) as source, binary_path.open('wb') as output:
            while chunk := source.read(4 * 1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        checksum = digest.hexdigest()
        require(checksum == report['sha256'], 'Binary differs from native verification report')
        checksum_info = member(binary + '.sha256')
        require(checksum_info.file_size < 1024, 'Checksum file exceeds size limit')
        line = archive.read(checksum_info).decode('utf-8-sig').strip().split()
        require(line == [checksum, binary], 'Companion checksum mismatch')
        checksum_path = directory / (binary + '.sha256')
        checksum_path.write_text(f'{checksum}  {binary}\n')
    archive_path.unlink()
    print(f'Validated {binary}: SHA256 {checksum}', flush=True)
    return [binary_path, checksum_path]


def main():
    manifest = json.loads(os.environ['SCHOOLWIDE_PACKAGE_MANIFEST'])
    require(manifest['tag'] == 'V' + manifest['version'], 'Tag/version mismatch')
    require(bool(re.fullmatch(r'\d+\.\d+\.\d+', manifest['version'])), 'Invalid version')
    require(bool(re.fullmatch('[0-9a-f]{40}', manifest['sourceCommit'])), 'Invalid source commit')
    require(sorted(item['platform'] for item in manifest['artifacts']) == ['darwin-arm64', 'darwin-x64', 'win32-x64'], 'Three approved platforms required')
    repo = os.environ['GITHUB_REPOSITORY']
    release = json.loads(subprocess.check_output(['gh', 'release', 'view', manifest['tag'], '--repo', repo, '--json', 'isDraft,assets']))
    require(release['isDraft'], 'Release must remain a draft during transfer')
    require(not release['assets'], 'Draft assets already exist; review before retrying')
    with tempfile.TemporaryDirectory(prefix='verified-schoolwide-') as folder:
        directory = Path(folder)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(transfer, item, directory, manifest['version'], manifest['sourceCommit']) for item in manifest['artifacts']]
            files = [file for future in futures for file in future.result()]
        subprocess.run(['gh', 'release', 'upload', manifest['tag'], '--repo', repo, *map(str, files)], check=True)
    print('All six verified assets uploaded. Release remains a draft.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Download exceptions can contain the temporary signed URL. Never log it.
        print('Package validation or transfer failed: ' + type(error).__name__, flush=True)
        raise SystemExit(1) from None
