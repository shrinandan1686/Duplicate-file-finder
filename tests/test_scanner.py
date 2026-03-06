import unittest
import os
import shutil
import tempfile
import json
from file_scanner import FileScanner, FileInfo

class TestFileScanner(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for scanning
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.json")
        
        # Create a dummy config
        config = {
            "supported_extensions": [".jpg", ".png"],
            "scan_options": {
                "min_file_size_bytes": 10,
                "include_hidden_folders": False
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
            
        # Create some test files
        self.sub_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.sub_dir)
        
        # Valid files
        self.file1 = os.path.join(self.test_dir, "image1.jpg")
        with open(self.file1, 'wb') as f:
            f.write(b"content for image 1" * 10)
            
        self.file2 = os.path.join(self.sub_dir, "image2.png")
        with open(self.file2, 'wb') as f:
            f.write(b"content for image 2" * 10)
            
        # Invalid: Too small
        self.small_file = os.path.join(self.test_dir, "small.jpg")
        with open(self.small_file, 'wb') as f:
            f.write(b"tiny")
            
        # Invalid: Unsupported extension
        self.txt_file = os.path.join(self.test_dir, "test.txt")
        with open(self.txt_file, 'wb') as f:
            f.write(b"text content" * 10)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scanner_discovery(self):
        scanner = FileScanner(self.config_path)
        files = scanner.scan_directories([self.test_dir])
        
        # Should find image1.jpg and image2.png
        # small.jpg is skipped (too small)
        # test.txt is skipped (wrong extension)
        self.assertEqual(len(files), 2)
        
        paths = [f.path for f in files]
        self.assertIn(self.file1, paths)
        self.assertIn(self.file2, paths)

    def test_scanner_summary(self):
        scanner = FileScanner(self.config_path)
        scanner.scan_directories([self.test_dir])
        summary = scanner.get_scan_summary()
        
        self.assertEqual(summary['files_scanned'], 2)
        self.assertEqual(summary['errors_count'], 0)

if __name__ == '__main__':
    unittest.main()
