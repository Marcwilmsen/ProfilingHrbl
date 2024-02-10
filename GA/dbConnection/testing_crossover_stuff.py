import random
import re

import numpy as np

parents = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
           [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]
offspring = []
locations = np.array(["01A01", "01B02", "01C03", "01D04", "01D05",
                      "02A01", "02B02", "02C03", "02D04", "02D06",
                      "03A01", "03B02", "03C03", "03D04", "03D05",
                      "32P3B01", "32P3B02", "32P3B03", "32P3B04", "32P3B05",
                      ])
constraints = {
    -1: [],
    1: ["01", "02"],
    2: ["01", "02"],
    3: ["01", "02"],
    4: ["01D04"],
    5: ["01", "02", "03"],
    6: ["EVEN"],
    7: ["ODD"],
    8: ["HIGHVALUE"],
    9: ["01", "02"],
    10: ["01", "02"],
    11: ["01", "02"],
    12:  ["01", "02"],
    13: ["03"],
    14:  ["01", "02"],
    15:  ["01", "02"],
    16: ["03", "04"],
    17:  ["01", "02"],
    18:  ["01", "02"],
    19: ["04"],
    20:  ["01", "02"],
}

# for i in range(1, 2):
#     solution = parents[len(offspring)].copy()
#     number_of_elements_to_switch = 5
#
#     for i in range(1, number_of_elements_to_switch):
#         idx1, idx2 = random.randint(0, len(solution) - 1), random.randint(0, len(solution) - 1)
#         product1, product2 = solution[idx1], solution[idx2]
#         print("swapping " + str(solution[idx1]) + " with " + str(solution[idx2]))
#         tmp = solution[idx1]
#         solution[idx1] = solution[idx2]
#         solution[idx2] = tmp
#         print("swapped " + str(solution[idx1]) + " with " + str(solution[idx2]))
#
#     offspring.append(solution)
# print("01D04"[2:3])
#
# print("Check for differences between offspring and parent: ")
# for i in range(0, 3):
#     for j in range(0, len(offspring[i]) - 1):
#         if offspring[i][j] != parents[i][j]:
#             print("Change detected: offspring " + str(offspring[i][j]) + " and parent " + str(parents[i][j]))


def custom_crossover_with_zone_constraint(parents, offspring_size):
    offspring = []

    while len(offspring) < offspring_size:
        solution = parents[len(offspring)].copy()
        number_of_elements_to_switch = 5

        for i in range(1, number_of_elements_to_switch):
            idx1, idx2 = random.randint(0, len(locations) - 1), random.randint(0, len(locations) - 1)
            product1, product2 = solution[idx1], solution[idx2]
            slot1, slot2 = locations[idx1], locations[idx2]

            product1_bool = product_can_be_placed_at_slot(constraints.get(product1), slot2)
            product2_bool = product_can_be_placed_at_slot(constraints.get(product2), slot1)

            if product1_bool and product2_bool:
                tmp = solution[idx1]
                solution[idx1] = solution[idx2]
                solution[idx2] = tmp

        offspring.append(solution)

    return np.array(offspring)


def product_can_be_placed_at_slot(product_constraint, destination_slot):
    if len(product_constraint)==0:
        return True

    if (check_for_zone_constraint(product_constraint, destination_slot) and
            check_for_level_constraint(product_constraint, destination_slot) and
            check_for_slot_constraint(product_constraint, destination_slot)):
        return True

    return False


def check_for_slot_constraint(product_constraint, destination_slot):
    regex_pattern = r'\d\d[A-D]\d\d'  # Regex pattern for exactly two digits
    matched_strings = find_matching_strings(regex_pattern, product_constraint)

    if (len(matched_strings) == 0):
        return True

    if (len(matched_strings) > 0):
        print(f"Found slot constraint in {product_constraint}")

    if destination_slot[0] == matched_strings[0]:
        return True
    elif destination_slot != matched_strings:
        return False

    return True


def check_for_level_constraint(product_constraint, destination_slot):
    regex_pattern = r'^[ABCD]$'  # Regex pattern for exactly one letter of A, B, C or D
    matched_strings = find_matching_strings(regex_pattern, product_constraint)
    level = find_matching_strings(regex_pattern, destination_slot)

    if (len(matched_strings) == 0):
        return True

    if (len(matched_strings) > 0):
        print(f"Found level constraint in {product_constraint}")

    if level[0] in matched_strings:
        return True
    elif level[0] not in matched_strings:
        return False

    return True


def check_for_zone_constraint(product_constraint, destination_slot):
    regex_pattern = r'^\d{2}$'  # Regex pattern for exactly two digits
    matched_strings = find_matching_strings(regex_pattern, product_constraint)

    if (len(matched_strings) == 0):
        return True

    if(len(matched_strings) > 0):
        print(f"Found zone constraint in {product_constraint}")

    if destination_slot[:2] in matched_strings:
        return True
    elif destination_slot[:2] not in matched_strings:
        return False

    return True


def find_matching_strings(regex, string_array):
    """
    Returns all strings from the string_array that match the given regex pattern.

    :param regex: A string representing the regex pattern to match against.
    :param string_array: A list of strings to be checked against the regex.
    :return: A list of strings that match the regex pattern.
    """
    pattern = re.compile(regex)
    matching_strings = [s for s in string_array if pattern.fullmatch(s)]
    return matching_strings


custom_crossover_with_zone_constraint(parents, 2)