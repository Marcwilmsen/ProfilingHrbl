import Herb_PyGAD.main
from ..testData import country_groups_for_area
import numpy as np


def get_total_picks_per_group(count_all_zones):
    """
        Using the output of the count per masterarea per group we can sum up the total count of each group.
        This is needed for calculations later on

        Complexity:
        O(n)

        Parameters:
        - count_all_zones ({}): A dictionary containing the data for each masterarea for each group
        e.g.: "M1_group1": 1234,
                ....

        Returns:
        group_picks ({}): A dictionary containing the total count of picks for each group
        e.g.: "group1": 4321,
                ....
    """
    # sum of per masterarea per group
    group_picks = {}
    for zone_name, zone_data in count_all_zones.items():
        group_number = 1
        for i in zone_data:
            key = 'group' + str(group_number)
            if key in group_picks:
                group_picks[key] = group_picks.get(key) + i
            else:
                group_picks[key] = i
            group_number += 1
        group_number = 1
    return group_picks


def count_picks_per_master_area_per_group(zones_dict, country_groups):
    """
        count_picks_per_master_area_per_group countrs the picks per masterarea per each country group.
        The picks for each masterarea for each group are counted by Count_picks_for_country.
        The result is put in a dictionary which is returned at the end

        Complexity:
        # O(n x m x s x g)

        Parameters:
        - zones_dict ({}): A dictionary containing the mastereas
        e.g.: "master_zones = {
                    'm1': [m1_Zones],
                    'm2': [m2_Zones],
                    'm3': [m3_Zones],
                    'm4': [m4_Zones],
                }"
        - country_groups ([[String]]): An Array of Strings where each String is a Shortform representing a country (Germany -> DE, Netherlands -> NL)

        Returns:
        picks_counts ({}): A dictionary containing the data for each masterarea for each group
        "M1_group1": 1234,
        ....
    """
    picks_counts = {}

    for zone_name, zone_data in zones_dict.items():
        picks_for_zone = []
        for countries in country_groups:
            count = count_picks_for_country_group(zone_data, countries)
            picks_for_zone.append(count)
        picks_counts[zone_name] = picks_for_zone

    return picks_counts


def check_matching_strings(array1, array2):
    # Convert both arrays to sets for efficient lookup
    set1 = set(array1)
    set2 = set(array2)

    # Find the intersection of the two sets
    intersection = set1.intersection(set2)

    # Check if the intersection is not empty
    return len(intersection) > 0


def count_picks_for_country_group(solution, group):
    """
        Count_picks_for_country gets a solution and a group.

        Each product in the solution is used, the belonging country is loaded and it is checked if the products country is in this group array.
        If it is the picks are added to the sum.
        When all products are checked the sum of this group picks is returned

        Complexity:
        # O(s x g)

        Parameters:
        - solution ([Int]): An Array of ints representing the id of the product. The solution can be the complete current generation of the GA or just a masterarea. It depends who calls the method.
        - group ([String]): An Array of Strings where each String is a Shortform representing a country (Germany -> DE, Netherlands -> NL)

        Returns:
        Int: The su of picks of products that belong to this country group.
    """
    total_picks = 0
    for product in solution:
        # if np.intersect1d(Herb_PyGAD.main.countries.get(product), group) > 0:
        # if Herb_PyGAD.main.countries.get(product) in group:
        if check_matching_strings(Herb_PyGAD.main.countries.get(int(product), []), group):
            total_picks += Herb_PyGAD.main.pickdata.get(product)
    return total_picks


def count_picks_per_country_per_masterarea(solution_cut_in_master_areas):
    picks_per_country_per_masterarea_dict = {}
    for masterArea_name, masterArea_data in solution_cut_in_master_areas.items():
        picks_per_country_dict = {}
        for product in masterArea_data:
            if product != -1:
                for country in Herb_PyGAD.main.countries.get(product):
                    # Initialize the country key with 0 if it doesn't exist
                    picks_per_country_dict[country] = picks_per_country_dict.get(country, 0)
                    # Add pickdata value to the country, ensuring it's an integer
                    picks_per_country_dict[country] += Herb_PyGAD.main.pickdata.get(product, 0)
        picks_per_country_per_masterarea_dict[masterArea_name] = picks_per_country_dict
    return picks_per_country_per_masterarea_dict
