import unittest
import os, shutil
import numpy as np
import GA.Herb_PyGAD.fitness.zoneCutter as zoneCutter
import GA.Herb_PyGAD.testData as testData


class ZoneCutterTest(unittest.TestCase):
    def setUp(self):
        self.filepathWithFolder = "./herbGA_cache/zones"

    def tearDown(self):
        try:
            if os.path.exists(self.filepathWithFolder + ".npy"):
                shutil.rmtree("herbGA_cache")
            if os.path.exists("herbGA_logs"):
                shutil.rmtree("herbGA_logs")
        except OSError as e:
            print("Failed with:", e.strerror)

    def test_cut_zones(self):
        solution = zoneCutter.cut_solution_in_masterAreas(testData.skus, testData.locations)
        for name, masterarea in solution.items():
            self.assertTrue(np.array_equal(masterarea, testData.solution_cut_in_masterareas.get(name)))