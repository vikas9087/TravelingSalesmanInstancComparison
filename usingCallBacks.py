from secFormulation import SecModel
import gurobipy as gp
from gurobipy import GRB
import city as city
import networkx as nx
import time as time


def callBackSubTourElimination(model, where):
    if where == GRB.Callback.MIPSOL:
        solution = model.cbGetSolution(model._vars)
        selected_edges = extractTours(solution)
        if len(selected_edges) < model._number_cities:
            # add subtour elimination constraint
            model.cbLazy(gp.quicksum(model._vars[edge] for edge in selected_edges) <= len(selected_edges) - 1)


def extractTours(solution):
    selected_edges = []
    for sol in solution:
        if solution[sol] >= 1 - 1e-6:
            selected_edges.append(sol)
    tour_edges = []
    origin_city = selected_edges[0][0]
    nextCity = selected_edges[0][1]
    tour_edges.append(selected_edges[0])
    del selected_edges[0]
    for edge in selected_edges:
        startCity = edge[0]
        if startCity == nextCity:
            nextCity = edge[1]
            tour_edges.append(edge)
            continue
        elif startCity == origin_city:
            break

    return tour_edges


class CallBackModel(SecModel):
    """
    Inherit from the CreateModel class. Add additional functionalities
    """

    def __init__(self, env: gp.Env, cities: city.City.cities, distances: dict, startSoltution: list,
                 usingLazyConstraint: bool = False, giveInitialSolution: bool = False):
        super().__init__(env, cities, distances, startSoltution, giveInitialSolution)
        if usingLazyConstraint:
            self.environment.setParam('LazyConstraints', 1)
        self.buildModel()

    # def buildModel(self):
    #     model_name = 'SEC_Cities-' + str(len(self.cities))
    #     tsp = gp.Model(env=self.environment, name=model_name)
    #     cityFromTo = tsp.addVars(self.indexes, vtype=GRB.BINARY, name='cityFromTo')
    #     self.cityFromTo = cityFromTo
    #     # add constraints:
    #     for cityA in self.cities:
    #         tsp.addConstr(gp.quicksum(
    #             cityFromTo[(cityA, cityB)] for cityB in self.cities if (cityA, cityB) in self.indexes) == 1)
    #         tsp.addConstr(gp.quicksum(
    #             cityFromTo[(cityB, cityA)] for cityB in self.cities if (cityA, cityB) in self.indexes) == 1)
    #
    #     tsp.setObjective(gp.quicksum(cityFromTo[key] * self.distances[key] for key in self.indexes), GRB.MINIMIZE)
    #
    #     self.tsp = tsp
    #
    # def __giveInitialSolution(self):
    #     for i in self.initialSoltution:
    #         start = i
    #         if i+1 < len(self.initialSoltution):
    #             end = i+1
    #         else:
    #             end = self.initialSoltution[0]
    #         self.cityFromTo[(i,i+1)].start = 1

    def solve(self):
        print('Solution Approach: Gurobi Callbacks')
        try:
            self.tsp._vars = self.cityFromTo
            self.tsp._number_cities = len(self.cities)
            self.tsp.update()
            start_time = time.time()
            self.tsp.optimize(callBackSubTourElimination)
        except gp.GurobiError as e:
            print(f'Error code: {e.errno} & string is: {str(e)}')
        except AttributeError:
            print('Encountered an attribute error')
        self.time_elapsed = time.time() - start_time
        self.total_distance = self.tsp.objVal
        solution = self.tsp.getAttr('x', self.cityFromTo)
        self.tsp.dispose()
        self.environment.dispose()
