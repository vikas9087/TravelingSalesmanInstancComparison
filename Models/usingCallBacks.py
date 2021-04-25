from Models.secFormulation import SecModel
from Models.secFormulation import buildGraph
import gurobipy as gp
from gurobipy import GRB
import Models.city as city
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

    def __init__(self, env: gp.Env, cities: city.City.cities, distances: dict, startSolution: list,
                 usingLazyConstraint: bool = False, give_initial_solution: bool = False):
        super().__init__(env, cities, distances, startSolution, give_initial_solution)
        if usingLazyConstraint:
            self.environment.setParam('LazyConstraints', 1)
        self.buildModel()

    def solve(self):
        try:
            self.tsp._vars = self.cityFromTo
            self.tsp._number_cities = len(self.cities)
            self.tsp.update()
            start_time = time.time()
            self.tsp.optimize(callBackSubTourElimination)
            solution = self.tsp.getAttr('x', self.cityFromTo)
        except gp.GurobiError as e:
            print(f'Error code: {e.errno} & string is: {str(e)}')
        except AttributeError:
            print('Encountered an attribute error')
        self.time_elapsed = time.time() - start_time
        self.optimal_gap = self.tsp.MIPGap*100
        self.tsp.dispose()