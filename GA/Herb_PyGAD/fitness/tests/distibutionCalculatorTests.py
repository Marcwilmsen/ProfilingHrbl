import unittest
import GA.Herb_PyGAD.fitness.distributionCalculator as distributionCalculator
import GA.Herb_PyGAD.testData as testData

class DistributionCalculatorTests(unittest.TestCase):

    def test_calculate_distribution_per_zone(self):
        result= distributionCalculator.calculate_distribution_per_zone(testData.picks_per_master_area,
                                                                       testData.total_picks_per_group.get("group1"),
                                                                       testData.total_picks_per_group.get("group2"),
                                                                       testData.total_picks_per_group.get("group3"),
                                                                       testData.total_picks_per_group.get("group4"))
        print(result)
        for name, count in result.items():
            self.assertEquals(count, testData.distribution_per_zone.get(name))

