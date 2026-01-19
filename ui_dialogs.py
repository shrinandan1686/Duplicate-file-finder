"""
Dialog windows for Duplicate File Finder.
Includes confirmation dialogs and other UI dialogs.
"""

from typing import List, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QTextEdit, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from file_scanner import FileInfo
from deletion_manager import DeletionMethod
from utils import format_bytes


class DeletionConfirmationDialog(QDialog):
    """Dialog to confirm file deletion with safety checks."""
    
    def __init__(self, files: List[FileInfo], parent=None):
        super().__init__(parent)
        self.files = files
        self.confirmed = False
        self.selected_method = DeletionMethod.RECYCLE_BIN
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Confirm Deletion")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Warning label
        warning_label = QLabel("⚠️ You are about to delete files")
        warning_font = QFont()
        warning_font.setPointSize(14)
        warning_font.setBold(True)
        warning_label.setFont(warning_font)
        warning_label.setStyleSheet("color: #f44336;")
        layout.addWidget(warning_label)
        
        # Summary
        total_size = sum(f.size for f in self.files)
        summary_label = QLabel(
            f"<b>Files to delete:</b> {len(self.files)}<br>"
            f"<b>Total size:</b> {format_bytes(total_size)}"
        )
        layout.addWidget(summary_label)
        
        # File list
        list_label = QLabel("Files:")
        layout.addWidget(list_label)
        
        file_list = QTextEdit()
        file_list.setReadOnly(True)
        file_list.setMaximumHeight(200)
        file_text = "\n".join(f.path for f in self.files[:50])  # Limit to 50
        if len(self.files) > 50:
            file_text += f"\n... and {len(self.files) - 50} more files"
        file_list.setPlainText(file_text)
        layout.addWidget(file_list)
        
        # Deletion method selection
        method_label = QLabel("Deletion method:")
        method_font = QFont()
        method_font.setBold(True)
        method_label.setFont(method_font)
        layout.addWidget(method_label)
        
        self.method_group = QButtonGroup()
        
        self.recycle_radio = QRadioButton("Move to Recycle Bin (Recommended - Reversible)")
        self.recycle_radio.setChecked(True)
        self.method_group.addButton(self.recycle_radio)
        layout.addWidget(self.recycle_radio)
        
        self.hard_delete_radio = QRadioButton("Permanent Delete (WARNING - Cannot be undone!)")
        self.hard_delete_radio.toggled.connect(self.on_hard_delete_toggled)
        self.method_group.addButton(self.hard_delete_radio)
        layout.addWidget(self.hard_delete_radio)
        
        # Hard delete confirmation
        self.confirmation_widget = QWidget()
        confirmation_layout = QVBoxLayout(self.confirmation_widget)
        confirmation_layout.setContentsMargins(20, 0, 0, 0)
        
        confirm_label = QLabel('To confirm permanent deletion, type "DELETE" below:')
        confirm_label.setStyleSheet("color: #f44336; font-weight: bold;")
        confirmation_layout.addWidget(confirm_label)
        
        self.confirmation_input = QLineEdit()
        self.confirmation_input.setPlaceholderText("Type DELETE here")
        confirmation_layout.addWidget(self.confirmation_input)
        
        self.confirmation_widget.setVisible(False)
        layout.addWidget(self.confirmation_widget)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        self.confirm_btn = QPushButton("Confirm Deletion")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.confirm_btn.clicked.connect(self.on_confirm)
        button_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_hard_delete_toggled(self, checked: bool):
        """Handle hard delete radio button toggle."""
        self.confirmation_widget.setVisible(checked)
        if not checked:
            self.confirmation_input.clear()
    
    def on_confirm(self):
        """Handle confirm button click."""
        # Determine selected method
        if self.recycle_radio.isChecked():
            self.selected_method = DeletionMethod.RECYCLE_BIN
            self.confirmed = True
            self.accept()
        
        elif self.hard_delete_radio.isChecked():
            # Check confirmation text
            if self.confirmation_input.text().strip() == "DELETE":
                self.selected_method = DeletionMethod.HARD_DELETE
                self.confirmed = True
                
                # Extra confirmation for hard delete
                reply = QMessageBox.question(
                    self,
                    "Final Confirmation",
                    "Are you absolutely sure you want to PERMANENTLY delete these files?\n\n"
                    "This action CANNOT be undone!",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.accept()
                else:
                    self.confirmed = False
            else:
                QMessageBox.warning(
                    self,
                    "Confirmation Required",
                    'Please type "DELETE" exactly to confirm permanent deletion.'
                )
    
    def get_result(self) -> Tuple[DeletionMethod, bool]:
        """
        Get the dialog result.
        
        Returns:
            Tuple of (deletion_method, confirmed)
        """
        return (self.selected_method, self.confirmed)


class AboutDialog(QDialog):
    """About dialog showing application information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("About Duplicate File Finder")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Duplicate File Finder")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        layout.addSpacing(20)
        
        # Description
        description = QLabel(
            "A safe and user-friendly tool to detect and manage duplicate image files.\n\n"
            "Features:\n"
            "• Multi-stage deduplication (size → hash → perceptual)\n"
            "• Safe deletion with Recycle Bin support\n"
            "• Intelligent suggestions for which files to keep\n"
            "• Comprehensive logging and error handling\n\n"
            "Built with Python and PyQt6"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
