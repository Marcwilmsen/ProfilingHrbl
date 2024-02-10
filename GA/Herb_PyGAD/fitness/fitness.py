import logging

from . import zoneCutter, pickCounter, distributionCalculator
from .. import main

logger = logging.getLogger('py_gad')
# Define the desired distribution percentages
desired_distribution = [0.35, 0.35, 0.35, 0.35,
                        0.35, 0.35, 0.35, 0.35,
                        0.25, 0.25, 0.25, 0.25,
                        0.05, 0.05, 0.05, 0.05
                        ]


def fitness_func(ga_generation, solution, solution_idx):
    """
        Calculate the fitness of a given solution based on its distribution across zones.

        The fitness is determined by how well the solution distributes across the specified zones.
        The chromosome format is represented as [M1-Zones, M2-Zones, M3-Zones, M4-Zones, ...].

        Complexity:
        O(m×s×g)
        - m: Represents the size of the country_groups list or an iterable related to groups of countries.
        - s: Represents the size of the solution list or a similar list representing the solution data.
        - g: Represents the average size of the countries list or set within certain loops.

        Parameters:
        - solution ([Int]): An Array of ints representing the id of the product. The solution is the current generation of the GA.

        Returns:
        float: A value between 0 and 1 that shows the accuracy of the solution by comparing the dired distribution to the actual calculated distribution.
    """
    # Extract the distribution from the chromosome
    master_zones = zoneCutter.cut_solution_in_masterAreas(solution, main.locations)

    ziperino, distribution_per_zone_per_country = calculate_zipzap(master_zones)
    fitness = sum([abs(desired - current) for desired, current in ziperino])

    logger.debug("fitness: {}".format(fitness))
    logger.debug("fitness return: {}".format(1 / (1 + fitness)))
    # Return the fitness value (higher is better)
    return 1 / (1 + fitness)


def calculate_zipzap(master_zones):
    count_all_zones = pickCounter.count_picks_per_master_area_per_group(master_zones, main.country_groups_for_area, main.countries, main.pickdata)
    logger.debug("count all zones: {}".format(count_all_zones))

    # Count total picks per group accross all areas
    total_picks_groups = pickCounter.get_total_picks_per_group(count_all_zones)

    # Calculate the current distribution percentages
    distribution_per_zone_per_country = distributionCalculator.calculate_distribution_per_zone(count_all_zones,
                                                                        total_picks_groups.get("group1"),
                                                                        total_picks_groups.get("group2"),
                                                                        total_picks_groups.get("group3"),
                                                                        total_picks_groups.get("group4"))

    # Calculate the absolute difference between current and desired distribution
    # zipzap = zip(desired_distribution, distribution_per_zone_per_country.values())
    # logger.info("zipzap: {}".format(list(zipzap)))

    return zip(desired_distribution, distribution_per_zone_per_country.values()), distribution_per_zone_per_country
