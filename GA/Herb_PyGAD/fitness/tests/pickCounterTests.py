import unittest
import numpy as np
import testData

from fitness.pickCounter import count_picks_for_country, count_picks_per_master_area_per_group, \
    get_total_picks_per_group


class PickCounterTest(unittest.TestCase):

    def setUp(self):
        self.cut_zones = [[1, 2, 3], [4, 5, 6, 7], [8, 9, 10],
                          [11, 12, 13, 14, 15],[16, 17, 18, 19, 20], [21, 22, 23],
                          [24, 25, 26, 27], [28, 29, 30, 31, 32, 33], [34, 35, 36],
                          [37, 38], [39, 40]]
        m1_Zones = np.concatenate((self.cut_zones[0], self.cut_zones[1], self.cut_zones[2]), axis=None)
        m2_Zones = np.concatenate((self.cut_zones[3], self.cut_zones[4], self.cut_zones[5]), axis=None)
        m3_Zones = np.concatenate((self.cut_zones[6], self.cut_zones[7], self.cut_zones[8]), axis=None)
        m4_Zones = np.concatenate((self.cut_zones[9], self.cut_zones[10]), axis=None)
        self.master_zones = {
            'm1': m1_Zones,
            'm2': m2_Zones,
            'm3': m3_Zones,
            'm4': m4_Zones,
        }

    def test_count_picks_for_country(self):
        count = count_picks_for_country(testData.skus, testData.country_groups_for_area[0])
        self.assertEquals(count, 9505)

    def test_count_picks_per_master_area_per_group(self):
        result = count_picks_per_master_area_per_group(self.master_zones, testData.country_groups_for_area)
        expected_result = {'m1': [2374, 4743, 0, 0], 'm2': [2340, 0, 8151, 2890], 'm3': [4791, 0, 3539, 0], 'm4': [0, 0, 2181, 0]}
        self.assertEquals(result, expected_result)

    def test_get_total_picks_per_group(self):
        input = {'m1': [2374, 4743, 0, 0], 'm2': [2340, 0, 8151, 2890], 'm3': [4791, 0, 3539, 0],
                           'm4': [0, 0, 2181, 0]}
        result = get_total_picks_per_group(input)
        expected_result = {'group1': 9505, 'group2': 4743, 'group3': 13871, 'group4': 2890}
        self.assertEquals(result, expected_result)
