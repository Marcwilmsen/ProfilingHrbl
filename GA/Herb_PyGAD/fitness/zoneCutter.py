import logging
import Herb_PyGAD.main
import numpy as np
from Herb_PyGAD.dataSaver import save_file, file_exists, load_file
from Herb_PyGAD.testData import filepath

logger = logging.getLogger('py_gad')


# O(n)
def find_zone_start_end_indexes():
    if file_exists(filepath):
        return load_file(filepath)

    zone_Id_letter = []
    prev_value = ""
    count = 0
    indexes = []
    for i in Herb_PyGAD.main.locations:
        value = i[:2]
        if value != prev_value:
            zone_Id_letter.append(value)
            indexes.append(count)

        prev_value = value
        count += 1



    save_file(filepath, indexes)
    logger.debug("Indexes to save: {}".format(indexes))
    logger.debug("Zonecutter count: {}".format(count))
    return indexes


# O(n x k)
def cut_solution_array_into_zones(solution):
    zones = []
    zone_index = find_zone_start_end_indexes()

    for index, start in enumerate(zone_index):
        if index < len(zone_index) - 1:
            zones.append(solution[start:zone_index[index + 1]])
        else:
            zones.append(solution[start:])

    return zones


# Chromosome format: [M1-Zones, M2-Zones, M3-Zones, M4-Zones]
def cut_solution_in_masterAreas(solution):
    solution_int = np.array(solution).astype(int)
    zone_1, zone_2, zone_3, zone_4, zone_5, zone_6, zone_7, zone_8, zone_9, zone_10, zone_11, zone_12 = cut_solution_array_into_zones(solution_int)

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