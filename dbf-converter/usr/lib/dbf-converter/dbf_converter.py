#!/usr/bin/env python3
import os
import csv
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar,
                             QMessageBox, QGroupBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from dbfread import DBF


class DBFtoCSVConverter(QMainWindow):
    def __init__(self):
        # Call the parent class initializer
        super(DBFtoCSVConverter, self).__init__()

        # Configure the main window
        self.setWindowTitle("DBF to CSV Converter")
        self.setMinimumSize(650, 400)

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
        input_group = QGroupBox("Select DBF File")
        input_layout = QHBoxLayout(input_group)

        self.input_path = QLineEdit()
        input_layout.addWidget(self.input_path)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_input)
        input_layout.addWidget(browse_button)

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

        main_layout.addWidget(progress_group)

        # Convert button
        convert_button = QPushButton("Convert")
        convert_button.setMinimumHeight(40)
        convert_button.clicked.connect(self.convert_file)
        main_layout.addWidget(convert_button)

        # Status bar
        self.statusBar().showMessage("Ready to convert DBF files to CSV")

    def browse_input(self):
        """Open a file dialog to select the input DBF file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select DBF File", "", "DBF Files (*.dbf);;All Files (*.*)"
        )
        if filename:
            self.input_path.setText(filename)

    def browse_output(self):
        """Open a directory dialog to select the output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if directory:
            self.output_path.setText(directory)

    def convert_file(self):
        """Convert the selected DBF file to CSV"""
        input_path = self.input_path.text()
        output_dir = self.output_path.text()

        # Validate input and output paths
        if not input_path:
            QMessageBox.critical(self, "Error", "Please select a DBF file")
            return

        if not output_dir:
            QMessageBox.critical(self, "Error", "Please select an output directory")
            return

        if not os.path.isfile(input_path):
            QMessageBox.critical(self, "Error", "Selected input file does not exist")
            return

        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, "Error", "Selected output directory does not exist")
            return

        try:
            # Get the base filename without extension
            base_name = os.path.basename(input_path)
            file_name_without_ext = os.path.splitext(base_name)[0]
            output_path = os.path.join(output_dir, f"{file_name_without_ext}.csv")

            # Update status
            self.status_label.setText(f"Reading DBF file: {base_name}")
            self.statusBar().showMessage(f"Processing {base_name}")
            QApplication.processEvents()

            # Read the DBF file
            dbf = DBF(input_path)

            # Get total number of records for progress tracking
            total_records = len(dbf)

            # Update status
            self.status_label.setText(f"Converting {total_records} records to CSV")
            QApplication.processEvents()

            # Write to CSV file
            with open(output_path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)

                # Write header
                writer.writerow(dbf.field_names)

                # Write records with progress update
                for i, record in enumerate(dbf):
                    writer.writerow([record[field] for field in dbf.field_names])

                    # Update progress bar
                    progress_value = int((i + 1) / total_records * 100)
                    self.progress_bar.setValue(progress_value)
                    self.status_label.setText(f"Converting: {progress_value}% complete")

                    # Update the GUI every 100 records to avoid freezing
                    if i % 100 == 0:
                        QApplication.processEvents()

            # Reset progress and update status
            self.progress_bar.setValue(0)
            self.status_label.setText(f"Conversion completed successfully")
            self.statusBar().showMessage(f"File converted to: {output_path}")

            # Show success message
            QMessageBox.information(self, "Success", f"File converted successfully to:\n{output_path}")

        except Exception as e:
            self.status_label.setText("Error during conversion")
            QMessageBox.critical(self, "Error", f"An error occurred during conversion:\n{str(e)}")
            self.statusBar().showMessage("Conversion failed")


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
    converter = DBFtoCSVConverter()
    converter.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()