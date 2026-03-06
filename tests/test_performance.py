import unittest
import time
import os
import shutil
import tempfile
from file_scanner import FileScanner
from deduplication_engine import DeduplicationEngine
from logger import get_logger

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.logger = get_logger()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_large_scan_performance(self):
        """Simulate a scan of 1000 files and measure performance."""
        # Create 1000 small files
        for i in range(1000):
            with open(os.path.join(self.test_dir, f"file_{i}.jpg"), 'wb') as f:
                f.write(b"content" * 10)
        
        scanner = FileScanner()
        
        start_time = time.time()
        files = scanner.scan_directories([self.test_dir])
        end_time = time.time()
        
        duration = end_time - start_time
        self.logger.info(f"BENCHMARK - Scanned 1000 files in {duration:.4f} seconds")
        
        # Performance expectation: 1000 small files should be scanned very quickly (under 2 seconds)
        self.assertLess(duration, 2.0, "Scan performance too slow")

    def test_deduplication_performance(self):
        """Simulate deduplication of 100 files with some duplicates."""
        files = []
        for i in range(100):
            path = os.path.join(self.test_dir, f"dup_{i}.jpg")
            # Create pairs of duplicates
            content = f"content_{i // 2}".encode()
            with open(path, 'wb') as f:
                f.write(content)
            
            from file_scanner import FileInfo
            files.append(FileInfo(
                path=path,
                size=len(content),
                extension=".jpg",
                resolution=(100, 100),
                created_time=time.time(),
                modified_time=time.time()
            ))
            
        engine = DeduplicationEngine()
        
        start_time = time.time()
        groups = engine.find_duplicates(files, use_perceptual=False)
        end_time = time.time()
        
        duration = end_time - start_time
        self.logger.info(f"BENCHMARK - Deduplicated 100 files in {duration:.4f} seconds")
        
        self.assertEqual(len(groups), 50) # 100 files, 50 pairs
        # Performance expectation: 100 files should be processed quickly (under 1 second)
        self.assertLess(duration, 1.0, "Deduplication performance too slow")

if __name__ == '__main__':
    unittest.main()
