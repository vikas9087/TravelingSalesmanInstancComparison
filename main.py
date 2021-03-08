from city import City
import gurobipy as gp
from secFormulation import SecModel
import geneticAlgorithm as ga
from usingCallBacks import CallBackModel


gurobi_env = gp.Env(empty=False)
gurobi_env.setParam('MIPGap', 0.10)
gurobi_env.setParam('OutputFlag', 0)

city = City(number_cities=400)
cities = city.cities
distance = city.pairwise_distance
# startSolution = ga.solveGeneticAlgorithm(eliteSize=25, mutationRate=0.1, cities=cities, popSize=50, generations=100)

tsp_mode = SecModel(gurobi_env, cities, distance, None)
tsp_mode.solve()
print(f'Optimal Solution is :{tsp_mode.total_distance}')
print(f'Total elapsed time: {tsp_mode.time_elapsed}')
