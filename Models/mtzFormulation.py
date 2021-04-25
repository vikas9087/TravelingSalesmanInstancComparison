from Models.secFormulation import SecModel
import gurobipy as gp
from gurobipy import GRB
import Models.city as city
import time as time


class MtzFormulation(SecModel):
    """
    Inherit from the CreateModel class. Add additional functionalities
    """

    def __init__(self, env: gp.Env, cities: city.City.cities, distances: dict, startSolution: list,
                 usingLazyConstraint: bool = False, give_initial_solution: bool = False):
        super().__init__(env, cities, distances, startSolution, give_initial_solution)
        self.__addMtzConstraints()
        self.tsp.update()

    def __addMtzConstraints(self):
        number_cities = len(self.cities.keys())
        cityRank = self.tsp.addVars(list(range(number_cities)), vtype=GRB.INTEGER, ub=number_cities, name='cityRank')
        for i in range(1, number_cities):
            self.tsp.addConstr(cityRank[i] <= number_cities - 1)
            for j in range(1, number_cities):
                if i != j:
                    cityA = self.cities[i]
                    cityB = self.cities[j]
                    self.tsp.addConstr(
                        cityRank[i] - cityRank[j] + number_cities * self.cityFromTo[(i, j)] <= number_cities - 1)

    def solve(self):
        try:
            start_time = time.time()
            self.tsp.optimize()
        except gp.GurobiError as e:
            print(f'Error code: {e.errno} & string is: {str(e)}')
        except AttributeError:
            print('Encountered an attribute error')
        self.time_elapsed = time.time() - start_time
        self.optimal_gap = self.tsp.MIPGap*100
        solution = self.tsp.getAttr('x', self.cityFromTo)
        self.buildGraph(solution)
        self.tsp.dispose()
