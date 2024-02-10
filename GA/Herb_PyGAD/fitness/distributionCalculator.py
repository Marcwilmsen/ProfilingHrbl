import logging

logger = logging.getLogger("py_gad")


def calculate_distribution_per_zone(count_all_zones, total_picks_group1, total_picks_group2, total_picks_group3,
                                    total_picks_group4):
    """
        Helper method to prepare the data.
        Returns the result of calculate_distribution below.

        Complexity:
        O(1)

        Parameters:
        - count_all_zones ({}): A dictionary containing the data for each masterarea for each group
        e.g.: {
            'm1': [250, 50, 0, 0],
            'm2': [0, 175, 0, 0],
            'm3': [0, 50, 225, 0],
            'm4': [0, 0, 25, 250]
        }

        - total_picks_group1 - total_picks_group4 (Int): The sum of picks of this group

        Returns:
        The output of the method below:
        country_per_zone_distribution
        e.g. {'m1_group1': 1.0, 'm1_group2': 0.18181818181818182, 'm1_group3': 0, 'm1_group4': 0, 'm2_group1': 0, 'm2_group2': 0.6363636363636364, 'm2_group3': 0, 'm2_group4': 0, 'm3_group1': 0, 'm3_group2': 0.18181818181818182, 'm3_group3': 0.9, 'm3_group4': 0, 'm4_group1': 0, 'm4_group2': 0, 'm4_group3': 0.1, 'm4_group4': 1.0}
    """
    total_picks_area_group = {
        'm1_group1': count_all_zones.get("m1")[0], 'm1_group2': count_all_zones.get("m1")[1],
        'm1_group3': count_all_zones.get("m1")[2], 'm1_group4': count_all_zones.get("m1")[3],
        'm2_group1': count_all_zones.get("m2")[0], 'm2_group2': count_all_zones.get("m2")[1],
        'm2_group3': count_all_zones.get("m2")[2], 'm2_group4': count_all_zones.get("m2")[3],
        'm3_group1': count_all_zones.get("m3")[0], 'm3_group2': count_all_zones.get("m3")[1],
        'm3_group3': count_all_zones.get("m3")[2], 'm3_group4': count_all_zones.get("m3")[3],
        'm4_group1': count_all_zones.get("m4")[0], 'm4_group2': count_all_zones.get("m4")[1],
        'm4_group3': count_all_zones.get("m4")[2], 'm4_group4': count_all_zones.get("m4")[3],
    }

    total_picks_group = {
        'group1': total_picks_group1, 'group2': total_picks_group2, 'group3': total_picks_group3,
        'group4': total_picks_group4
    }

    country_per_zone_distribution = calculate_distribution(total_picks_area_group, total_picks_group)
    logger.debug("country_per_zone_distribution: {}".format(country_per_zone_distribution))
    return country_per_zone_distribution


def calculate_distribution(total_picks_area_group, total_picks_group):
    """
        Dividing the total picks per group by the picks per group per masterarea to get the percentage split of this masterarea.

        Complexity:
        # O(n)

        Parameters:
        All parameters can be looked up in the method above

        Returns:
        A dictionary containing the percentage cut of the picks per masterarea per group from the total picks per group
    """
    current_distribution = {}
    for master_area_with_group, picks in total_picks_area_group.items():
        master_area, group = master_area_with_group.split('_')
        if picks != 0 and total_picks_group[group] != 0:
            current_distribution[master_area_with_group] = picks / total_picks_group[group]
        else:
            current_distribution[master_area_with_group] = 0

    return current_distribution
