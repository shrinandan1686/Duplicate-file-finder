"""
Deduplication Engine for Duplicate File Finder.
Implements multi-stage duplicate detection pipeline.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from file_scanner import FileInfo
from utils import compute_file_hash, format_bytes
from logger import get_logger

logger = get_logger()


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate files."""
    files: List[FileInfo]
    detection_method: str  # 'hash' or 'perceptual'
    similarity_score: float = 100.0  # 100 = exact duplicate, <100 = similar
    
    def get_total_wasted_space(self) -> int:
        """Calculate total wasted disk space (all files except one)."""
        if len(self.files) <= 1:
            return 0
        # All duplicates have same size, so (count - 1) * size
        return (len(self.files) - 1) * self.files[0].size
    
    def get_suggested_keeper(self, strategy: str = 'keep_oldest') -> FileInfo:
        """
        Get the suggested file to keep based on strategy.
        
        Args:
            strategy: One of 'keep_oldest', 'keep_newest', 'keep_highest_resolution',
                     'keep_shortest_path'
            
        Returns:
            FileInfo object that should be kept
        """
        if not self.files:
            return None
        
        if strategy == 'keep_oldest':
            return min(self.files, key=lambda f: f.created_time)
        
        elif strategy == 'keep_newest':
            return max(self.files, key=lambda f: f.created_time)
        
        elif strategy == 'keep_highest_resolution':
            # Filter files with valid resolution
            files_with_res = [f for f in self.files if f.resolution]
            if not files_with_res:
                return self.files[0]  # Fallback to first file
            
            # Calculate area (width * height)
            return max(files_with_res, key=lambda f: f.resolution[0] * f.resolution[1])
        
        elif strategy == 'keep_shortest_path':
            return min(self.files, key=lambda f: len(f.path))
        
        else:
            return self.files[0]
    
    def get_suggestion_reason(self, keeper: FileInfo, strategy: str) -> str:
        """Get human-readable reason for the suggestion."""
        if strategy == 'keep_oldest':
            from datetime import datetime
            date_str = datetime.fromtimestamp(keeper.created_time).strftime('%Y-%m-%d')
            return f"Oldest file (created {date_str})"
        
        elif strategy == 'keep_newest':
            from datetime import datetime
            date_str = datetime.fromtimestamp(keeper.created_time).strftime('%Y-%m-%d')
            return f"Newest file (created {date_str})"
        
        elif strategy == 'keep_highest_resolution':
            if keeper.resolution:
                return f"Highest resolution ({keeper.resolution[0]}x{keeper.resolution[1]})"
            return "First file (no resolution data)"
        
        elif strategy == 'keep_shortest_path':
            return f"Shortest path ({len(keeper.path)} chars)"
        
        return "Default selection"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'files': [f.to_dict() for f in self.files],
            'file_count': len(self.files),
            'detection_method': self.detection_method,
            'similarity_score': self.similarity_score,
            'wasted_space_bytes': self.get_total_wasted_space(),
            'wasted_space_formatted': format_bytes(self.get_total_wasted_space())
        }


class DeduplicationEngine:
    """Multi-stage deduplication engine."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the deduplication engine."""
        self.config = self._load_config(config_path)
        self.max_workers = self.config.get('performance', {}).get('max_worker_threads', 4)
        self.hash_chunk_size = self.config.get('performance', {}).get('hash_chunk_size_kb', 64)
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Unable to load config: {e}")
            return {}
    
    def find_duplicates(self, 
                       files: List[FileInfo],
                       use_perceptual: bool = False,
                       progress_callback: Optional[Callable[[int, int], None]] = None) -> List[DuplicateGroup]:
        """
        Find duplicate files using multi-stage pipeline.
        
        Args:
            files: List of FileInfo objects to analyze
            use_perceptual: Enable perceptual hashing for similar images
            progress_callback: Optional callback(current, total)
            
        Returns:
            List of DuplicateGroup objects
        """
        logger.info(f"Starting deduplication of {len(files)} files")
        
        # Stage 1: Group by size and extension (fast pre-filter)
        size_groups = self._group_by_size_and_extension(files)
        logger.info(f"Stage 1: Found {len(size_groups)} size groups")
        
        # Stage 2: Hash-based exact duplicate detection
        duplicate_groups = self._find_exact_duplicates(size_groups, progress_callback)
        logger.info(f"Stage 2: Found {len(duplicate_groups)} exact duplicate groups")
        
        # Stage 3: Optional perceptual hashing
        if use_perceptual:
            perceptual_groups = self._find_similar_images(files, duplicate_groups, progress_callback)
            duplicate_groups.extend(perceptual_groups)
            logger.info(f"Stage 3: Found {len(perceptual_groups)} similar image groups")
        
        # Calculate statistics
        total_duplicates = sum(len(group.files) for group in duplicate_groups)
        total_wasted = sum(group.get_total_wasted_space() for group in duplicate_groups)
        logger.info(f"Total: {len(duplicate_groups)} groups, {total_duplicates} files, "
                   f"{format_bytes(total_wasted)} wasted space")
        
        return duplicate_groups
    
    def _group_by_size_and_extension(self, files: List[FileInfo]) -> Dict[tuple, List[FileInfo]]:
        """
        Stage 1: Group files by (size, extension).
        
        Returns:
            Dictionary mapping (size, extension) to list of files
        """
        groups = defaultdict(list)
        
        for file_info in files:
            key = (file_info.size, file_info.extension)
            groups[key].append(file_info)
        
        # Filter out singleton groups (no possible duplicates)
        return {k: v for k, v in groups.items() if len(v) > 1}
    
    def _find_exact_duplicates(self, 
                               size_groups: Dict[tuple, List[FileInfo]],
                               progress_callback: Optional[Callable[[int, int], None]]) -> List[DuplicateGroup]:
        """
        Stage 2: Find exact duplicates using SHA-256 hashing.
        
        Args:
            size_groups: Groups of files with same size and extension
            progress_callback: Progress callback
            
        Returns:
            List of DuplicateGroup objects for exact duplicates
        """
        duplicate_groups = []
        
        # Calculate total files to process
        total_files = sum(len(files) for files in size_groups.values())
        processed_files = 0
        
        for (size, ext), file_list in size_groups.items():
            # Compute hashes for all files in this size group
            hash_map = defaultdict(list)
            
            # Use thread pool for parallel hashing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {
                    executor.submit(compute_file_hash, f.path, 'sha256', self.hash_chunk_size): f
                    for f in file_list
                }
                
                for future in as_completed(future_to_file):
                    file_info = future_to_file[future]
                    try:
                        file_hash = future.result()
                        if file_hash:
                            hash_map[file_hash].append(file_info)
                        
                        processed_files += 1
                        if progress_callback and processed_files % 10 == 0:
                            progress_callback(processed_files, total_files)
                    
                    except Exception as e:
                        logger.error(f"Error hashing {file_info.path}: {e}")
            
            # Create duplicate groups for files with same hash
            for file_hash, files_with_hash in hash_map.items():
                if len(files_with_hash) > 1:
                    group = DuplicateGroup(
                        files=files_with_hash,
                        detection_method='hash',
                        similarity_score=100.0
                    )
                    duplicate_groups.append(group)
        
        return duplicate_groups
    
    def _find_similar_images(self,
                            all_files: List[FileInfo],
                            exact_duplicates: List[DuplicateGroup],
                            progress_callback: Optional[Callable[[int, int], None]]) -> List[DuplicateGroup]:
        """
        Stage 3: Find visually similar images using perceptual hashing.
        
        Args:
            all_files: All scanned files
            exact_duplicates: Already found exact duplicates (to exclude)
            progress_callback: Progress callback
            
        Returns:
            List of DuplicateGroup objects for similar images
        """
        try:
            import imagehash
            from PIL import Image
        except ImportError:
            logger.warning("imagehash library not available. Skipping perceptual hashing.")
            return []
        
        # Get files already in exact duplicate groups
        exact_duplicate_paths = set()
        for group in exact_duplicates:
            for file_info in group.files:
                exact_duplicate_paths.add(file_info.path)
        
        # Filter out exact duplicates
        files_to_check = [f for f in all_files if f.path not in exact_duplicate_paths]
        
        logger.info(f"Computing perceptual hashes for {len(files_to_check)} files")
        
        # Compute perceptual hashes
        phash_map = {}
        for i, file_info in enumerate(files_to_check):
            try:
                with Image.open(file_info.path) as img:
                    phash = imagehash.average_hash(img)
                    phash_map[file_info.path] = (phash, file_info)
                
                if progress_callback and i % 10 == 0:
                    progress_callback(i, len(files_to_check))
            
            except Exception as e:
                logger.warning(f"Unable to compute perceptual hash for {file_info.path}: {e}")
        
        # Find similar images based on hash distance
        threshold = self.config.get('perceptual_hash', {}).get('similarity_threshold', 5)
        similar_groups = []
        processed = set()
        
        for path1, (hash1, file1) in phash_map.items():
            if path1 in processed:
                continue
            
            similar_files = [file1]
            processed.add(path1)
            
            for path2, (hash2, file2) in phash_map.items():
                if path2 in processed:
                    continue
                
                # Calculate hamming distance
                distance = hash1 - hash2
                if distance <= threshold:
                    similar_files.append(file2)
                    processed.add(path2)
            
            # Create group if we found similar images
            if len(similar_files) > 1:
                similarity_score = 100 - (threshold * 2)  # Rough approximation
                group = DuplicateGroup(
                    files=similar_files,
                    detection_method='perceptual',
                    similarity_score=similarity_score
                )
                similar_groups.append(group)
        
        return similar_groups
