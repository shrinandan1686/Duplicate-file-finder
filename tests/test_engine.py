import unittest
import os
import shutil
import tempfile
from file_scanner import FileInfo
from deduplication_engine import DeduplicationEngine, DuplicateGroup

class TestDeduplicationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DeduplicationEngine()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_mock_file(self, name, content):
        path = os.path.join(self.test_dir, name)
        with open(path, 'wb') as f:
            f.write(content)
        return FileInfo(
            path=path,
            size=len(content),
            extension=os.path.splitext(name)[1],
            resolution=(100, 100),
            created_time=1000,
            modified_time=1000
        )

    def test_find_exact_duplicates(self):
        # Create 2 sets of exact duplicates
        f1 = self.create_mock_file("a1.jpg", b"content A")
        f2 = self.create_mock_file("a2.jpg", b"content A")
        
        f3 = self.create_mock_file("b1.png", b"content B")
        f4 = self.create_mock_file("b2.png", b"content B")
        
        f5 = self.create_mock_file("unique.jpg", b"unique content")
        
        files = [f1, f2, f3, f4, f5]
        groups = self.engine.find_duplicates(files, use_perceptual=False)
        
        # Should find 2 groups
        self.assertEqual(len(groups), 2)
        
        # Verify group contents
        group_sizes = sorted([len(g.files) for g in groups])
        self.assertEqual(group_sizes, [2, 2])

    def test_duplicate_group_waste_calculation(self):
        f1 = self.create_mock_file("a1.jpg", b"12345") # 5 bytes
        f2 = self.create_mock_file("a2.jpg", b"12345")
        f3 = self.create_mock_file("a3.jpg", b"12345")
        
        group = DuplicateGroup(files=[f1, f2, f3], detection_method="exact")
        # Total size = 15, Kept = 5, Wasted = 10
        self.assertEqual(group.get_total_wasted_space(), 10)

if __name__ == '__main__':
    unittest.main()
