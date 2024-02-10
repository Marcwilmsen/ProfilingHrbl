# tasks.py
from celery import shared_task
import numpy as np
from warehouse_app.db_functions import get_locations, load_warehouse_layout, query_skus_with_picks_by_warehouse_profile, get_historic_results
from warehouse_app.backend_observer import Observer
import Herb_PyGAD.main as pygad
import Herb_PyGAD.testData as testData
from django.dispatch import Signal
from warehouse_project.send_message_to_frontend import send_message_to_all
from warehouse_app.models import WarehouseSolutionStartParameter, SessionLocal
from datetime import datetime
# Define the signal without providing_args
websocket_message_signal = Signal()
import logging
logger = logging.getLogger(__name__)

@shared_task
def run_algorithm(data):
        try:
                print("Starting pyGAD algorytm")
                
                # Extract parameters from data
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                generation_number = data.get('generation_number', 1000)
                percentage = int(data.get('percentage', int(99)))

                with SessionLocal() as session:
                    try:
                        start_parameter = WarehouseSolutionStartParameter(
                            number_of_generations= generation_number,
                            algo_from_date = start_date,
                            algo_too_date=  end_date,
                            percentage_to_stop=percentage,
                            day_where_algo_was_started= datetime.now()
                        )
                        session.add(start_parameter)
                        session.commit()
                    except Exception as e:
                        logging.error(
                            f"Error in query_skus_with_picks_by_warehouse_profile: {e}")
                        session.rollback()
                        raise e

                print(f"STARTING PYGAD ALGO -  Start Date: {start_date}, End Date: {end_date}, Generation Number: {generation_number}, Percentage: {percentage} ")
                send_message_to_all(f"STARTING PYGAD ALGO -  Start Date: {start_date}, End Date: {end_date}, Generation Number: {generation_number}, Percentage: {percentage} ")

                # Load init data from database
                skus_ids, countries, picks, nbr_of_lanes_results, constraints_list = query_skus_with_picks_by_warehouse_profile(
                    'masterlist', start_date, end_date)
                locations, location_types, location_sides, unique_location_types = get_locations()
                historic_results = get_historic_results()
                warehouse_layout_skus = load_warehouse_layout("masterlist")
                # Debugging: Check the length of warehouse_layout_skus
                print(f"Length of warehouse_layout_skus: {len(warehouse_layout_skus)}")

                # Create nbr_of_lanes dictionary
                nbr_of_lanes = dict(zip(skus_ids, nbr_of_lanes_results))

                # Convert constraints list to dictionary.
                constraints = {}
                for sku_id, constraint in zip(skus_ids, constraints_list):
                    if constraint is None:
                        constraints[sku_id] = None
                    else:
                        constraints[sku_id] = constraint.split('|')

                #build countries_dict
                countries_dict = {sku_id: country_str.split(
                    '/')[:-1] for sku_id, country_str in zip(skus_ids, countries)}

                for sku_id in skus_ids:
                    if not countries_dict.get(sku_id):
                        print(f"Warning: No country data for SKU ID {sku_id}")
                        countries_dict[sku_id] = ['default_country']

                #build pick_data_dict
                pick_data_dict = dict(zip(skus_ids, picks))
                pick_data_dict[-1] = 0

                #build init_pop with last 10 solutions from database

                #because locations where 2950 and sku's only 700-900,
                # we fill the sku dict with -1 (empty) sku's so that every location can be matched to a real sku or a "-1" sku
                while len(locations) != len(skus_ids):
                    skus_ids.append(-1)

                initial_population = [warehouse_layout_skus]
                historic_lengths = set(len(historic_result) for historic_result in historic_results)
                initial_population.extend(historic_results)


                # Adjust the chromosomes to make sure all have the same length
                max_length = max(historic_lengths.union({len(warehouse_layout_skus)}))
                for chromosome in initial_population:
                    while len(chromosome) < max_length:
                        chromosome.append(-1)  # Append -1 if the chromosome is shorter
                    while len(chromosome) > max_length:
                        chromosome.pop()  # Remove the last element if the chromosome is longer


                # Debugging: Print the last element of each chromosome in initial_population
                for i, chromosome in enumerate(initial_population, start=1):
                    if chromosome:  # Ensure the chromosome is not empty
                        print(f"Chromosome {i} last element: {chromosome[-1]}")
                    else:
                        print(f"Chromosome {i} is empty")

                # Logging the lengths of initial_population elements
                for i, chromosome in enumerate(initial_population, start=1):
                    print(f"Chromosome {i} length: {len(chromosome)}")

                # Check for consistent lengths in initial_population
                if len(set(map(len, initial_population))) != 1:
                    logger.error("Not all chromosomes in the initial population have the same length.")
                    raise ValueError("Not all chromosomes in the initial population have the same length.")

                # Convert initial_population to a NumPy array and check its dimensions
                initial_population_np = np.array(initial_population)
                if initial_population_np.ndim != 2:
                    logger.error(f"Initial population is not 2D. Shape: {initial_population_np.shape}")
                    raise ValueError(f"Initial population is not 2D. Shape: {initial_population_np.shape}")

                # Ensure all elements in initial_population are of the same length
                if not all(len(chromosome) == len(initial_population_np[0]) for chromosome in initial_population):
                    logger.error("Not all chromosomes in the initial population have the same length.")
                    raise ValueError("Not all chromosomes in the initial population have the same length.")

                        
                # Only executed if not enough historic results were added
                while len(initial_population) != 10:
                    initial_population.append(warehouse_layout_skus)

                # Debugging: Print lengths of all individuals in initial population
                for i, individual in enumerate(initial_population):
                    print(f"Individual {i} length: {len(individual)}")


                # Ensure all elements in initial_population are of the same length
                if len(set(len(individual) for individual in initial_population)) > 1:
                    print("Error: Inconsistent lengths in initial population")

                backend = Observer()
                reach_str = "reach_" + str(float(percentage/100))
                print("reach_str: ", reach_str)

                pygad.run_ga(initial_population, skus_ids, locations, location_types, location_sides, unique_location_types, countries_dict, pick_data_dict, nbr_of_lanes, constraints,
                            testData.country_groups_for_area, backend, generation_number, reach_str)
                print("Algorithm execution and database update completed")


        except Exception as e:
            # Log and handle the exception
            logger.error(f"Error during algorithm execution: {e}")
            raise e

        finally:
            print("Algorithm execution completed or terminated")