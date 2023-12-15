import logging
import random
import numpy as np

from Herb_PyGAD.fitness.zoneCutter import cut_solution_array_into_zones

logger = logging.getLogger('py_gad')


def custom_crossover(parents, offspring_size, ga_instance):
    """
        The crossover uses the parent to randomly select two zones in the pareents array.
        Then the algorithm randomly selects the number of elements to cut
        The same amount of products are cut from the end of each zone (Done so because not every zone has the same length)
        The 4 cut zones are crossed
        Zone 1 -> Zone 1.1 + Zone 1.2
        Zone 2 -> Zone 2.1 + Zone 2.2

        Children
        newZone 1 -> Zone 1.2 + Zone 2.2
        newZone 2 -> Zone 2.1 + Zone 1.2

        NewParent contains the swapped zones and is added to the array of children that is returned at the end.


        Complexity:
        O(n)

        Parameters:
        - parents ([Int]): An Array of ints representing the id of the product. The parent array is randomly selected by the GA
        - offspring_size (tuple(Amount of children, length of each child)): Only the amount of children that should be produced are interesting in this method

        Returns:
        An array of children
    """
    offspring = []

    while len(offspring) < offspring_size[0]:

        logging.debug("Parent before crossover: {}".format(parents[len(offspring)]))
        zones = cut_solution_array_into_zones(parents[len(offspring)])
        
        random_zone_idx_1 = random.randint(0,len(zones)-1)
        random_zone_idx_2 = random.randint(0,len(zones)-1)
        random_zone_1 = zones[random_zone_idx_1]
        random_zone_2 = zones[random_zone_idx_2]

        logging.debug("Zone A (before crossover): {}".format(random_zone_1))
        logging.debug("Zone A (before crossover): {}".format(random_zone_2))

        number_of_elements_to_switch = random.randint(1, len(random_zone_1)-1)
        if number_of_elements_to_switch < len(random_zone_1) and number_of_elements_to_switch < len(random_zone_2):
            start_1 = random_zone_1[:len(random_zone_1) - number_of_elements_to_switch]
            stop_1 = random_zone_1[len(random_zone_1) - number_of_elements_to_switch:]

            start_2 = random_zone_2[:len(random_zone_2) - number_of_elements_to_switch]
            stop_2 = random_zone_2[len(random_zone_2) - number_of_elements_to_switch:]

            zones[random_zone_idx_1] = np.concatenate((start_1, stop_2), axis=None)
            zones[random_zone_idx_2] = np.concatenate((start_2, stop_1), axis=None)

        logging.debug("Zone A (after crossover): {}".format(zones[random_zone_idx_1]))
        logging.debug("Zone B (after crossover): {}".format(zones[random_zone_idx_2]))
        newParent = np.concatenate(zones, axis=None)
        logging.debug("Edited parent after crossover: {}".format(newParent))

        offspring.append(newParent)
    return np.array(offspring)
