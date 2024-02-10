import logging
import numpy as np
from .. import dataSaver as datasaver, testData

logger = logging.getLogger('py_gad')


# O(n)
def find_zone_start_end_indexes(locations):
    if datasaver.file_exists(testData.filepath):
        return datasaver.load_file(testData.filepath)

    zone_Id_letter = []
    prev_value = ""
    count = 0
    indexes = []
    for i in locations:
        value = i[:2]
        if value != prev_value:
            zone_Id_letter.append(value)
            indexes.append(count)

        prev_value = value
        count += 1

    datasaver.save_file(testData.filepath, indexes)
    logger.debug("Indexes to save: {}".format(indexes))
    logger.debug("Zonecutter count: {}".format(count))
    return indexes


# O(n x k)
def cut_solution_array_into_zones(solution, locations):
    solution_in_zones = []
    zone_index = find_zone_start_end_indexes(locations)

    for index, start in enumerate(zone_index):
        if index < len(zone_index) - 1:
            solution_in_zones.append(solution[start:zone_index[index + 1]])
        else:
            solution_in_zones.append(solution[start:])

    return solution_in_zones


def cut_locations_array_into_zones(locations):
    location_zones = []
    zone_index = find_zone_start_end_indexes(locations)

    for index, start in enumerate(zone_index):
        if index < len(zone_index) - 1:
            location_zones.append(locations[start:zone_index[index + 1]])
        else:
            location_zones.append(locations[start:])

    return location_zones


# Chromosome format: [M1-Zones, M2-Zones, M3-Zones, M4-Zones]
def cut_solution_in_masterAreas(solution, locations):
    solution_int = np.array(solution).astype(int)
    zone_1, zone_2, zone_3, zone_4, zone_5, zone_6, zone_7, zone_8, zone_9, zone_10, zone_11, zone_12 = cut_solution_array_into_zones(solution_int, locations)

    m1_Zones = np.concatenate((zone_1, zone_2, zone_3), axis=None)
    m2_Zones = np.concatenate((zone_4, zone_5), axis=None)
    m3_Zones = np.concatenate((zone_6, zone_7, zone_8), axis=None)
    m4_Zones = np.concatenate((zone_9, zone_10, zone_11, zone_12), axis=None)

    # Count the picks per masterarea per group
    master_zones = {
        'm1': m1_Zones,
        'm2': m2_Zones,
        'm3': m3_Zones,
        'm4': m4_Zones,
    }

    return master_zones