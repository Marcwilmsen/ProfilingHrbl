import unittest
import numpy as np
import os.path
from ..zoneCutter import cut_solution_array_into_zones, save_file, file_exists, load_file, delete_file
import testData


class ZoneCutterTest(unittest.TestCase):
    def setUp(self):
        self.cut_zones = [[1, 2, 3], [4, 5, 6, 7], [8, 9, 10], [11, 12, 13, 14, 15],
                          [16, 17, 18, 19, 20], [21, 22, 23], [24, 25, 26, 27],
                          [28, 29, 30, 31, 32, 33], [34, 35, 36], [37, 38], [39, 40]]
        self.indexes = [0, 3, 7, 10, 15, 20, 23, 27, 33, 36, 38]
        self.filepath = "test"

    def tearDown(self):
        try:
            if os.path.isfile(self.filepath + ".npy"):
                os.remove("./test.npy")
            if os.path.isfile("zones.npy"):
                os.remove("./zones.npy")
        except OSError as e:
            print("Failed with:", e.strerror)
            print("Error code:", e.code)

    def test_cut_zones(self):
        zones = cut_solution_array_into_zones(testData.skus)
        for zone, expected_value in zip(zones, self.cut_zones):
            np.testing.assert_array_equal(zone, expected_value)

    def test_save_file(self):
        save_file(self.filepath, self.indexes)
        self.assertTrue(os.path.isfile(self.filepath + ".npy"))

    def test_file_exists(self):
        np.save(self.filepath, self.indexes)
        self.assertTrue(file_exists(self.filepath,))

    def test_load_file(self):
        np.save(self.filepath, self.indexes)
        self.assertTrue(os.path.isfile(self.filepath + ".npy"))
        data = load_file(self.filepath,)
        np.testing.assert_array_equal(self.indexes, data)

    def test_delete_file(self):
        np.save(self.filepath, self.indexes)
        self.assertTrue(os.path.isfile(self.filepath + ".npy"))
        delete_file(self.filepath,)
        self.assertFalse(os.path.isfile(self.filepath + ".npy"))