import random as rn
from Models.city import createCity
from geopy.distance import great_circle
import matplotlib.pyplot as plt
import numpy as np
import math as math


rn.seed(0)


def __createRoute(cities):
    route = rn.sample(cities, len(cities))
    return route


def __initialPopulation(popSize: int, cities: dict):
    city_list = list(cities.values())
    population = [__createRoute(cities=city_list) for i in range(popSize)]
    return population


def __routeDistanceFitness(route):
    distance = 0
    for i in range(len(route)):
        start_city = route[i]
        to_city = None
        if i + 1 < len(route):
            to_city = route[i + 1]
        else:
            to_city = route[0]
        distance += great_circle(start_city, to_city).miles

    if distance > 0:
        return distance, 1 / float(distance)
    else:
        raise Exception('Route Distance can not be 0')


def __rankFitness(population):
    """
    Function to get the index of routes sorted in descending order
    :param population: list of routes
    :return: dictionary of 'fitness' and 'fitness_ranks'
    """
    fit = [__routeDistanceFitness(population[i])[1] for i in range(len(population))]
    fitness_matrix = {'fitness': sorted(fit, reverse=True), 'fitness_ranks': sorted(range(len(fit)),
                                                                                    key=lambda k: fit[k], reverse=True)}
    fitness_matrix['fitness_cumsum'] = np.cumsum(fitness_matrix['fitness'])
    return fitness_matrix


def __selection(fitnessMatrix: __rankFitness, eliteSize: int):
    selection = []

    if eliteSize > 0:
        for i in range(eliteSize):
            selection.append(fitnessMatrix['fitness_ranks'][i])

    for i in range(len(fitnessMatrix['fitness_ranks']) - eliteSize):
        select = 100 * rn.random()
        for j in range(len(fitnessMatrix['fitness_ranks'])):
            fit_score = fitnessMatrix['fitness_cumsum'][j] * 100 / sum(fitnessMatrix['fitness_cumsum'])
            if select < fit_score and fitnessMatrix['fitness_ranks'][j] not in selection:
                selection.append(fitnessMatrix['fitness_ranks'][j])
                break
    return selection


def __crossover(parentA, parentB) -> __createRoute:
    child = []
    childPA = []
    childPB = []

    geneA = int(rn.random() * len(parentA))
    geneB = int(rn.random() * len(parentB))

    start_gene = min(geneA, geneB)
    end_gene = max(geneA, geneB)

    for i in range(start_gene, end_gene):
        childPA.append(parentA[i])

    childPB = [gene for gene in parentB if gene not in childPA]
    child = childPA + childPB
    return child


def __crossoverPopulation(matingPool, eliteSize: int):
    children = []
    random_pool = rn.sample(matingPool, len(matingPool))

    if eliteSize > 0:
        for i in range(eliteSize):
            children.append(matingPool[i])
    for i in range(len(matingPool) - eliteSize):
        child = __crossover(random_pool[i], random_pool[len(matingPool) - 1 - i])
        children.append(child)

    return children


def __mutate(child, mutationRate: float):
    for swapped in range(len(child)):
        if rn.random() < mutationRate:
            swapWith = int(rn.random() * len(child))

            cityA = child[swapped]
            cityB = child[swapWith]

            child[swapped] = cityB
            child[swapWith] = cityA

    return child


def __mutatePopulation(population, mutationRate: float):
    if mutationRate > 1 or mutationRate < 0:
        raise Exception('Mutation rate should between 0 and 1')

    mutated_population = []

    for child in population:
        mutated_population.append(__mutate(child, mutationRate))

    return mutated_population


def __addNewRoutes(matingPool, popSize: int, cities):
    if len(matingPool) == popSize:
        return matingPool
    else:
        city_list = None
        if type(cities) == dict:
            city_list = list(cities.values())
        else:
            city_list = cities
        while len(matingPool) < popSize:
            matingPool.append(__createRoute(city_list))
    return matingPool


def __nextGeneration(currentPopulation, eliteSize: int, mutationRate: float,
                     cities, popSize: int):
    fitness_matrix = __rankFitness(currentPopulation)
    selected_routes = __selection(fitness_matrix, eliteSize)
    selected_pool = [currentPopulation[i] for i in selected_routes]
    mating_pool = __addNewRoutes(selected_pool, popSize, cities)
    children = __crossoverPopulation(mating_pool, eliteSize)
    next_generation = __mutatePopulation(children, mutationRate)
    return next_generation


def __getCityIndexes(cities: dict, result: list):
    route = []

    for value in result:
        val = list(cities.keys())[list(cities.values()).index(value)]
        route.append(val)
    return route


def solveGeneticAlgorithm(eliteSize: int, mutationRate: float, cities: dict, popSize: int, generations: int):
    population = __initialPopulation(popSize, cities)
    best_route = None
    best_value = math.inf
    values = []

    for i in range(generations):
        population = __nextGeneration(population, eliteSize, mutationRate, cities, popSize)
        current_value = 1 / __rankFitness(population)['fitness'][0]
        values.append(current_value)
        if current_value < best_value:
            best_route = population[__rankFitness(population)['fitness_ranks'][0]]
            best_value = current_value
    best_route_index = __getCityIndexes(cities, best_route)
    return best_route_index
