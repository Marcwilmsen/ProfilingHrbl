import os
import time
import logging
import logging.handlers as handlers
from . import fitness, dataSaver, testData
from .crossover import custom_crossover
from .fitness import zoneCutter, pickCounter
from .fitness.fitness import fitness_func, calculate_zipzap
from pygad import pygad
from .observer import PyGADObservable

logger = logging.getLogger('py_gad')
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

try:
    os.makedirs("./herbGA_logs")
except FileExistsError:
    pass

logHandler = handlers.RotatingFileHandler('./herbGA_logs/pygad.log', maxBytes=1000000, backupCount=2)

logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
# logger.addHandler(logHandler)

if dataSaver.file_exists(testData.filepath):
    dataSaver.delete_file(testData.filepath)

locations = []
location_type_constraints = {}
location_side_constraints = {}
all_unique_location_types = []
initial_population = []
skus = []
countries = {}
pickdata = {}
country_groups_for_area = []
pygad_observer = PyGADObservable()
constraints = {}
number_of_lanes = {}
number_of_generations = 0

last_fitness = 0
def on_generation(ga_instance):
    global last_fitness
    #print(f"Generation = {ga_instance.generations_completed}")
    #print(f"Fitness    = {ga_instance.best_solution()[1]}")
    print(f"Fitness change in gen {ga_instance.generations_completed}     = {ga_instance.best_solution()[1] - last_fitness}")
    last_fitness = ga_instance.best_solution()[1]
    generation = ga_instance.generations_completed
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    result_dict = {
        "result_type": "MID_result",
        "generation": generation,
        "max_generations": number_of_generations,
        "progess_in_percent": float(generation/number_of_generations*100),
        "solution": solution.tolist(),
        "locations": locations,
        "solution_fitness": solution_fitness
    }
    pygad_observer.notify_observers(result_dict)


def run_ga(initial_pop, skus_array, locations_array, location_types, location_sides, unique_location_types,
           countries_dict, pick_data_dict, nbr_of_lanes_dict, constraints_dict,
           country_groups_for_area_array, backend, generation=1000, stop_percentage="reach_0.99"):
    """
        Starts the genetic algorithm, calculates the runtime and prints the result

        :param list initial_pop: [[Int], [Int], ...] to start the genetic algorithm with a custom initial population on the first generation
        :param array skus_array: [] of all available skus. This array must have the same lenght as the locations array. Empty locations should be marked with -1.
        :param array locations_array: sorted [] of all slots in the warehouse. This array must have the same lenght as the SKU array because together these 2 arrays are a warehouse layout
        :param dict location_types: {} of all locations and its type
        :param dict location_sides: {} of all locations and its side
        :param array unique_location_types: [] of all unique location types
        :param dict countries_dict: {} of all skus and its assigned countries
        :param dict pick_data_dict: {} of all skus and its calculated sum of picks per given timeframe
        :param dict nbr_of_lanes_dict: {} of all skus and its number of lanes
        :param dict constraints_dict: {} of all skus and its constraints as array
        :param dict country_groups_for_area_array: 2D-Array contains the country distibution for each group
        :param observable backend: The observer from the backend
        :param int generation: Specifies the number of generations for the pygad (default is set to 1000)
        :param str stop_percentage: Exit criteria to stop the algorithm early when a certain fitness is reached (default is set to 99%)
    """
    global locations, location_type_constraints, location_side_constraints, all_unique_location_types, \
        initial_population, skus, countries, pickdata, country_groups_for_area, constraints, number_of_lanes, number_of_generations

    pygad_observer.add_observer(backend)

    initial_population = initial_pop
    skus = skus_array
    locations = locations_array
    location_type_constraints = location_types
    location_side_constraints = location_sides
    all_unique_location_types = unique_location_types
    countries = countries_dict
    pickdata = pick_data_dict
    country_groups_for_area = country_groups_for_area_array
    constraints = constraints_dict
    number_of_lanes = nbr_of_lanes_dict
    number_of_generations = generation

    t1 = time.time()

    ga_instance = pygad.GA(initial_population=initial_population,
                           num_generations=generation,
                           num_parents_mating=5,
                           keep_elitism=5,
                           fitness_func=fitness_func,
                           crossover_type=custom_crossover,
                           mutation_type=None,
                           stop_criteria=stop_percentage,
                           on_generation=on_generation,
                           parallel_processing=None)

    ga_instance.run()

    t2 = time.time()
    print("Time is", t2 - t1)

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    # logger.info("Parameters of the best solution : {solution}".format(solution=solution))
    # logger.info("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    master_areas = zoneCutter.cut_solution_in_masterAreas(solution, locations)
    zipzap, distribution_per_zone_per_country = calculate_zipzap(master_areas)
    result_dict = {
        "result_type": "FINAL_result",
        "solution": solution.tolist(),
        "locations": locations,
        "solution_fitness": solution_fitness,
        "zipzap": zipzap,
        "distribution_per_zone_per_country": distribution_per_zone_per_country,
        "distribution_per_country": pickCounter.count_picks_per_country_per_masterarea(master_areas, countries, pickdata)
    }
    pygad_observer.notify_observers(result_dict)

    # ga_instance.plot_fitness().savefig("gen_vs_fit-graph")

    dataSaver.delete_file(testData.filepath)