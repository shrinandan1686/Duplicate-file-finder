"""
Duplicate File Finder - Main Application Entry Point
A safe and user-friendly tool for detecting and managing duplicate image files.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui_main_window import MainWindow
from logger import setup_logger

# Initialize logger
logger = setup_logger()


def main():
    """Main application entry point."""
    logger.info("Starting Duplicate File Finder application")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Duplicate File Finder")
    app.setOrganizationName("DuplicateFinder")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Run application
    exit_code = app.exec()
    
    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
