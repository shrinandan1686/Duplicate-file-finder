"""
Suggestion Engine for Duplicate File Finder.
Helps users decide which file to keep in duplicate groups.
"""

from typing import List, Tuple
from file_scanner import FileInfo
from logger import get_logger

logger = get_logger()


class SuggestionEngine:
    """Generates suggestions for which file to keep in duplicate groups."""
    
    STRATEGIES = {
        'keep_oldest': 'Keep the oldest file (by creation date)',
        'keep_newest': 'Keep the newest file (by creation date)',
        'keep_highest_resolution': 'Keep the file with highest resolution',
        'keep_shortest_path': 'Keep the file with shortest path',
        'keep_preferred_folder': 'Keep files in preferred folders'
    }
    
    def __init__(self, preferred_folders: List[str] = None):
        """
        Initialize the suggestion engine.
        
        Args:
            preferred_folders: List of folder paths in priority order
        """
        self.preferred_folders = preferred_folders or []
    
    def suggest_keeper(self, 
                      files: List[FileInfo], 
                      strategy: str = 'keep_highest_resolution') -> Tuple[FileInfo, str]:
        """
        Suggest which file to keep based on strategy.
        
        Args:
            files: List of duplicate FileInfo objects
            strategy: Strategy name
            
        Returns:
            Tuple of (suggested_file, reason_string)
        """
        if not files:
            return None, "No files provided"
        
        if len(files) == 1:
            return files[0], "Only one file"
        
        if strategy == 'keep_oldest':
            return self._suggest_oldest(files)
        
        elif strategy == 'keep_newest':
            return self._suggest_newest(files)
        
        elif strategy == 'keep_highest_resolution':
            return self._suggest_highest_resolution(files)
        
        elif strategy == 'keep_shortest_path':
            return self._suggest_shortest_path(files)
        
        elif strategy == 'keep_preferred_folder':
            return self._suggest_preferred_folder(files)
        
        else:
            logger.warning(f"Unknown strategy: {strategy}. Using first file.")
            return files[0], "Default (unknown strategy)"
    
    def _suggest_oldest(self, files: List[FileInfo]) -> Tuple[FileInfo, str]:
        """Suggest the oldest file by creation time."""
        oldest = min(files, key=lambda f: f.created_time)
        from datetime import datetime
        date_str = datetime.fromtimestamp(oldest.created_time).strftime('%Y-%m-%d %H:%M')
        return oldest, f"Oldest (created {date_str})"
    
    def _suggest_newest(self, files: List[FileInfo]) -> Tuple[FileInfo, str]:
        """Suggest the newest file by creation time."""
        newest = max(files, key=lambda f: f.created_time)
        from datetime import datetime
        date_str = datetime.fromtimestamp(newest.created_time).strftime('%Y-%m-%d %H:%M')
        return newest, f"Newest (created {date_str})"
    
    def _suggest_highest_resolution(self, files: List[FileInfo]) -> Tuple[FileInfo, str]:
        """Suggest the file with highest resolution."""
        # Filter files with valid resolution
        files_with_res = [f for f in files if f.resolution and f.resolution[0] > 0]
        
        if not files_with_res:
            # Fallback to oldest if no resolution info
            return self._suggest_oldest(files)
        
        # Find highest resolution by area (width * height)
        highest = max(files_with_res, key=lambda f: f.resolution[0] * f.resolution[1])
        return highest, f"Highest resolution ({highest.resolution[0]}×{highest.resolution[1]})"
    
    def _suggest_shortest_path(self, files: List[FileInfo]) -> Tuple[FileInfo, str]:
        """Suggest the file with shortest path (closer to root)."""
        shortest = min(files, key=lambda f: len(f.path))
        return shortest, f"Shortest path ({len(shortest.path)} chars)"
    
    def _suggest_preferred_folder(self, files: List[FileInfo]) -> Tuple[FileInfo, str]:
        """Suggest file based on preferred folder priority."""
        if not self.preferred_folders:
            # Fallback to highest resolution
            return self._suggest_highest_resolution(files)
        
        # Check each preferred folder in priority order
        for preferred in self.preferred_folders:
            for file_info in files:
                if preferred.lower() in file_info.path.lower():
                    folder_name = preferred.split('\\')[-1].split('/')[-1]
                    return file_info, f"In preferred folder ({folder_name})"
        
        # If no match, fallback to highest resolution
        return self._suggest_highest_resolution(files)
    
    def get_files_to_delete(self, 
                           files: List[FileInfo], 
                           keeper: FileInfo) -> List[FileInfo]:
        """
        Get list of files that should be deleted (all except keeper).
        
        Args:
            files: All duplicate files
            keeper: The file to keep
            
        Returns:
            List of files to delete
        """
        return [f for f in files if f.path != keeper.path]
