import random
from deap import base, creator, tools, algorithms

def evalCargo(individual, boat, cargo_options):
    """
    Evaluate an individual's fitness.

    The individual is a binary list indicating whether to load each cargo item.
    If the total weight or space exceeds the boat's limits, a fitness of 0 is returned.
    Otherwise, fitness is computed as the sum of (cargo.value_per_unit * cargo.weight).

    Returns:
        A tuple containing the total value.
    """
    total_weight = 0
    total_space = 0
    total_value = 0
    for gene, cargo in zip(individual, cargo_options):
        if gene:
            total_weight += cargo.weight
            total_space += cargo.space_required
            total_value += cargo.value_per_unit * cargo.weight  # Adjust the value function as needed.
    if total_weight > boat.max_weight or total_space > boat.max_space:
        return 0,
    return total_value,


def optimize_cargo(boat, cargo_options, population_size=50, generations=100, cxpb=0.5, mutpb=0.2):
    """
    Use DEAP's genetic algorithm to optimize the cargo load for a given boat.

    :param boat: An instance of Boat.
    :param cargo_options: A list of Cargo instances.
    :param population_size: Size of the population.
    :param generations: Number of generations to run the algorithm.
    :param cxpb: Crossover probability.
    :param mutpb: Mutation probability.
    :return: A tuple (best_individual, best_fitness).
    """
    n = len(cargo_options)

    # Create the fitness and individual classes (if not already created).
    try:
        creator.FitnessMax
    except AttributeError:
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    try:
        creator.Individual
    except AttributeError:
        creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    # Attribute generator: random 0 or 1 for each cargo option.
    toolbox.register("attr_bool", random.randint, 0, 1)

    # Structure initializer: define an individual and population.
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Register the evaluation, crossover, mutation, and selection functions.
    toolbox.register("evaluate", evalCargo, boat=boat, cargo_options=cargo_options)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Create an initial population.
    pop = toolbox.population(n=population_size)

    # Use a Hall of Fame to keep track of the best solution.
    hof = tools.HallOfFame(1)

    # Run the genetic algorithm.
    algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=generations,
                        halloffame=hof, verbose=False)

    best = hof[0]
    best_fitness = evalCargo(best, boat, cargo_options)[0]

    return best, best_fitness


def load_optimal_cargo(boat, cargo_options):
    """
    Use the genetic algorithm to select the optimal set of cargo items and load them onto the boat.

    :param boat: An instance of Boat.
    :param cargo_options: A list of Cargo instances.
    :return: The boat with the selected cargo loaded.
    """
    best_individual, best_value = optimize_cargo(boat, cargo_options)
    print("Optimal cargo load value:", best_value)

    # Load the cargo items as indicated by the best individual.
    for gene, cargo in zip(best_individual, cargo_options):
        if gene == 1:
            boat.load_cargo(cargo)
    return boat


# if __name__ == "__main__":
#     # Example usage:
#     boat = Boat("Panama Express", max_weight=10000, max_space=500)
#
#     # Define available cargo options.
#     cargo_options = [
#         Cargo("Container A", value_per_unit=100, weight=2000, space_required=150, category="Container"),
#         Cargo("Container B", value_per_unit=150, weight=3000, space_required=200, category="Container"),
#         Cargo("Bulk Cargo", value_per_unit=50, weight=6000, space_required=250, category="Bulk"),
#     ]
#
#     # Optimize cargo loading and apply the result to the boat.
#     optimized_boat = load_optimal_cargo(boat, cargo_options)
#
#     print("\nFinal cargo loaded on the boat:")
#     for cargo in optimized_boat.cargo_list:
#         print(cargo)
