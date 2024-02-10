import logging
import random
import re

import numpy as np

from . import main

# Big brain code energy gone
logger = logging.getLogger('py_gad')


def custom_crossover(parents, offspring_size, ga_instance):
    offspring = []

    while len(offspring) < offspring_size[0]:
        solution = parents[len(offspring)].copy()
        number_of_elements_to_switch = int(len(solution) / 20)

        for i in range(1, number_of_elements_to_switch):
            idx1, idx2 = random.randint(0, len(main.locations) - 1), random.randint(0, len(main.locations) - 1)
            product1, product2 = solution[idx1], solution[idx2]
            slot1, slot2 = main.locations[idx1], main.locations[idx2]

            if main.number_of_lanes.get(product1) == main.number_of_lanes.get(product1):
                product1_bool = product_can_be_placed_at_slot(main.constraints.get(product1), slot2)
                product2_bool = product_can_be_placed_at_slot(main.constraints.get(product2), slot1)

                if product1_bool and product2_bool:
                    # if slot2[:2] == "32":
                    # logger.info(f"swapped product: {product1} with constraints: {main.constraints.get(product1)} to {slot2}")
                    # if slot1[:2] == "32":
                    # logger.info(f"swapped product: {product2} with constraints: {main.constraints.get(product2)} to {slot1}")
                    tmp = solution[idx1]
                    solution[idx1] = solution[idx2]
                    solution[idx2] = tmp

        offspring.append(solution)

    return np.array(offspring)


def product_can_be_placed_at_slot(product_constraint, destination_slot):
    if product_constraint is None:
        return True

    if len(product_constraint) == 0:
        return True

    if (check_for_zone_constraint(product_constraint, destination_slot) and
            check_for_level_constraint(product_constraint, destination_slot) and
            check_for_slot_constraint(product_constraint, destination_slot) and
            check_for_even_odd_constraint(product_constraint, destination_slot) and
            check_for_location_type_constraint(product_constraint, destination_slot)):
        return True

    # if check_for_zone_constraint(product_constraint, destination_slot):
    #   return True

    return False


def check_for_slot_constraint(product_constraint, destination_slot):
    regex_pattern = r'\d\d[A-D]\d\d'  # Regex pattern for exactly two digits
    matched_strings = find_matching_strings(regex_pattern, product_constraint)

    if (len(matched_strings) == 0):
        # No slot constraint for this product
        return True

    # if (len(matched_strings) > 0):
        # logger.info(f"Found slot constraint in {product_constraint} and returned {matched_strings}")

    if destination_slot[0] == matched_strings[0]:
        return True
    elif destination_slot[0] != matched_strings[0]:
        # Destination slot NOT equal to the constraint slot. Violated constraint here
        return False

    return True


def check_for_level_constraint(product_constraint, destination_slot):
    regex_pattern = r'^[ABCD]$'  # Regex pattern for exactly one letter of A, B, C or D
    matched_strings = find_matching_strings(regex_pattern, product_constraint)
    level = find_matching_strings(regex_pattern, destination_slot)

    if (len(matched_strings) == 0 or len(level) == 0):
        # No level constraint for this product or no level found in the location (2nd should not happen)
        return True

    # if (len(matched_strings) > 0):
        # logger.info(f"Found level constraint in {product_constraint} and returned {matched_strings}")

    if level[0] in matched_strings:
        return True
    elif level[0] not in matched_strings:
        # Destination level NOT in the constraints list. Violated constraint here
        return False

    return True


def check_for_zone_constraint(product_constraint, destination_slot):
    regex_pattern = r'^\d{2}$'  # Regex pattern for exactly two digits
    matched_strings = find_matching_strings(regex_pattern, product_constraint)

    if (len(matched_strings) == 0):
        # No zone constraint for this  product
        return True

    # if (len(matched_strings) > 0):
        # logger.info(f"Found zone constraint in {product_constraint} and returned {matched_strings}")

    if destination_slot[:2] in matched_strings:
        return True
    elif destination_slot[:2] not in matched_strings:
        # Destination zone NOT in the constraints list. Violated constraint here
        return False

    return True


def check_for_even_odd_constraint(product_constraint, destination_slot):
    regex_pattern = r'\b(EVEN|ODD)\b'  # Regex pattern for the word EVEN and the word ODD
    matched_strings = find_matching_strings(regex_pattern, product_constraint)

    if (len(matched_strings) == 0):
        # No EVEN ODD constraint for this  product
        return True

    #if (len(matched_strings) > 0):
        # logger.info(f"Found even/odd constraint in {product_constraint} and returned {matched_strings}")

    if main.location_side_constraints.get(destination_slot) == matched_strings[0]:
        return True
    elif main.location_side_constraints.get(destination_slot) != matched_strings[0]:
        # EVEN/ODD constraint not in constraint list. Constraint violation here
        return False

    return True


def check_for_location_type_constraint(product_constraint, destination_slot):
    # Checks if the product has an Locationtype constraint ['FLOW' 'HIGHVALUE' 'WBS' 'WBSFLOW']
    regex_pattern = r'\b(' + '|'.join(
        main.all_unique_location_types) + r')\b'  # Regex pattern for the words from unique location types
    matched_strings = find_matching_strings(regex_pattern, product_constraint)

    if (len(matched_strings) == 0):
        # No location type constraint for this  product
        return True

    # if (len(matched_strings) > 0):
        # logger.info(f"Found type constraint in {product_constraint}")

    if main.location_type_constraints.get(destination_slot) in matched_strings:
        return True
    elif main.location_type_constraints.get(destination_slot) not in matched_strings:
        # Locationtype constraint ['FLOW' 'HIGHVALUE' 'WBS' 'WBSFLOW'] not in constraint list. Constraint violation here
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
