import sys
import os
from typing import List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QProgressBar, QCheckBox, QFileDialog,
    QGroupBox, QMessageBox, QSlider, QSpinBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor

from file_scanner import FileScanner, FileInfo
from deduplication_engine import DeduplicationEngine, DuplicateGroup
from ui_results_view import ResultsView
from logger import get_logger
import ui_styles
import json

logger = get_logger()

class ScanThread(QThread):
    """Background thread for scanning files."""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list, list)
    error = pyqtSignal(str)
    
    def __init__(self, root_paths: List[str], use_perceptual: bool, parent=None):
        super().__init__(parent)
        self.root_paths = root_paths
        self.use_perceptual = use_perceptual
    
    def run(self):
        try:
            scanner = FileScanner()
            files = scanner.scan_directories(
                self.root_paths,
                progress_callback=lambda count, path: self.progress.emit(count, path)
            )
            if not files:
                self.error.emit("No image files found in selected directories.")
                return
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
    """Main application window overhauled with modern dark theme."""
    
    def __init__(self):
        super().__init__()
        self.selected_folders = []
        self.scan_thread = None
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        self.setWindowTitle("Duplicate File Finder")
        self.setMinimumSize(1000, 750)
        self.setStyleSheet(ui_styles.GLOBAL_STYLES)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Duplicate File Finder")
        title_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {ui_styles.COLORS['primary']};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Content Splitter (Manual Layout)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left Panel: Folders
        left_panel = QFrame()
        left_panel.setStyleSheet(f"background-color: {ui_styles.COLORS['card_bg']}; border-radius: 12px; border: 1px solid {ui_styles.COLORS['border']};")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        left_layout.addWidget(QLabel("<b>SCAN DIRECTORIES</b>"))
        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet(f"background-color: {ui_styles.COLORS['bg']}; border: none; border-radius: 8px; padding: 10px; color: {ui_styles.COLORS['text']};")
        left_layout.addWidget(self.folder_list)
        
        btn_h = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Folder")
        self.add_btn.setStyleSheet(f"background-color: {ui_styles.COLORS['primary']}; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_folder)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setStyleSheet(f"background-color: transparent; color: {ui_styles.COLORS['text_dim']}; padding: 12px; border: 1px solid {ui_styles.COLORS['border']}; border-radius: 8px;")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_folders)
        
        btn_h.addWidget(self.add_btn)
        btn_h.addWidget(self.clear_btn)
        left_layout.addLayout(btn_h)
        
        # Right Panel: Options
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {ui_styles.COLORS['card_bg']}; border-radius: 12px; border: 1px solid {ui_styles.COLORS['border']};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        right_layout.addWidget(QLabel("<b>SCAN OPTIONS</b>"))
        
        self.hidden_folders_checkbox = QCheckBox("Search Hidden Folders")
        right_layout.addWidget(self.hidden_folders_checkbox)
        
        self.perceptual_checkbox = QCheckBox("Find Similar (Visually)")
        self.perceptual_checkbox.toggled.connect(self.on_perceptual_toggled)
        right_layout.addWidget(self.perceptual_checkbox)
        
        right_layout.addSpacing(20)
        right_layout.addWidget(QLabel("Similarity Strictness:"))
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(10)
        self.threshold_slider.setValue(5)
        self.threshold_slider.setEnabled(False)
        self.threshold_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height: 6px; background: {ui_styles.COLORS['border']}; border-radius: 3px; }}
            QSlider::handle:horizontal {{ background: {ui_styles.COLORS['primary']}; width: 18px; height: 18px; margin: -6px 0; border-radius: 9px; }}
        """)
        right_layout.addWidget(self.threshold_slider)
        
        right_layout.addStretch()
        
        self.load_recent_btn = QPushButton("📁 Load Previous Results")
        self.load_recent_btn.setStyleSheet(f"background-color: transparent; color: {ui_styles.COLORS['text']}; padding: 14px; border: 1px solid {ui_styles.COLORS['border']}; border-radius: 10px;")
        self.load_recent_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_recent_btn.clicked.connect(self.load_previous_results)
        right_layout.addWidget(self.load_recent_btn)
        
        content_layout.addWidget(left_panel, 2)
        content_layout.addWidget(right_panel, 1)
        main_layout.addLayout(content_layout)
        
        # Progress & Action Area
        self.progress_area = QWidget()
        self.progress_area.setVisible(False)
        p_layout = QVBoxLayout(self.progress_area)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f"QProgressBar {{ background: {ui_styles.COLORS['border']}; border-radius: 4px; }} QProgressBar::chunk {{ background: {ui_styles.COLORS['primary']}; border-radius: 4px; }}")
        self.progress_bar.setTextVisible(False)
        self.status_label = QLabel("Ready...")
        p_layout.addWidget(self.status_label)
        p_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_area)
        
        self.scan_btn = QPushButton("START SCAN")
        self.scan_btn.setFixedHeight(65)
        self.scan_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ui_styles.COLORS['primary']};
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 12px;
            }}
            QPushButton:hover {{ background-color: {ui_styles.COLORS['primary_hover']}; }}
            QPushButton:disabled {{ background-color: #333; color: #666; }}
        """)
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_btn.clicked.connect(self.start_scan)
        main_layout.addWidget(self.scan_btn)

    def on_perceptual_toggled(self, checked):
        self.threshold_slider.setEnabled(checked)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.folder_list.addItem(folder)

    def clear_folders(self):
        self.folder_list.clear()
        self.selected_folders.clear()

    def start_scan(self):
        if not self.selected_folders:
            QMessageBox.warning(self, "No Folders", "Please select folders to scan.")
            return
        
        self.progress_area.setVisible(True)
        self.scan_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting scan...")
        
        self.scan_thread = ScanThread(self.selected_folders, self.perceptual_checkbox.isChecked())
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.start()

    def on_scan_progress(self, count, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(count % 100)

    def on_scan_finished(self, files, groups):
        self.scan_btn.setEnabled(True)
        self.progress_area.setVisible(False)
        if not groups:
            QMessageBox.information(self, "No Duplicates", f"Scanned {len(files)} files. No duplicates found.")
            return
        self.open_results_view(groups)

    def on_scan_error(self, error):
        self.scan_btn.setEnabled(True)
        self.progress_area.setVisible(False)
        QMessageBox.critical(self, "Error", f"An error occurred: {error}")

    def open_results_view(self, groups):
        self.results_window = ResultsView(groups, self)
        self.results_window.show()

    def load_previous_results(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Results", "", "JSON (*.json)")
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            groups = []
            for g_data in data['groups']:
                files = []
                for f_data in g_data['files']:
                    # Filter only fields that the FileInfo constructor expects
                    valid_keys = {'path', 'size', 'extension', 'resolution', 'created_time', 'modified_time'}
                    filtered_data = {k: v for k, v in f_data.items() if k in valid_keys}
                    
                    # Ensure resolution is a tuple as expected by FileInfo dataclass
                    if filtered_data.get('resolution'):
                        filtered_data['resolution'] = tuple(filtered_data['resolution'])
                        
                    files.append(FileInfo(**filtered_data))
                groups.append(DuplicateGroup(files=files, detection_method=g_data['detection_method']))
            self.open_results_view(groups)
        except Exception as e:
            logger.error(f"Failed to load results: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load: {e}")

    def load_config(self):
        """Load configuration/set defaults."""
        try:
            if os.path.exists("config.json"):
                with open("config.json", 'r') as f:
                    config = json.load(f)
                self.hidden_folders_checkbox.setChecked(config.get('scan_options', {}).get('include_hidden_folders', False))
                self.perceptual_checkbox.setChecked(config.get('perceptual_hash', {}).get('enabled', False))
                self.threshold_slider.setValue(config.get('perceptual_hash', {}).get('similarity_threshold', 5))
        except Exception as e:
            logger.warning(f"Config load error: {e}")
