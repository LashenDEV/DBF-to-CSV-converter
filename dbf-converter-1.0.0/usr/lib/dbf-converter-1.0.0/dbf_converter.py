#!/usr/bin/env python3
import os
import csv
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar,
                             QMessageBox, QGroupBox, QFrame, QListWidget, QSplitter,
                             QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from dbfread import DBF


class ConversionWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    conversion_complete = pyqtSignal(str)
    conversion_failed = pyqtSignal(str, str)

    def __init__(self, input_path, output_dir):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir

    def run(self):
        try:
            # Get the base filename without extension
            base_name = os.path.basename(self.input_path)
            file_name_without_ext = os.path.splitext(base_name)[0]
            output_path = os.path.join(self.output_dir, f"{file_name_without_ext}.csv")

            # Read the DBF file
            dbf = DBF(self.input_path)

            # Get total number of records for progress tracking
            total_records = len(dbf)

            # Emit initial progress
            self.progress_updated.emit(0, f"Converting {base_name}: Starting...")

            # Write to CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)

                # Write header
                writer.writerow(dbf.field_names)

                # Write records with progress update
                for i, record in enumerate(dbf):
                    writer.writerow([record[field] for field in dbf.field_names])

                    # Update progress bar
                    if i % 50 == 0 or i == total_records - 1:  # Update every 50 records or at the end
                        progress_value = int((i + 1) / total_records * 100)
                        self.progress_updated.emit(progress_value,
                                                   f"Converting {base_name}: {progress_value}% complete")

            self.conversion_complete.emit(output_path)

        except Exception as e:
            self.conversion_failed.emit(base_name, str(e))


class DBFtoCSVConverter(QMainWindow):
    def __init__(self):
        # Call the parent class initializer
        super(DBFtoCSVConverter, self).__init__()

        self.setObjectName("dbf-converter")
        # Configure the main window
        self.setWindowTitle("DBF to CSV Converter")
        self.setMinimumSize(800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("DBF to CSV Converter")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Input file selection
        input_group = QGroupBox("Select DBF Files")
        input_layout = QVBoxLayout(input_group)

        # List of selected files
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        input_layout.addWidget(self.files_list)

        # Buttons for file selection
        file_buttons_layout = QHBoxLayout()
        add_files_button = QPushButton("Add Files")
        add_files_button.clicked.connect(self.add_files)
        file_buttons_layout.addWidget(add_files_button)

        remove_files_button = QPushButton("Remove Selected")
        remove_files_button.clicked.connect(self.remove_files)
        file_buttons_layout.addWidget(remove_files_button)

        clear_all_button = QPushButton("Clear All")
        clear_all_button.clicked.connect(self.clear_files)
        file_buttons_layout.addWidget(clear_all_button)

        input_layout.addLayout(file_buttons_layout)
        main_layout.addWidget(input_group)

        # Output directory selection
        output_group = QGroupBox("Select Output Directory")
        output_layout = QHBoxLayout(output_group)
        self.output_path = QLineEdit()
        output_layout.addWidget(self.output_path)
        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(self.browse_output)
        output_layout.addWidget(browse_output_button)
        main_layout.addWidget(output_group)

        # Progress section
        progress_group = QGroupBox("Conversion Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)

        # Log of converted files
        log_label = QLabel("Conversion Log:")
        progress_layout.addWidget(log_label)

        self.conversion_log = QListWidget()
        self.conversion_log.setMaximumHeight(150)
        progress_layout.addWidget(self.conversion_log)

        main_layout.addWidget(progress_group)

        # Convert button
        convert_layout = QHBoxLayout()

        convert_button = QPushButton("Convert All Files")
        convert_button.setMinimumHeight(40)
        convert_button.clicked.connect(self.convert_files)
        convert_layout.addWidget(convert_button)

        main_layout.addLayout(convert_layout)

        # Status bar
        self.statusBar().showMessage("Ready to convert multiple DBF files to CSV")

        # Member variables
        self.workers = []
        self.current_file_index = 0

    def add_files(self):
        """Open a file dialog to select multiple input DBF files"""
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Select DBF Files", "", "DBF Files (*.dbf);;All Files (*.*)"
        )

        if filenames:
            for filename in filenames:
                # Check if the file is already in the list
                exists = False
                for i in range(self.files_list.count()):
                    if filename == self.files_list.item(i).text():
                        exists = True
                        break

                if not exists:
                    self.files_list.addItem(filename)

            self.statusBar().showMessage(f"Added {len(filenames)} files")

    def remove_files(self):
        """Remove selected files from the list"""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            row = self.files_list.row(item)
            self.files_list.takeItem(row)

        self.statusBar().showMessage(f"Removed {len(selected_items)} files")

    def clear_files(self):
        """Clear all files from the list"""
        self.files_list.clear()
        self.statusBar().showMessage("Cleared all files")

    def browse_output(self):
        """Open a directory dialog to select the output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if directory:
            self.output_path.setText(directory)

    def convert_files(self):
        """Convert all the selected DBF files to CSV"""
        # Check if there are files to convert
        if self.files_list.count() == 0:
            QMessageBox.critical(self, "Error", "Please add at least one DBF file")
            return

        output_dir = self.output_path.text()

        # Validate output directory
        if not output_dir:
            QMessageBox.critical(self, "Error", "Please select an output directory")
            return

        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, "Error", "Selected output directory does not exist")
            return

        # Clear previous conversion log
        self.conversion_log.clear()

        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting conversion...")

        # Process files one by one
        self.current_file_index = 0
        self.process_next_file(output_dir)

    def process_next_file(self, output_dir):
        """Process the next file in the queue"""
        if self.current_file_index >= self.files_list.count():
            # All files have been processed
            self.status_label.setText("All conversions completed")
            self.progress_bar.setValue(0)
            QMessageBox.information(self, "Success", "All files have been converted")
            return

        # Get the next file path
        input_path = self.files_list.item(self.current_file_index).text()

        # Create and start a worker thread for this file
        worker = ConversionWorker(input_path, output_dir)

        # Connect signals
        worker.progress_updated.connect(self.update_progress)
        worker.conversion_complete.connect(self.file_conversion_complete)
        worker.conversion_failed.connect(self.file_conversion_failed)

        # Keep a reference to the worker
        self.workers.append(worker)

        # Start conversion
        worker.start()

    def update_progress(self, value, message):
        """Update the progress bar and status message"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def file_conversion_complete(self, output_path):
        """Handle completion of a file conversion"""
        input_path = self.files_list.item(self.current_file_index).text()
        base_name = os.path.basename(input_path)

        # Add to log
        self.conversion_log.addItem(f"✓ Converted: {base_name} → {os.path.basename(output_path)}")
        self.conversion_log.scrollToBottom()

        # Move to next file
        self.current_file_index += 1
        self.process_next_file(self.output_path.text())

    def file_conversion_failed(self, filename, error_message):
        """Handle failure of a file conversion"""
        # Add to log
        self.conversion_log.addItem(f"✗ Failed: {filename} - {error_message}")
        self.conversion_log.scrollToBottom()

        # Move to next file
        self.current_file_index += 1
        self.process_next_file(self.output_path.text())


def main():
    # Check if required packages are installed
    try:
        import dbfread
        from PyQt5.QtWidgets import QApplication
    except ImportError as e:
        missing_package = str(e).split("'")[1]
        print(f"Required package '{missing_package}' is not installed.")
        print(f"Please install it using: pip install {missing_package}")
        return

    app = QApplication(sys.argv)

    app.setApplicationName("DBF to CSV Converter")
    app.setApplicationVersion("1.0.0")

    app.setDesktopFileName("dbf-converter.desktop")

    converter = DBFtoCSVConverter()

    icon_path = "/usr/share/icons/hicolor/128x128/apps/dbf-converter.png"
    app.setWindowIcon(QIcon(icon_path))
    converter.setWindowIcon(QIcon(icon_path))

    converter.setProperty("windowIcon", QIcon(icon_path))

    converter.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()