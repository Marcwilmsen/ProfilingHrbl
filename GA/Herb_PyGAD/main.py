import json
import os
import time
import logging
import logging.handlers as handlers
from .fitness.fitness import fitness_func, calculate_zipzap
from .fitness.zoneCutter import cut_solution_in_masterAreas
from .crossover import custom_crossover
from .mutation import custom_mutation
from .dataSaver import file_exists, delete_file
from .testData import filepath
from pygad import pygad
from .observer import PyGADObserver
from .fitness.pickCounter import count_picks_per_country_per_masterarea

logger = logging.getLogger('py_gad')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

try:
    os.makedirs("./herbGA_logs")
except FileExistsError:
    pass

logHandler = handlers.RotatingFileHandler('./herbGA_logs/pygad.log', maxBytes=1000000, backupCount=2)

logHandler.setLevel(logging.DEBUG)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

if file_exists(filepath):
    delete_file(filepath)

locations = []
initial_population = []
skus = []
countries = {}
pickdata = {}
country_groups_for_area = []
pygad_observer = PyGADObserver()


def on_generation(ga_instance):
    # logger.info(f"Generation = {ga_instance.generations_completed}")
    # logger.info(f"Fitness    = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    generation = ga_instance.generations_completed
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    # pygad_observer.notify_observers(f"{dict(zip({ga_instance.generations_completed}, {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}))}")
    result_dict = {
        "result_type": "MID_result",
        "generation": generation,
        "solution": solution.tolist(),
        "locations": locations,
        "solution_fitness": solution_fitness
    }
    pygad_observer.notify_observers(result_dict)


def run_ga(initial_pop, skus_array, locations_array, countries_dict, pick_data_dict,
           country_groups_for_area_array, backend, generation = 1000):
    """
        Starts the genetic algorithm, calculates the runtime and prints the result

        :param list initial_pop: [[Int], [Int], ...] to start the genetic algorithm with a custom initial population on the first generation
        :param array skus_array: [] of all available skus. This array must have the same lenght as the locations array. Empty locations should be marked with -1.
        :param array locations_array: sorted [] of all slots in the warehouse. This array must have the same lenght as the SKU array because together these 2 arrays are a warehouse layout
        :param dict countries_dict: {} of all skus and its assigned countries
        :param dict pick_data_dict: {} of all skus and its calculated sum of picks per given timeframe
        :param array country_groups_for_area_array: [[string], [string], ...] with 1 array of country codes for each group
    """
    global locations
    global initial_population
    global skus
    global countries
    global pickdata
    global country_groups_for_area

    pygad_observer.add_observer(backend)

    initial_population = initial_pop
    skus = skus_array
    locations = locations_array
    countries = countries_dict
    pickdata = pick_data_dict
    country_groups_for_area = country_groups_for_area_array

    t1 = time.time()

    ga_instance = pygad.GA(initial_population=initial_population,
                           num_generations=generation,
                           num_parents_mating=9,
                           keep_elitism=3,
                           fitness_func=fitness_func,
                           crossover_type=custom_crossover,
                           mutation_type=custom_mutation,
                           on_generation=on_generation,
                           parallel_processing=None)

    ga_instance.run()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    # logger.info("Parameters of the best solution : {solution}".format(solution=solution))
    # logger.info("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    master_areas = cut_solution_in_masterAreas(solution)
    zipzap, distribution_per_zone_per_country = calculate_zipzap(master_areas)
    result_dict = {
        "result_type": "FINAL_result",
        "solution": solution.tolist(),
        "locations": locations,
        "solution_fitness": solution_fitness,
        "zipzap": zipzap,
        "distribution_per_zone_per_country": distribution_per_zone_per_country,
        "distribution_per_country": count_picks_per_country_per_masterarea(master_areas)
    }
    pygad_observer.notify_observers(result_dict)

    t2 = time.time()
    print("Time is", t2 - t1)

    # ga_instance.plot_fitness().savefig("gen_vs_fit-graph")

    delete_file(filepath)