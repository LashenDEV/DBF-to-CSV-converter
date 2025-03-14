# DBF to CSV Converter

## Overview
DBF to CSV Converter is a simple graphical application that allows users to convert dBASE (.dbf) files to CSV format. The application provides a user-friendly interface for selecting multiple DBF files, choosing an output directory, and converting them in batch.

## Installation

### From Debian Package
To install the DBF to CSV Converter on Ubuntu or Debian-based systems:

1. Download the Debian package (`dbf-converter-1.0.0.deb`)
2. Open a terminal and navigate to the directory containing the package
3. Run the installation command:
   ```
   sudo dpkg -i dbf-converter-1.0.0.deb
   ```
4. If there are dependency issues, run:
   ```
   sudo apt --fix-broken install
   ```

### Building the Package
If you need to build the package from source:

1. Clone or download the source code
2. Navigate to the source directory
3. Run the package build command:
   ```
   dpkg-deb --build --root-owner-group dbf-converter-1.0.0
   ```
4. This will create a `dbf-converter-1.0.0.deb` file in the parent directory

## Usage

1. Launch the application from your applications menu or by running `dbf-converter` in the terminal
2. Add DBF files by clicking the "Add Files" button
3. Select the output directory where the CSV files will be saved
4. Click "Convert All Files" to begin the conversion process
5. Monitor the progress in the conversion log

## Features

- Convert multiple DBF files to CSV format simultaneously
- Progress tracking for each file conversion
- Detailed conversion log
- Simple and intuitive user interface
- Preserves field names and data types from the original DBF files

## Dependencies

- Python 3
- PyQt5
- dbfread

## Uninstallation

To remove the application:

```
sudo dpkg -r dbf-converter
```

## Troubleshooting

### Common Issues

1. **Missing dependencies**: If you encounter errors about missing Python packages, install them with:
   ```
   pip install PyQt5 dbfread
   ```

2. **Permission errors**: Ensure you have write permissions for the selected output directory

3. **Icon not displaying correctly**: If the application icon doesn't show properly in the taskbar, try logging out and back in to refresh the icon cache

### Error Reporting

If you encounter any issues with the application, please report them by creating an issue in the project repository with:

1. A description of the problem
2. Steps to reproduce the issue
3. The error message (if any)
4. Your system information (OS version, Python version)