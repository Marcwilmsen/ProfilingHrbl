import unittest
import GA.Herb_PyGAD.testData as testData
import GA.Herb_PyGAD.fitness.pickCounter as pickCounter


class PickCounterTest(unittest.TestCase):

    def test_count_picks_per_master_area_per_group(self):
        result = pickCounter.count_picks_per_master_area_per_group(testData.solution_cut_in_masterareas, testData.country_groups_for_area, testData.countries, testData.pickdata)
        print(result)
        for name, count in result.items():
            self.assertEquals(count, testData.picks_per_master_area.get(name))

    def test_get_total_picks_per_group(self):
        result = pickCounter.get_total_picks_per_group(testData.picks_per_master_area)
        print(result)
        for name, count in result.items():
            self.assertEquals(count, testData.total_picks_per_group.get(name))

    def test_count_picks_per_country_per_masterarea(self):
        result = pickCounter.count_picks_per_country_per_masterarea(testData.solution_cut_in_masterareas, testData.countries, testData.pickdata)
        print(result)
        for name, count in result.items():
            self.assertEquals(count, testData.count_picks_per_country_per_masterarea.get(name))