import unittest
import GA.Herb_PyGAD.fitness.fitness as fitness
import GA.Herb_PyGAD.testData as testData


class FitnessTests(unittest.TestCase):
    def test_calculate_zipzap(self):
        result = fitness.calculate_zipzap(testData.solution_cut_in_masterareas)
        print(result)

