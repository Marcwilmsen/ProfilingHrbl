import random
import numpy as np
from dbConnection.postgresConnector import load_products, load_pick_data, load_locations
from Herb_PyGAD.main import run_ga

indexes, sku_mapping, countries_mapping = load_products()
locations = load_locations()
load_pick = load_pick_data('2023-08-15', '2023-08-15', sku_mapping)


def get_skus():
    """
        The SKU and the locations array have to be of the same length for the algorithm to work.
        Only the skus are shuffled by the algorithm and the locations are static.
        So we can only assign each product to a location if both arrays have the same length.
    """
    while len(indexes) != len(locations):
        indexes.append(-1)
    return indexes


skus = get_skus()


locations = np.array(locations)


countries = countries_mapping


pickdata = load_pick


country_groups_for_area = [
    ["CH", "NO"],
    ["DE"],
    ["SE", "FI"],
    ["AT", "BE", "DK", "FR", "GB", "IE", "MT", "NL"]
]

initial_pop = [skus,
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus)),
                random.sample(list(skus), len(skus))
               ]


def main():
    run_ga(initial_pop, skus, locations, countries, pickdata, country_groups_for_area)


main()