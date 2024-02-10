import os, shutil
import unittest
import numpy as np
import GA.Herb_PyGAD.dataSaver as dataSaver


class DataSaverTests(unittest.TestCase):
    def setUp(self):
        self.filepathWithFolder = "./herbGA_cache/test"
        self.filepathWithoutFolder = "test"
        self.indexes = [0, 3, 7, 10, 15, 20, 23, 27, 33, 36, 38]

    def tearDown(self):
        try:
            if os.path.isfile(self.filepathWithFolder + ".npy"):
                shutil.rmtree("herbGA_cache")
            if os.path.isfile(self.filepathWithoutFolder + ".npy"):
                os.remove("test.npy")
        except OSError as e:
            print("Failed with:", e.strerror)

    def test_save_file(self):
        dataSaver.save_file(self.filepathWithFolder, self.indexes)
        self.assertTrue(os.path.isfile(self.filepathWithFolder + ".npy"))

    def test_file_exists(self):
        np.save(self.filepathWithoutFolder, self.indexes)
        self.assertTrue(dataSaver.file_exists(self.filepathWithoutFolder))

    def test_load_file(self):
        np.save(self.filepathWithoutFolder, self.indexes)
        self.assertTrue(os.path.isfile(self.filepathWithoutFolder + ".npy"))
        data = dataSaver.load_file(self.filepathWithoutFolder,)
        np.testing.assert_array_equal(self.indexes, data)

    def test_delete_file(self):
        np.save(self.filepathWithoutFolder, self.indexes)
        self.assertTrue(os.path.isfile(self.filepathWithoutFolder + ".npy"))
        dataSaver.delete_file(self.filepathWithoutFolder)
        self.assertFalse(os.path.isfile(self.filepathWithoutFolder + ".npy"))

