import unittest
import os
import shutil
import tempfile
from PIL import Image
from utils import format_bytes, get_image_resolution, is_system_folder, compute_file_hash, get_file_times

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_format_bytes(self):
        self.assertEqual(format_bytes(500), "500.00 B")
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1024 * 1024), "1.00 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024), "1.00 GB")

    def test_get_image_resolution(self):
        img_path = os.path.join(self.test_dir, "test.png")
        img = Image.new('RGB', (100, 200), color='red')
        img.save(img_path)
        
        resolution = get_image_resolution(img_path)
        self.assertEqual(resolution, (100, 200))

    def test_is_system_folder(self):
        self.assertTrue(is_system_folder("C:/Windows"))
        self.assertTrue(is_system_folder("C:/$Recycle.Bin"))
        self.assertTrue(is_system_folder(".git"))
        self.assertFalse(is_system_folder("C:/Users/Documents/Photos"))

    def test_compute_file_hash(self):
        file_path = os.path.join(self.test_dir, "test.txt")
        content = b"Hello World"
        with open(file_path, 'wb') as f:
            f.write(content)
        
        hash1 = compute_file_hash(file_path)
        self.assertIsNotNone(hash1)
        
        # Verify same content gives same hash
        hash2 = compute_file_hash(file_path)
        self.assertEqual(hash1, hash2)

    def test_get_file_times(self):
        file_path = os.path.join(self.test_dir, "time_test.txt")
        with open(file_path, 'w') as f:
            f.write("test")
        
        ctime, mtime = get_file_times(file_path)
        self.assertGreater(ctime, 0)
        self.assertGreater(mtime, 0)

if __name__ == '__main__':
    unittest.main()
