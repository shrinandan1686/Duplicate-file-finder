"""
Main Window for Duplicate File Finder.
Provides the primary user interface for folder selection and scanning.
"""

import sys
import os
from typing import List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QProgressBar, QCheckBox, QFileDialog,
    QGroupBox, QMessageBox, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from file_scanner import FileScanner, FileInfo
from deduplication_engine import DeduplicationEngine, DuplicateGroup
from ui_results_view import ResultsView
from logger import get_logger
import json

logger = get_logger()


class ScanThread(QThread):
    """Background thread for scanning files."""
    
    progress = pyqtSignal(int, str)  # files_scanned, current_path
    finished = pyqtSignal(list, list)  # files, duplicate_groups
    error = pyqtSignal(str)
    
    def __init__(self, root_paths: List[str], use_perceptual: bool, parent=None):
        super().__init__(parent)
        self.root_paths = root_paths
        self.use_perceptual = use_perceptual
    
    def run(self):
        """Run the scanning and deduplication process."""
        try:
            # Step 1: Scan files
            scanner = FileScanner()
            files = scanner.scan_directories(
                self.root_paths,
                progress_callback=lambda count, path: self.progress.emit(count, path)
            )
            
            if not files:
                self.error.emit("No image files found in selected directories.")
                return
            
            # Step 2: Find duplicates
            engine = DeduplicationEngine()
            duplicate_groups = engine.find_duplicates(
                files,
                use_perceptual=self.use_perceptual,
                progress_callback=lambda current, total: self.progress.emit(current, f"Analyzing {current}/{total}")
            )
            
            self.finished.emit(files, duplicate_groups)
        
        except Exception as e:
            logger.error(f"Error during scan: {e}", exc_info=True)
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.selected_folders = []
        self.scan_thread = None
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate File Finder")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Duplicate File Finder")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Folder selection group
        folder_group = self.create_folder_selection_group()
        layout.addWidget(folder_group)
        
        # Options group
        options_group = self.create_options_group()
        layout.addWidget(options_group)
        
        # Progress group
        self.progress_group = self.create_progress_group()
        self.progress_group.setVisible(False)
        layout.addWidget(self.progress_group)
        
        # Scan button
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setMinimumHeight(40)
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)
        
        # Stretch to push everything to top
        layout.addStretch()
    
    def create_folder_selection_group(self) -> QGroupBox:
        """Create the folder selection group box."""
        group = QGroupBox("Select Folders to Scan")
        layout = QVBoxLayout()
        
        # Folder list
        self.folder_list = QListWidget()
        self.folder_list.setMinimumHeight(150)
        layout.addWidget(self.folder_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(add_folder_btn)
        
        remove_folder_btn = QPushButton("Remove Selected")
        remove_folder_btn.clicked.connect(self.remove_folder)
        button_layout.addWidget(remove_folder_btn)
        
        clear_folders_btn = QPushButton("Clear All")
        clear_folders_btn.clicked.connect(self.clear_folders)
        button_layout.addWidget(clear_folders_btn)
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def create_options_group(self) -> QGroupBox:
        """Create the options group box."""
        group = QGroupBox("Scan Options")
        layout = QVBoxLayout()
        
        # Include hidden folders checkbox
        self.hidden_folders_checkbox = QCheckBox("Include hidden/system folders")
        layout.addWidget(self.hidden_folders_checkbox)
        
        # Perceptual hashing checkbox
        self.perceptual_checkbox = QCheckBox("Enable perceptual hashing (find similar images)")
        self.perceptual_checkbox.toggled.connect(self.on_perceptual_toggled)
        layout.addWidget(self.perceptual_checkbox)
        
        # Similarity threshold (only visible when perceptual is enabled)
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Similarity threshold:"))
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(10)
        self.threshold_slider.setValue(5)
        self.threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.threshold_slider.setTickInterval(1)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        self.threshold_slider.setEnabled(False)
        threshold_layout.addWidget(self.threshold_slider)
        
        self.threshold_label = QLabel("5")
        self.threshold_label.setMinimumWidth(30)
        threshold_layout.addWidget(self.threshold_label)
        
        layout.addLayout(threshold_layout)
        
        help_label = QLabel("Note: Lower threshold = more strict matching")
        help_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(help_label)
        
        group.setLayout(layout)
        return group
    
    def create_progress_group(self) -> QGroupBox:
        """Create the progress group box."""
        group = QGroupBox("Scan Progress")
        layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to scan...")
        layout.addWidget(self.status_label)
        
        # Files scanned counter
        self.files_label = QLabel("Files scanned: 0")
        layout.addWidget(self.files_label)
        
        group.setLayout(layout)
        return group
    
    def load_config(self):
        """Load configuration and set default values."""
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            
            # Set default options
            scan_options = config.get('scan_options', {})
            self.hidden_folders_checkbox.setChecked(
                scan_options.get('include_hidden_folders', False)
            )
            
            perceptual = config.get('perceptual_hash', {})
            self.perceptual_checkbox.setChecked(
                perceptual.get('enabled', False)
            )
            threshold = perceptual.get('similarity_threshold', 5)
            self.threshold_slider.setValue(threshold)
            self.threshold_label.setText(str(threshold))
        
        except Exception as e:
            logger.warning(f"Unable to load config: {e}")
    
    def on_perceptual_toggled(self, checked: bool):
        """Handle perceptual checkbox toggle."""
        self.threshold_slider.setEnabled(checked)
    
    def on_threshold_changed(self, value: int):
        """Handle threshold slider change."""
        self.threshold_label.setText(str(value))
    
    def add_folder(self):
        """Open folder dialog and add selected folder."""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Folder to Scan",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.folder_list.addItem(folder)
    
    def remove_folder(self):
        """Remove selected folder from list."""
        current_row = self.folder_list.currentRow()
        if current_row >= 0:
            self.folder_list.takeItem(current_row)
            del self.selected_folders[current_row]
    
    def clear_folders(self):
        """Clear all folders from list."""
        self.folder_list.clear()
        self.selected_folders.clear()
    
    def start_scan(self):
        """Start the scanning process."""
        if not self.selected_folders:
            QMessageBox.warning(
                self,
                "No Folders Selected",
                "Please select at least one folder to scan."
            )
            return
        
        # Update config with current options
        self.update_config()
        
        # Show progress group
        self.progress_group.setVisible(True)
        self.scan_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting scan...")
        
        # Start scan thread
        self.scan_thread = ScanThread(
            self.selected_folders,
            self.perceptual_checkbox.isChecked()
        )
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.start()
    
    def update_config(self):
        """Update config file with current options."""
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            
            config['scan_options']['include_hidden_folders'] = self.hidden_folders_checkbox.isChecked()
            config['perceptual_hash']['enabled'] = self.perceptual_checkbox.isChecked()
            config['perceptual_hash']['similarity_threshold'] = self.threshold_slider.value()
            
            with open("config.json", 'w') as f:
                json.dump(config, f, indent=2)
        
        except Exception as e:
            logger.warning(f"Unable to update config: {e}")
    
    def on_scan_progress(self, count: int, message: str):
        """Handle scan progress updates."""
        self.files_label.setText(f"Files processed: {count}")
        self.status_label.setText(message)
        # Pulse progress bar during scan
        self.progress_bar.setValue((count % 100))
    
    def on_scan_finished(self, files: List[FileInfo], duplicate_groups: List[DuplicateGroup]):
        """Handle scan completion."""
        self.scan_button.setEnabled(True)
        self.progress_bar.setValue(100)
        
        if not duplicate_groups:
            QMessageBox.information(
                self,
                "No Duplicates Found",
                f"Scanned {len(files)} files.\n\nNo duplicate files were found."
            )
            self.progress_group.setVisible(False)
            return
        
        # Calculate statistics
        total_duplicates = sum(len(group.files) for group in duplicate_groups)
        total_wasted = sum(group.get_total_wasted_space() for group in duplicate_groups)
        from utils import format_bytes
        
        self.status_label.setText(
            f"Found {len(duplicate_groups)} duplicate groups "
            f"({total_duplicates} files, {format_bytes(total_wasted)} wasted)"
        )
        
        # Open results view
        self.open_results_view(duplicate_groups)
    
    def on_scan_error(self, error_message: str):
        """Handle scan errors."""
        self.scan_button.setEnabled(True)
        self.progress_group.setVisible(False)
        
        QMessageBox.critical(
            self,
            "Scan Error",
            f"An error occurred during scanning:\n\n{error_message}"
        )
    
    def open_results_view(self, duplicate_groups: List[DuplicateGroup]):
        """Open the results view window."""
        results_window = ResultsView(duplicate_groups, self)
        results_window.show()
