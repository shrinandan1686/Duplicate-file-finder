"""
Deletion Manager for Duplicate File Finder.
Handles safe file deletion with multiple safety mechanisms.
"""

import os
import json
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

try:
    import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False

from utils import is_file_locked, format_bytes
from logger import get_logger, log_deletion

logger = get_logger()


class DeletionMethod(Enum):
    """Deletion method enumeration."""
    RECYCLE_BIN = "recycle_bin"
    HARD_DELETE = "hard_delete"
    DRY_RUN = "dry_run"


@dataclass
class DeletionResult:
    """Result of a deletion operation."""
    file_path: str
    success: bool
    method: str
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'success': self.success,
            'method': self.method,
            'error': self.error,
            'timestamp': self.timestamp
        }


@dataclass
class DeletionReport:
    """Summary report of a deletion operation."""
    total_files: int
    successful_deletions: int
    failed_deletions: int
    total_space_freed: int
    method: str
    log_file_path: str
    results: List[DeletionResult]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_files': self.total_files,
            'successful_deletions': self.successful_deletions,
            'failed_deletions': self.failed_deletions,
            'total_space_freed': self.total_space_freed,
            'total_space_freed_formatted': format_bytes(self.total_space_freed),
            'method': self.method,
            'log_file_path': self.log_file_path,
            'results': [r.to_dict() for r in self.results]
        }


class DeletionManager:
    """Manages safe file deletion with logging and error handling."""
    
    def __init__(self, log_dir: str = "deletion_logs"):
        """
        Initialize the deletion manager.
        
        Args:
            log_dir: Directory to store deletion logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        if not SEND2TRASH_AVAILABLE:
            logger.warning("send2trash library not available. Recycle bin mode will not work.")
    
    def delete_files(self, 
                    file_paths: List[str],
                    method: DeletionMethod = DeletionMethod.RECYCLE_BIN) -> DeletionReport:
        """
        Delete files using the specified method.
        
        Args:
            file_paths: List of file paths to delete
            method: Deletion method to use
            
        Returns:
            DeletionReport with results and statistics
        """
        logger.info(f"Starting deletion of {len(file_paths)} files using {method.value}")
        
        results = []
        total_space_freed = 0
        
        for file_path in file_paths:
            result = self._delete_single_file(file_path, method)
            results.append(result)
            
            # Track space freed only for successful deletions
            if result.success and method != DeletionMethod.DRY_RUN:
                try:
                    # File is already deleted, we need to have tracked size beforehand
                    # For simplicity, we'll rely on the caller to provide size info
                    pass
                except:
                    pass
        
        # Calculate statistics
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        # Save deletion log
        log_path = self._save_deletion_log(results, method)
        
        report = DeletionReport(
            total_files=len(file_paths),
            successful_deletions=successful,
            failed_deletions=failed,
            total_space_freed=total_space_freed,
            method=method.value,
            log_file_path=log_path,
            results=results
        )
        
        logger.info(f"Deletion complete. Success: {successful}, Failed: {failed}")
        return report
    
    def delete_files_with_sizes(self,
                               file_paths_with_sizes: List[tuple],
                               method: DeletionMethod = DeletionMethod.RECYCLE_BIN) -> DeletionReport:
        """
        Delete files with known sizes to accurately track space freed.
        
        Args:
            file_paths_with_sizes: List of (file_path, size) tuples
            method: Deletion method to use
            
        Returns:
            DeletionReport with results and statistics
        """
        logger.info(f"Starting deletion of {len(file_paths_with_sizes)} files using {method.value}")
        
        results = []
        total_space_freed = 0
        
        for file_path, file_size in file_paths_with_sizes:
            result = self._delete_single_file(file_path, method)
            results.append(result)
            
            # Track space freed only for successful deletions
            if result.success and method != DeletionMethod.DRY_RUN:
                total_space_freed += file_size
        
        # Calculate statistics
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        # Save deletion log
        log_path = self._save_deletion_log(results, method)
        
        report = DeletionReport(
            total_files=len(file_paths_with_sizes),
            successful_deletions=successful,
            failed_deletions=failed,
            total_space_freed=total_space_freed,
            method=method.value,
            log_file_path=log_path,
            results=results
        )
        
        logger.info(f"Deletion complete. Success: {successful}, Failed: {failed}, "
                   f"Space freed: {format_bytes(total_space_freed)}")
        return report
    
    def _delete_single_file(self, file_path: str, method: DeletionMethod) -> DeletionResult:
        """
        Delete a single file.
        
        Args:
            file_path: Path to the file
            method: Deletion method
            
        Returns:
            DeletionResult for this file
        """
        # Pre-validation checks
        if not os.path.exists(file_path):
            error_msg = "File does not exist"
            log_deletion(file_path, method.value, "failed", error_msg)
            return DeletionResult(file_path, False, method.value, error_msg)
        
        if is_file_locked(file_path):
            error_msg = "File is locked by another process"
            log_deletion(file_path, method.value, "failed", error_msg)
            return DeletionResult(file_path, False, method.value, error_msg)
        
        # Dry run - just validate, don't delete
        if method == DeletionMethod.DRY_RUN:
            log_deletion(file_path, method.value, "success (dry run)")
            return DeletionResult(file_path, True, method.value)
        
        # Recycle bin deletion
        if method == DeletionMethod.RECYCLE_BIN:
            if not SEND2TRASH_AVAILABLE:
                error_msg = "send2trash library not available"
                log_deletion(file_path, method.value, "failed", error_msg)
                return DeletionResult(file_path, False, method.value, error_msg)
            
            try:
                send2trash.send2trash(file_path)
                log_deletion(file_path, method.value, "success")
                return DeletionResult(file_path, True, method.value)
            
            except Exception as e:
                error_msg = str(e)
                log_deletion(file_path, method.value, "failed", error_msg)
                return DeletionResult(file_path, False, method.value, error_msg)
        
        # Hard delete (permanent)
        if method == DeletionMethod.HARD_DELETE:
            try:
                os.remove(file_path)
                log_deletion(file_path, method.value, "success")
                return DeletionResult(file_path, True, method.value)
            
            except Exception as e:
                error_msg = str(e)
                log_deletion(file_path, method.value, "failed", error_msg)
                return DeletionResult(file_path, False, method.value, error_msg)
    
    def _save_deletion_log(self, results: List[DeletionResult], method: DeletionMethod) -> str:
        """
        Save deletion log to JSON file.
        
        Args:
            results: List of deletion results
            method: Deletion method used
            
        Returns:
            Path to the saved log file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"deletion_{timestamp}.json"
        log_path = os.path.join(self.log_dir, log_filename)
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'method': method.value,
            'total_files': len(results),
            'successful': sum(1 for r in results if r.success),
            'failed': sum(1 for r in results if not r.success),
            'results': [r.to_dict() for r in results]
        }
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Deletion log saved to {log_path}")
        except Exception as e:
            logger.error(f"Failed to save deletion log: {e}")
        
        return log_path
    
    def preview_deletion(self, file_paths_with_sizes: List[tuple]) -> dict:
        """
        Preview what would happen if files were deleted (dry run).
        
        Args:
            file_paths_with_sizes: List of (file_path, size) tuples
            
        Returns:
            Dictionary with preview information
        """
        total_size = sum(size for _, size in file_paths_with_sizes)
        
        # Check which files can be deleted
        deletable = []
        issues = []
        
        for file_path, size in file_paths_with_sizes:
            if not os.path.exists(file_path):
                issues.append(f"{file_path}: File does not exist")
            elif is_file_locked(file_path):
                issues.append(f"{file_path}: File is locked")
            else:
                deletable.append((file_path, size))
        
        deletable_size = sum(size for _, size in deletable)
        
        return {
            'total_files': len(file_paths_with_sizes),
            'deletable_files': len(deletable),
            'blocked_files': len(issues),
            'total_size': total_size,
            'total_size_formatted': format_bytes(total_size),
            'deletable_size': deletable_size,
            'deletable_size_formatted': format_bytes(deletable_size),
            'issues': issues
        }
