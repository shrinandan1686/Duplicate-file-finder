"""
Results View for Duplicate File Finder.
Displays duplicate groups and allows user to select files for deletion.
"""

import os
from typing import List, Dict
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QGroupBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon

from deduplication_engine import DuplicateGroup
from file_scanner import FileInfo
from deletion_manager import DeletionManager, DeletionMethod
from suggestion_engine import SuggestionEngine
from ui_dialogs import DeletionConfirmationDialog
from utils import format_bytes, generate_thumbnail
from logger import get_logger
import json

logger = get_logger()


class DuplicateGroupWidget(QGroupBox):
    """Widget to display a single duplicate group."""
    
    def __init__(self, group: DuplicateGroup, group_number: int, strategy: str, parent=None):
        super().__init__(parent)
        self.group = group
        self.group_number = group_number
        self.strategy = strategy
        self.checkboxes: Dict[str, QCheckBox] = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI for this group."""
        # Get suggestion
        suggestion_engine = SuggestionEngine()
        keeper, reason = suggestion_engine.suggest_keeper(self.group.files, self.strategy)
        
        # Group title - clearer formatting
        wasted = format_bytes(self.group.get_total_wasted_space())
        group_title = (
            f"Group {self.group_number}: {len(self.group.files)} duplicates  •  "
            f"💾 {wasted} can be freed"
        )
        self.setTitle(group_title)
        
        # Style the group box
        self.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # CLEANER TABLE: Only essential columns
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "✓", "Preview", "Full Path", "Size", "Keep?"
        ])
        table.setRowCount(len(self.group.files))
        
        # Configure table for better visibility
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        
        # Style the table
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                gridline-color: #404040;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #555;
            }
        """)
        
        # Populate table with clearer layout
        for i, file_info in enumerate(self.group.files):
            is_suggested = (file_info.path == keeper.path)
            
            # Checkbox - for deletion selection
            checkbox = QCheckBox()
            if not is_suggested:
                checkbox.setChecked(True)  # Pre-select for deletion (NOT the keeper)
            checkbox.setToolTip("Check to delete this file")
            self.checkboxes[file_info.path] = checkbox
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            table.setCellWidget(i, 0, checkbox_widget)
            
            # Larger thumbnail for better visibility
            thumbnail_label = QLabel()
            thumbnail_path = generate_thumbnail(file_info.path)
            if thumbnail_path and os.path.exists(thumbnail_path):
                pixmap = QPixmap(thumbnail_path)
                scaled_pixmap = pixmap.scaled(
                    120, 120,  # Larger thumbnail
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                thumbnail_label.setPixmap(scaled_pixmap)
            else:
                thumbnail_label.setText("No\nPreview")
                thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setCellWidget(i, 1, thumbnail_label)
            
            # FULL PATH - This is what user wants to see!
            path_item = QTableWidgetItem(file_info.path)
            path_item.setToolTip(f"Click to copy path\n{file_info.path}")
            
            # Color code the suggested keeper
            if is_suggested:
                path_item.setBackground(Qt.GlobalColor.darkGreen)
                path_item.setForeground(Qt.GlobalColor.white)
            
            table.setItem(i, 2, path_item)
            
            # Size
            size_item = QTableWidgetItem(format_bytes(file_info.size))
            if is_suggested:
                size_item.setBackground(Qt.GlobalColor.darkGreen)
                size_item.setForeground(Qt.GlobalColor.white)
            table.setItem(i, 3, size_item)
            
            # Clear "Keep" indicator with reasoning
            if is_suggested:
                keep_text = f"⭐ KEEP\n{reason}"
                keep_item = QTableWidgetItem(keep_text)
                keep_item.setFont(QFont("", -1, QFont.Weight.Bold))
                keep_item.setBackground(Qt.GlobalColor.darkGreen)
                keep_item.setForeground(Qt.GlobalColor.white)
                keep_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                keep_item = QTableWidgetItem("Delete")
                keep_item.setForeground(Qt.GlobalColor.lightGray)
                keep_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 4, keep_item)
        
        # Resize columns for better visibility
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Checkbox
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Thumbnail
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Path (takes most space)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Size
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Keep?
        
        # Taller rows for better thumbnail visibility
        for i in range(len(self.group.files)):
            table.setRowHeight(i, 130)
        
        layout.addWidget(table)
        
        # SIMPLIFIED BUTTONS - Single row, clearer labels
        button_layout = QHBoxLayout()
        
        # Info label
        info_label = QLabel(f"💡 Green row = Suggested file to KEEP")
        info_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11px;")
        button_layout.addWidget(info_label)
        
        button_layout.addStretch()
        
        # Quick actions
        keep_suggested_btn = QPushButton("✓ Keep Only Suggested")
        keep_suggested_btn.setToolTip("Select all files EXCEPT the suggested keeper for deletion")
        keep_suggested_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        keep_suggested_btn.clicked.connect(lambda: self.select_except_suggested(keeper.path))
        button_layout.addWidget(keep_suggested_btn)
        
        clear_btn = QPushButton("Clear Selection")
        clear_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def select_except_suggested(self, keeper_path: str):
        """Select all files except the suggested keeper."""
        for path, checkbox in self.checkboxes.items():
            checkbox.setChecked(path != keeper_path)
    
    def select_all(self):
        """Select all files in this group."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all(self):
        """Deselect all files in this group."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_files(self) -> List[FileInfo]:
        """Get list of selected files."""
        selected = []
        for file_info in self.group.files:
            if self.checkboxes[file_info.path].isChecked():
                selected.append(file_info)
        return selected


class ResultsView(QMainWindow):
    """Results view window displaying duplicate groups."""
    
    def __init__(self, duplicate_groups: List[DuplicateGroup], parent=None):
        super().__init__(parent)
        self.duplicate_groups = duplicate_groups
        self.group_widgets: List[DuplicateGroupWidget] = []
        self.strategy = 'keep_highest_resolution'
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Duplicate Files Found")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"Found {len(self.duplicate_groups)} Duplicate Groups")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Strategy selector
        header_layout.addWidget(QLabel("Suggestion strategy:"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Keep Highest Resolution",
            "Keep Oldest",
            "Keep Newest",
            "Keep Shortest Path"
        ])
        self.strategy_combo.currentTextChanged.connect(self.on_strategy_changed)
        header_layout.addWidget(self.strategy_combo)
        
        layout.addLayout(header_layout)
        
        # Scroll area for groups
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Create group widgets
        self.create_group_widgets(scroll_layout)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Bottom panel
        bottom_layout = QHBoxLayout()
        
        # Summary label
        self.summary_label = QLabel()
        self.update_summary()
        bottom_layout.addWidget(self.summary_label)
        
        bottom_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        bottom_layout.addWidget(export_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete Selected Files")
        delete_btn.setMinimumHeight(40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected)
        bottom_layout.addWidget(delete_btn)
        
        layout.addLayout(bottom_layout)
    
    def create_group_widgets(self, layout: QVBoxLayout):
        """Create widgets for all duplicate groups."""
        self.group_widgets.clear()
        
        for i, group in enumerate(self.duplicate_groups, 1):
            group_widget = DuplicateGroupWidget(group, i, self.strategy)
            self.group_widgets.append(group_widget)
            layout.addWidget(group_widget)
    
    def on_strategy_changed(self, text: str):
        """Handle strategy change."""
        strategy_map = {
            "Keep Highest Resolution": "keep_highest_resolution",
            "Keep Oldest": "keep_oldest",
            "Keep Newest": "keep_newest",
            "Keep Shortest Path": "keep_shortest_path"
        }
        
        self.strategy = strategy_map.get(text, "keep_highest_resolution")
        
        # Recreate group widgets with new strategy
        # Remove old widgets
        scroll_area = self.centralWidget().layout().itemAt(1).widget()
        scroll_widget = scroll_area.widget()
        layout = scroll_widget.layout()
        
        # Clear layout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Recreate widgets
        self.create_group_widgets(layout)
        layout.addStretch()
    
    def update_summary(self):
        """Update the summary label."""
        selected_files = []
        total_size = 0
        
        for group_widget in self.group_widgets:
            selected = group_widget.get_selected_files()
            selected_files.extend(selected)
            total_size += sum(f.size for f in selected)
        
        self.summary_label.setText(
            f"<b>{len(selected_files)} files selected</b> - "
            f"<b>{format_bytes(total_size)}</b> to free"
        )
    
    def delete_selected(self):
        """Delete selected files."""
        # Update summary
        self.update_summary()
        
        # Get all selected files
        selected_files = []
        for group_widget in self.group_widgets:
            selected_files.extend(group_widget.get_selected_files())
        
        if not selected_files:
            QMessageBox.warning(
                self,
                "No Files Selected",
                "Please select files to delete."
            )
            return
        
        # Show confirmation dialog
        dialog = DeletionConfirmationDialog(selected_files, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            method, confirmed = dialog.get_result()
            
            if not confirmed:
                return
            
            # Perform deletion
            self.perform_deletion(selected_files, method)
    
    def perform_deletion(self, files: List[FileInfo], method: DeletionMethod):
        """Perform the actual deletion."""
        manager = DeletionManager()
        
        # Prepare file paths with sizes
        files_with_sizes = [(f.path, f.size) for f in files]
        
        # Delete files
        report = manager.delete_files_with_sizes(files_with_sizes, method)
        
        # Show results
        if report.successful_deletions == report.total_files:
            QMessageBox.information(
                self,
                "Deletion Successful",
                f"Successfully deleted {report.successful_deletions} files.\n\n"
                f"Space freed: {format_bytes(report.total_space_freed)}\n\n"
                f"Deletion log saved to:\n{report.log_file_path}"
            )
            self.close()
        else:
            QMessageBox.warning(
                self,
                "Deletion Completed with Errors",
                f"Deleted: {report.successful_deletions}/{report.total_files} files\n"
                f"Failed: {report.failed_deletions} files\n\n"
                f"Space freed: {format_bytes(report.total_space_freed)}\n\n"
                f"Check log for details:\n{report.log_file_path}"
            )
    
    def export_results(self):
        """Export results to JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "duplicate_results.json",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            data = {
                'total_groups': len(self.duplicate_groups),
                'groups': [group.to_dict() for group in self.duplicate_groups]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Results exported to:\n{file_path}"
            )
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export results:\n{str(e)}"
            )
