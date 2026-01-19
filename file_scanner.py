"""
File Scanner Module for Duplicate File Finder.
Recursively scans directories and collects image files with metadata.
"""

import os
from dataclasses import dataclass
from typing import List, Callable, Optional, Set
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from utils import get_image_resolution, is_system_folder, get_file_times
from logger import get_logger

logger = get_logger()


@dataclass
class FileInfo:
    """Represents metadata for a scanned file."""
    path: str
    size: int
    extension: str
    resolution: Optional[tuple]  # (width, height) for images
    created_time: float
    modified_time: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'path': self.path,
            'size': self.size,
            'extension': self.extension,
            'resolution': self.resolution,
            'created_time': self.created_time,
            'modified_time': self.modified_time,
            'created_date': datetime.fromtimestamp(self.created_time).isoformat(),
            'modified_date': datetime.fromtimestamp(self.modified_time).isoformat()
        }


class FileScanner:
    """Scans directories for image files and collects metadata."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the file scanner with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.supported_extensions = set(self.config.get('supported_extensions', []))
        self.scan_options = self.config.get('scan_options', {})
        self.files_scanned = 0
        self.errors = []
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Unable to load config from {config_path}: {e}. Using defaults.")
            return {}
    
    def scan_directories(self, 
                        root_paths: List[str], 
                        progress_callback: Optional[Callable[[int, str], None]] = None) -> List[FileInfo]:
        """
        Recursively scan directories for image files.
        
        Args:
            root_paths: List of root directory paths to scan
            progress_callback: Optional callback function(files_scanned, current_path)
            
        Returns:
            List of FileInfo objects for all discovered image files
        """
        logger.info(f"Starting scan of {len(root_paths)} root directories")
        self.files_scanned = 0
        self.errors = []
        
        all_files = []
        scanned_paths: Set[str] = set()  # Avoid scanning same directory multiple times
        
        for root_path in root_paths:
            if not os.path.exists(root_path):
                error_msg = f"Path does not exist: {root_path}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                continue
            
            # Normalize path to avoid duplicates
            normalized_path = os.path.normpath(os.path.abspath(root_path))
            
            if normalized_path in scanned_paths:
                logger.info(f"Skipping already scanned path: {root_path}")
                continue
            
            scanned_paths.add(normalized_path)
            files = self._scan_single_directory(normalized_path, progress_callback)
            all_files.extend(files)
        
        logger.info(f"Scan complete. Found {len(all_files)} image files. Errors: {len(self.errors)}")
        return all_files
    
    def _scan_single_directory(self, 
                               root_path: str, 
                               progress_callback: Optional[Callable[[int, str], None]]) -> List[FileInfo]:
        """Scan a single directory tree."""
        files = []
        
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Filter out system/hidden folders if configured
                if not self.scan_options.get('include_hidden_folders', False):
                    dirnames[:] = [d for d in dirnames if not is_system_folder(os.path.join(dirpath, d))]
                
                # Process files in current directory
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    
                    try:
                        file_info = self._process_file(file_path)
                        if file_info:
                            files.append(file_info)
                            self.files_scanned += 1
                            
                            # Call progress callback
                            if progress_callback and self.files_scanned % 10 == 0:
                                progress_callback(self.files_scanned, file_path)
                    
                    except Exception as e:
                        error_msg = f"Error processing {file_path}: {e}"
                        logger.warning(error_msg)
                        self.errors.append(error_msg)
        
        except PermissionError as e:
            error_msg = f"Permission denied accessing {root_path}: {e}"
            logger.warning(error_msg)
            self.errors.append(error_msg)
        
        except Exception as e:
            error_msg = f"Error scanning {root_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
        
        return files
    
    def _process_file(self, file_path: str) -> Optional[FileInfo]:
        """
        Process a single file and extract metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileInfo object or None if file should be skipped
        """
        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        
        # Check if extension is supported
        if extension not in self.supported_extensions:
            return None
        
        # Get file size
        try:
            size = os.path.getsize(file_path)
        except Exception as e:
            logger.warning(f"Unable to get size for {file_path}: {e}")
            return None
        
        # Check minimum file size
        min_size = self.scan_options.get('min_file_size_bytes', 0)
        if size < min_size:
            return None
        
        # Get image resolution
        resolution = get_image_resolution(file_path)
        
        # Get file times
        created_time, modified_time = get_file_times(file_path)
        
        return FileInfo(
            path=file_path,
            size=size,
            extension=extension,
            resolution=resolution,
            created_time=created_time,
            modified_time=modified_time
        )
    
    def get_scan_summary(self) -> dict:
        """
        Get summary of the last scan operation.
        
        Returns:
            Dictionary with scan statistics
        """
        return {
            'files_scanned': self.files_scanned,
            'errors_count': len(self.errors),
            'errors': self.errors[:10]  # Limit to first 10 errors
        }
