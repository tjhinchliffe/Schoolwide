# MOSAIC Schoolwide

## Download V2027.0.2

| Computer | Download |
| --- | --- |
| Windows 64-bit (x64) | [Windows installer](https://github.com/tjhinchliffe/Schoolwide/releases/download/V2027.0.2/Schoolwide-2027.0.2-Windows-x64-Setup.exe) |
| Mac with Apple Silicon (M-series chip) | [macOS Apple Silicon disk image](https://github.com/tjhinchliffe/Schoolwide/releases/download/V2027.0.2/Schoolwide-2027.0.2-macOS-arm64.dmg) |
| Mac with an Intel processor | [macOS Intel disk image](https://github.com/tjhinchliffe/Schoolwide/releases/download/V2027.0.2/Schoolwide-2027.0.2-macOS-x64.dmg) |

[Release notes and SHA256 checksums](https://github.com/tjhinchliffe/Schoolwide/releases/tag/V2027.0.2)

**Windows download refreshed 6 November 2026:** the Windows installer now includes the in-app updater and the previously verified Windows improvements. The Mac downloads remain the original 3 November builds. All still report version **2027.0.2**. If you already have an older Windows 2027.0.2 installation, download and run the Windows installer once to obtain the updater; future higher-version releases can then be offered inside Schoolwide.

On Windows, run the installer. On a Mac, open the disk image and drag **MOSAIC Schoolwide** into **Applications**, then open it there. Use **About This Mac** to check whether your Mac has an Apple chip or an Intel processor. The Mac packages are tested on macOS 15.

Python and the PDF browser are included. No separate Python, Node or developer tools are needed.

The Windows installer is unsigned. Mac packages have ad-hoc integrity signatures and are not Apple Developer ID signed or notarized. Managed devices may require school IT approval. If macOS blocks opening, follow your school’s installation process; [Apple explains its app security controls](https://support.apple.com/en-au/102445).

## Get started

Open **Configuration** to set the school profile and current student list, then **Import** to bring in assessment results. Open **Welcome → Help Guide** for 37 step-by-step tasks illustrated with 37 screenshots, including assessment dates, custom measures, live dashboard/table setup, templates, student notes and interactive HTML sharing. Shared Assessment ZIPs include their accompanying measures and install them automatically in the recipient’s Assessment Measures library.

The exact Windows installer and both mounted Mac disk images are verified with their bundled runtimes. Checks cover imports, configuration, zoom, backup/restore, Excel/PDF exports, populated templates, offline Help, and the offline Dashboard, Table and Students HTML viewer.

This repository provides public downloads. Application source remains in the private build repository. No school database, imported student list or user profile is included in these packages.
