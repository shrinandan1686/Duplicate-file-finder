"""
Modern Dark Theme Stylesheets for Duplicate File Finder.
Defines palette tokens and component-specific styles.
"""

# Color Palette
COLORS = {
    'bg': '#121212',
    'card_bg': '#1E1E1E',
    'card_hover': '#252525',
    'text': '#FFFFFF',
    'text_dim': '#B0B0B0',
    'primary': '#4CAF50',
    'primary_hover': '#66BB6A',
    'danger': '#F44336',
    'danger_hover': '#D32F2F',
    'recommended': '#4CAF50',
    'delete_overlay': 'rgba(244, 67, 54, 0.4)',
    'border': '#333333',
    'border_highlight': '#4CAF50'
}

GLOBAL_STYLES = f"""
    QMainWindow, QDialog {{
        background-color: {COLORS['bg']};
    }}
    
    QWidget {{
        color: {COLORS['text']};
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }}
    
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        border: none;
        background: {COLORS['bg']};
        width: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {COLORS['border']};
        min-height: 20px;
        border-radius: 5px;
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QComboBox {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 5px 10px;
        color: {COLORS['text']};
    }}
    
    QComboBox::drop-down {{
        border: none;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['card_bg']};
        selection-background-color: {COLORS['primary']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
    }}

    QPushButton:focus, QComboBox:focus, QSlider:focus {{
        border: 2px solid {COLORS['primary']};
        outline: none;
    }}
"""

SUMMARY_BAR_STYLE = f"""
    #SummaryBar {{
        background-color: {COLORS['card_bg']};
        border-bottom: 1px solid {COLORS['border']};
        padding: 5px 20px;
    }}
    #StatLabel {{
        font-size: 15px;
        font-weight: 500;
        color: {COLORS['text']};
    }}
    #ActionBtn {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        font-size: 14px;
    }}
    #ActionBtn:hover {{
        background-color: {COLORS['primary_hover']};
    }}
    #SecondaryBtn {{
        background-color: transparent;
        color: {COLORS['text_dim']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 9px 20px;
        font-weight: 500;
        font-size: 14px;
    }}
    #SecondaryBtn:hover {{
        background-color: {COLORS['card_hover']};
        color: {COLORS['text']};
        border-color: {COLORS['text_dim']};
    }}
"""

GROUP_CARD_STYLE = f"""
    #GroupCard {{
        background-color: {COLORS['card_bg']};
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
        margin-bottom: 24px;
    }}
    #GroupHeader {{
        background-color: transparent;
        border-bottom: 1px solid {COLORS['border']};
    }}
    #GroupHeader QLabel {{
        font-size: 15px;
        font-weight: bold;
        color: {COLORS['text']};
        padding: 12px 20px;
    }}
    QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {{
        background-color: transparent;
        border: none;
    }}
"""

IMAGE_CARD_STYLE = f"""
    #ImageCard {{
        background-color: {COLORS['bg']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px;
    }}
    #ImageCard:hover {{
        background-color: {COLORS['card_hover']};
        border-color: {COLORS['primary']};
    }}
    #ImageCard[state="recommended"] {{
        border-color: {COLORS['recommended']};
    }}
    #ImageCard[state="delete"] {{
        border-color: {COLORS['danger']};
    }}
    #Thumbnail {{
        border-radius: 4px;
        background-color: #000;
    }}
    #MetadataLabel {{
        color: {COLORS['text_dim']};
        font-size: 11px;
    }}
    #FileNameLabel {{
        font-weight: bold;
        font-size: 12px;
    }}
    #Badge {{
        background-color: {COLORS['recommended']};
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
    }}
    #BadgeCopy {{
        background-color: {COLORS['danger']};
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
    }}
"""
