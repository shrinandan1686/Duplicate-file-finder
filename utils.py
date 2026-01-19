"""
Utility functions for the Duplicate File Finder application.
Provides helpers for file operations, formatting, and image processing.
"""

import os
import hashlib
from typing import Tuple, Optional
from PIL import Image
from logger import get_logger

logger = get_logger()


def format_bytes(bytes_size: int) -> str:
    """
    Convert bytes to human-readable format (KB, MB, GB, TB).
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def get_image_resolution(file_path: str) -> Optional[Tuple[int, int]]:
    """
    Extract width and height from an image file.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Tuple of (width, height) or None if unable to read
    """
    try:
        with Image.open(file_path) as img:
            return img.size  # Returns (width, height)
    except Exception as e:
        logger.warning(f"Unable to get resolution for {file_path}: {e}")
        return None


def is_system_folder(folder_path: str) -> bool:
    """
    Check if a folder is a system or hidden folder that should be excluded.
    
    Args:
        folder_path: Path to the folder
        
    Returns:
        True if folder should be excluded, False otherwise
    """
    # Common system folders on Windows
    system_folders = {
        '$recycle.bin', 'system volume information', 'windows',
        'program files', 'program files (x86)', 'programdata',
        'appdata', '$windows.~bt', 'recovery', 'perflogs'
    }
    
    folder_name = os.path.basename(folder_path).lower()
    
    # Check if it's a system folder
    if folder_name in system_folders:
        return True
    
    # Check if it starts with special characters (hidden/system)
    if folder_name.startswith('$') or folder_name.startswith('.'):
        return True
    
    # Check Windows file attributes for hidden/system flags
    try:
        import ctypes
        attrs = ctypes.windll.kernel32.GetFileAttributesW(folder_path)
        # FILE_ATTRIBUTE_HIDDEN = 0x2, FILE_ATTRIBUTE_SYSTEM = 0x4
        if attrs != -1 and (attrs & 0x2 or attrs & 0x4):
            return True
    except Exception:
        pass  # If we can't check attributes, don't exclude
    
    return False


def generate_thumbnail(file_path: str, thumbnail_size: Tuple[int, int] = (150, 150), 
                      cache_dir: str = "thumbnails") -> Optional[str]:
    """
    Generate a thumbnail for an image file.
    
    Args:
        file_path: Path to the original image
        thumbnail_size: Size of the thumbnail as (width, height)
        cache_dir: Directory to store cached thumbnails
        
    Returns:
        Path to the generated thumbnail or None if failed
    """
    try:
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate thumbnail filename from original file's hash
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        thumbnail_ext = os.path.splitext(file_path)[1].lower()
        if thumbnail_ext not in ['.jpg', '.jpeg', '.png']:
            thumbnail_ext = '.jpg'
        
        thumbnail_path = os.path.join(cache_dir, f"{file_hash}{thumbnail_ext}")
        
        # Return cached thumbnail if it exists
        if os.path.exists(thumbnail_path):
            return thumbnail_path
        
        # Generate new thumbnail
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if necessary (for JPEG)
            if img.mode == 'RGBA' and thumbnail_ext in ['.jpg', '.jpeg']:
                img = img.convert('RGB')
            
            # Create thumbnail maintaining aspect ratio
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, quality=85, optimize=True)
            
        return thumbnail_path
        
    except Exception as e:
        logger.warning(f"Unable to generate thumbnail for {file_path}: {e}")
        return None


def compute_file_hash(file_path: str, algorithm: str = 'sha256', 
                     chunk_size_kb: int = 64) -> Optional[str]:
    """
    Compute cryptographic hash of a file using chunked reading.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm ('sha256', 'md5', etc.)
        chunk_size_kb: Size of chunks to read in KB
        
    Returns:
        Hexadecimal hash string or None if failed
    """
    try:
        hash_func = hashlib.new(algorithm)
        chunk_size = chunk_size_kb * 1024
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
        
    except Exception as e:
        logger.error(f"Unable to compute hash for {file_path}: {e}")
        return None


def is_file_locked(file_path: str) -> bool:
    """
    Check if a file is locked by another process.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is locked, False otherwise
    """
    try:
        # Try to open the file in exclusive mode
        with open(file_path, 'a'):
            pass
        return False
    except (IOError, OSError):
        return True


def get_file_times(file_path: str) -> Tuple[float, float]:
    """
    Get creation and modification times for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (creation_time, modification_time) as timestamps
    """
    try:
        stat = os.stat(file_path)
        # On Windows, st_ctime is creation time
        return (stat.st_ctime, stat.st_mtime)
    except Exception as e:
        logger.warning(f"Unable to get file times for {file_path}: {e}")
        return (0, 0)
