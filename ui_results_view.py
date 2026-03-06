import os
import json
from enum import Enum
from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QCheckBox, QMessageBox, QFileDialog, 
    QComboBox, QSplitter, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, QThreadPool, QRunnable, QObject, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QPalette

from deduplication_engine import DuplicateGroup
from file_scanner import FileInfo
from deletion_manager import DeletionManager, DeletionMethod
from suggestion_engine import SuggestionEngine
from ui_dialogs import DeletionConfirmationDialog
from utils import format_bytes, generate_thumbnail
from logger import get_logger
import ui_styles

logger = get_logger()

class ThumbnailSignals(QObject):
    finished = pyqtSignal(str)

class ThumbnailWorker(QRunnable):
    """Worker for background thumbnail generation."""
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.signals = ThumbnailSignals()

    def run(self):
        try:
            thumb_path = generate_thumbnail(self.file_path)
            if thumb_path:
                self.signals.finished.emit(thumb_path)
        except Exception as e:
            logger.error(f"Thumbnail error: {e}")

class CardState(Enum):
    NEUTRAL = "neutral"
    RECOMMENDED = "recommended"
    DELETE = "delete"

class ImageCard(QFrame):
    """Modern image card with async thumbnail and metadata."""
    clicked = pyqtSignal(FileInfo)
    stateChanged = pyqtSignal(FileInfo, CardState)

    def __init__(self, file_info: FileInfo, is_recommended: bool, reason: str = "", parent=None):
        super().__init__(parent)
        self.file_info = file_info
        self.is_recommended = is_recommended
        self.reason = reason
        self.state = CardState.RECOMMENDED if is_recommended else CardState.DELETE
        self.setObjectName("ImageCard")
        self.setProperty("state", self.state.value)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.init_ui()
        self.start_loading_thumbnail()

    def init_ui(self):
        self.setFixedSize(180, 260)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Thumbnail Placeholder
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setObjectName("Thumbnail")
        self.thumbnail_label.setFixedSize(164, 140)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setText("Loading...")
        
        # Opacity Effect for Fade-in
        self.opacity_effect = QGraphicsOpacityEffect(self.thumbnail_label)
        self.opacity_effect.setOpacity(0)
        self.thumbnail_label.setGraphicsEffect(self.opacity_effect)
        
        layout.addWidget(self.thumbnail_label)

        # Badge (Original/Copy)
        self.badge = QLabel("ORIGINAL" if self.is_recommended else "COPY")
        self.badge.setObjectName("Badge" if self.is_recommended else "BadgeCopy")
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.badge)
        
        self.reason_label = QLabel(self.reason if self.is_recommended else "")
        self.reason_label.setObjectName("MetadataLabel")
        self.reason_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.reason_label)

        # Metadata
        name_label = QLabel(os.path.basename(self.file_info.path))
        name_label.setObjectName("FileNameLabel")
        name_label.setToolTip(self.file_info.path)
        layout.addWidget(name_label)

        res = self.file_info.resolution
        res_str = f"{res[0]}x{res[1]}" if res else "Unknown"
        meta_str = f"{res_str} • {format_bytes(self.file_info.size)}"
        meta_label = QLabel(meta_str)
        meta_label.setObjectName("MetadataLabel")
        layout.addWidget(meta_label)

        path_label = QLabel(os.path.dirname(self.file_info.path))
        path_label.setObjectName("MetadataLabel")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)

        self.setStyleSheet(ui_styles.IMAGE_CARD_STYLE)
        self.update_state_ui()

    def start_loading_thumbnail(self):
        worker = ThumbnailWorker(self.file_info.path)
        worker.signals.finished.connect(self.on_thumbnail_ready)
        QThreadPool.globalInstance().start(worker)

    def on_thumbnail_ready(self, path: str):
        if os.path.exists(path):
            pix = QPixmap(path)
            self.thumbnail_label.setPixmap(pix.scaled(
                160, 136, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
            
            # Fade-in Animation
            self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_anim.setDuration(400)
            self.fade_anim.setStartValue(0)
            self.fade_anim.setEndValue(1)
            self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.fade_anim.start()
        else:
            self.thumbnail_label.setText("No Preview")
            self.opacity_effect.setOpacity(1)

    def enterEvent(self, event):
        # Scale up slightly on hover
        self.anim = QPropertyAnimation(self, b"minimumSize")
        self.anim.setDuration(150)
        self.anim.setEndValue(QSize(185, 265))
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Scale back down
        self.anim = QPropertyAnimation(self, b"minimumSize")
        self.anim.setDuration(150)
        self.anim.setEndValue(QSize(180, 260))
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.start()
        super().leaveEvent(event)

    def update_state_ui(self):
        self.setProperty("state", self.state.value)
        is_orig = (self.state == CardState.RECOMMENDED)
        self.badge.setText("ORIGINAL" if is_orig else "COPY")
        self.badge.setObjectName("Badge" if is_orig else "BadgeCopy")
        self.badge.style().unpolish(self.badge)
        self.badge.style().polish(self.badge)
        
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        self.clicked.emit(self.file_info)
        self.set_state(CardState.RECOMMENDED)
        super().mousePressEvent(event)

    def toggle_state(self):
        if self.state == CardState.RECOMMENDED:
            self.set_state(CardState.DELETE)
        else:
            self.set_state(CardState.RECOMMENDED)

    def set_state(self, state: CardState):
        if self.state != state:
            self.state = state
            self.update_state_ui()
            self.stateChanged.emit(self.file_info, self.state)


class DuplicateGroupCard(QFrame):
    """Card representing a group of duplicates with collapsible content."""
    selectionChanged = pyqtSignal()
    imageClicked = pyqtSignal(FileInfo)

    def __init__(self, group: DuplicateGroup, group_number: int, strategy: str, parent=None):
        super().__init__(parent)
        self.group = group
        self.group_number = group_number
        self.strategy = strategy
        self.setObjectName("GroupCard")
        self.cards: Dict[str, ImageCard] = {}
        self.is_collapsed = False
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 15)
        self.main_layout.setSpacing(0)

        # Header
        self.header = QFrame()
        self.header.setObjectName("GroupHeader")
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout = QHBoxLayout(self.header)
        
        self.title_label = QLabel()
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.status_icon = QLabel("▼")
        header_layout.addWidget(self.status_icon)
        
        self.main_layout.addWidget(self.header)

        # Content Container
        self.content_container = QWidget()
        content_v_layout = QVBoxLayout(self.content_container)
        content_v_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(280)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(15)

        suggestion_engine = SuggestionEngine()
        keeper, reason = suggestion_engine.suggest_keeper(self.group.files, self.strategy)

        for file_info in self.group.files:
            is_rec = (file_info.path == keeper.path)
            card = ImageCard(file_info, is_rec, reason if is_rec else "")
            card.stateChanged.connect(self.on_card_state_changed)
            card.clicked.connect(self.imageClicked.emit)
            self.cards[file_info.path] = card
            content_layout.addWidget(card)

        content_layout.addStretch()
        self.scroll_area.setWidget(content_widget)
        content_v_layout.addWidget(self.scroll_area)
        
        self.main_layout.addWidget(self.content_container)

        self.setStyleSheet(ui_styles.GROUP_CARD_STYLE)
        self.header.mousePressEvent = self.toggle_collapse
        self.update_header()

    def update_header(self):
        wasted = format_bytes(self.group.get_total_wasted_space())
        selected = self.get_selected_for_deletion()
        reclaimable = format_bytes(sum(f.size for f in selected))
        
        status_text = f"Group #{self.group_number} • {len(self.group.files)} duplicates"
        if selected:
            status_text += f" • <span style='color: #4CAF50;'>{reclaimable} selected</span>"
        else:
            status_text += f" • {wasted} total"
        self.title_label.setText(status_text)

    def toggle_collapse(self, event=None):
        self.is_collapsed = not self.is_collapsed
        self.status_icon.setText("►" if self.is_collapsed else "▼")
        
        # Smooth collapse animation
        start_height = self.content_container.height()
        end_height = 0 if self.is_collapsed else 280 # 280 is the fixedHeight set in init_ui
        
        self.anim = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.anim.setDuration(300)
        self.anim.setStartValue(start_height)
        self.anim.setEndValue(end_height)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.anim.start()
        
        self.update_header()

    def on_card_state_changed(self, file_info: FileInfo, new_state: CardState):
        """Implement Smart Selection: Only one KEEP per group."""
        if new_state == CardState.RECOMMENDED:
            # Mark all others as DELETE
            for path, card in self.cards.items():
                if path != file_info.path:
                    card.set_state(CardState.DELETE)
        self.update_header()
        self.selectionChanged.emit()

    def deselect_all(self):
        for card in self.cards.values():
            card.set_state(CardState.NEUTRAL)
        self.update_header()
        self.selectionChanged.emit()

    def get_selected_for_deletion(self) -> List[FileInfo]:
        return [c.file_info for c in self.cards.values() if c.state == CardState.DELETE]

class ResultsView(QMainWindow):
    """Overhauled main results window with batch loading for performance."""
    
    def __init__(self, duplicate_groups: List[DuplicateGroup], parent=None):
        super().__init__(parent)
        self.duplicate_groups = duplicate_groups
        self.group_widgets: List[DuplicateGroupCard] = []
        self.strategy = 'keep_highest_resolution'
        
        # Incremental Loading State
        self.batch_index = 0
        self.batch_size = 15
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self.load_next_batch)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Results - Duplicate File Finder")
        self.setMinimumSize(1300, 900)
        self.setStyleSheet(ui_styles.GLOBAL_STYLES)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Summary Bar
        summary_bar = QWidget()
        summary_bar.setObjectName("SummaryBar")
        summary_bar.setFixedHeight(85)
        summary_bar.setStyleSheet(ui_styles.SUMMARY_BAR_STYLE)
        summary_layout = QVBoxLayout(summary_bar)
        summary_layout.setSpacing(5)
        
        top_h = QHBoxLayout()
        self.stat_label = QLabel()
        self.stat_label.setObjectName("StatLabel")
        top_h.addWidget(self.stat_label)
        
        top_h.addStretch()
        
        clear_btn = QPushButton("Clear Selection")
        clear_btn.setObjectName("SecondaryBtn")
        clear_btn.setFixedWidth(140)
        clear_btn.clicked.connect(self.clear_all_selection)
        top_h.addWidget(clear_btn)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setObjectName("ActionBtn")
        self.delete_btn.clicked.connect(self.confirm_deletion)
        top_h.addWidget(self.delete_btn)
        
        summary_layout.addLayout(top_h)

        # Recovery Bar
        bar_container = QWidget()
        bar_layout = QHBoxLayout(bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.recovery_bar = QFrame()
        self.recovery_bar.setFixedHeight(6)
        self.recovery_bar.setStyleSheet(f"background-color: {ui_styles.COLORS['border']}; border-radius: 3px;")
        self.recovery_fill = QFrame(self.recovery_bar)
        self.recovery_fill.setFixedHeight(6)
        self.recovery_fill.setStyleSheet(f"background-color: {ui_styles.COLORS['primary']}; border-radius: 3px;")
        
        bar_layout.addWidget(self.recovery_bar)
        summary_layout.addWidget(bar_container)
        
        main_layout.addWidget(summary_bar)

        # 2. Bulk Action Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"background-color: {ui_styles.COLORS['bg']}; border-bottom: 1px solid {ui_styles.COLORS['border']};")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(20, 0, 20, 0)
        
        toolbar_layout.addWidget(QLabel("Auto Select Best:"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Keep Highest Resolution", "Keep Newest", "Keep Oldest", "Keep Shortest Path"
        ])
        self.strategy_combo.setFixedWidth(200)
        self.strategy_combo.currentTextChanged.connect(self.on_strategy_changed)
        toolbar_layout.addWidget(self.strategy_combo)
        
        toolbar_layout.addStretch()
        
        main_layout.addWidget(toolbar)

        # 3. Main Content - Splitter for Sidebar
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Results List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(24, 24, 24, 24)
        self.results_layout.setSpacing(0)
        
        self.scroll_area.setWidget(self.results_container)
        self.splitter.addWidget(self.scroll_area)
        
        # Side Preview Panel (Initially Hidden)
        self.preview_panel = QFrame()
        self.preview_panel.setFixedWidth(400)
        self.preview_panel.setStyleSheet(f"background-color: {ui_styles.COLORS['card_bg']}; border-left: 1px solid {ui_styles.COLORS['border']};")
        self.preview_layout = QVBoxLayout(self.preview_panel)
        
        self.preview_image = QLabel()
        self.preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_image.setStyleSheet("background-color: #000; border-radius: 8px;")
        self.preview_image.setMinimumHeight(400)
        
        self.preview_meta = QLabel()
        self.preview_meta.setWordWrap(True)
        self.preview_meta.setStyleSheet(f"color: {ui_styles.COLORS['text']}; font-size: 13px; line-height: 1.5;")
        
        self.preview_layout.addWidget(self.preview_image)
        self.preview_layout.addSpacing(20)
        self.preview_layout.addWidget(self.preview_meta)
        self.preview_layout.addStretch()
        
        self.preview_panel.hide()
        self.splitter.addWidget(self.preview_panel)
        
        main_layout.addWidget(self.splitter)

        # Initialize Data
        self.batch_index = 0
        self.batch_size = 15
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self.load_next_batch)
        
        self.refresh_results()

    def refresh_results(self):
        # Clear existing
        for i in reversed(range(self.results_layout.count())):
            item = self.results_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        self.group_widgets.clear()
        
        # Start incremental loading
        self.batch_index = 0
        self.stat_label.setText("Preparing results...")
        self.load_timer.start(5) # Trigger every 5ms

    def load_next_batch(self):
        end = min(self.batch_index + self.batch_size, len(self.duplicate_groups))
        
        for i in range(self.batch_index, end):
            group = self.duplicate_groups[i]
            group_card = DuplicateGroupCard(group, i + 1, self.strategy)
            group_card.selectionChanged.connect(self.update_summary)
            group_card.imageClicked.connect(self.show_preview)
            self.group_widgets.append(group_card)
            self.results_layout.addWidget(group_card)
        
        self.batch_index = end
        
        # Update progress label
        progress_pct = int((self.batch_index / len(self.duplicate_groups)) * 100)
        self.stat_label.setText(f"Rendering Results... {progress_pct}%")

        if self.batch_index >= len(self.duplicate_groups):
            self.load_timer.stop()
            self.results_layout.addStretch()
            self.update_summary()

    def show_preview(self, file_info: FileInfo):
        self.preview_panel.show()
        pixmap = QPixmap(file_info.path)
        if not pixmap.isNull():
            self.preview_image.setPixmap(pixmap.scaled(
                380, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.preview_image.setText("Unable to load image")

        res_str = f"{file_info.resolution[0]}x{file_info.resolution[1]}" if file_info.resolution else "Unknown"
        meta_html = f"""
            <h3 style='color: #4CAF50;'>File Details</h3>
            <b>Name:</b> {os.path.basename(file_info.path)}<br><br>
            <b>Resolution:</b> {res_str}<br><br>
            <b>Size:</b> {format_bytes(file_info.size)}<br><br>
            <b>Path:</b> {file_info.path}<br><br>
            <b>Modified:</b> {os.path.getmtime(file_info.path) if os.path.exists(file_info.path) else ''}
        """
        self.preview_meta.setText(meta_html)

    def update_summary(self):
        total_selected = 0
        total_reclaimable = 0
        total_groups = len(self.duplicate_groups)
        max_possible = sum(g.get_total_wasted_space() for g in self.duplicate_groups)
        
        for g in self.group_widgets:
            selected = g.get_selected_for_deletion()
            total_selected += len(selected)
            total_reclaimable += sum(f.size for f in selected)

        self.stat_label.setText(
            f"<b>{total_groups}</b> Groups • "
            f"<b>{total_selected}</b> Selected • "
            f"<b>{format_bytes(total_reclaimable)}</b> to Reclaim"
        )
        self.delete_btn.setEnabled(total_selected > 0)
        
        # Update recovery bar width smoothly
        if max_possible > 0:
            percentage = min(total_reclaimable / max_possible, 1.0)
            target_width = int(self.recovery_bar.width() * percentage)
            target_width = max(target_width, 1)
            
            self.bar_anim = QPropertyAnimation(self.recovery_fill, b"minimumWidth")
            self.bar_anim.setDuration(300)
            self.bar_anim.setEndValue(target_width)
            self.bar_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.bar_anim.start()
        else:
            self.recovery_fill.setFixedWidth(0)

    def on_strategy_changed(self, text: str):
        strategy_map = {
            "Keep Highest Resolution": "keep_highest_resolution",
            "Keep Oldest": "keep_oldest",
            "Keep Newest": "keep_newest",
            "Keep Shortest Path": "keep_shortest_path"
        }
        self.strategy = strategy_map.get(text, "keep_highest_resolution")
        self.refresh_results()
        self.update_summary()

    def clear_all_selection(self):
        for g in self.group_widgets:
            g.deselect_all()
        self.update_summary()

    def confirm_deletion(self):
        selected_files = []
        for g in self.group_widgets:
            selected_files.extend(g.get_selected_for_deletion())
        
        if not selected_files: return

        dialog = DeletionConfirmationDialog(selected_files, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            method, confirmed = dialog.get_result()
            if confirmed:
                self.perform_deletion(selected_files, method)

    def perform_deletion(self, files: List[FileInfo], method: DeletionMethod):
        manager = DeletionManager()
        files_with_sizes = [(f.path, f.size) for f in files]
        report = manager.delete_files_with_sizes(files_with_sizes, method)
        
        if report.successful_deletions == report.total_files:
            QMessageBox.information(self, "Success", f"Cleaned {report.successful_deletions} files.\n{format_bytes(report.total_space_freed)} freed.")
            self.close()
        else:
            QMessageBox.warning(self, "Partial Success", f"Errors occurred. Check logs:\n{report.log_file_path}")

    def export_results(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Results", "duplicate_results.json", "JSON (*.json)")
        if not file_path: return
        try:
            data = {'groups': [g.group.to_dict() for g in self.group_widgets]}
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "Exported", f"Results saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
