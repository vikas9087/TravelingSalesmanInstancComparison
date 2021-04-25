import gurobipy as gp
from gurobipy import GRB
import Models.city as city
import networkx as nx
import time
import matplotlib.pyplot as plt


def buildGraph(cities: city.City.cities, solution, show_graph = False) -> nx.Graph:
    var_dict = {}
    for sol in solution:
        if solution[sol] >= 1 - 1e-6:
            var_dict[sol] = solution[sol]

    # Build a graph
    graph = nx.Graph()
    # add nodes to graph
    for i in range(len(cities)):
        graph.add_node(i, pos=cities[i])
    # add edges
    for key in var_dict:
        graph.add_edge(key[0], key[1])
    if show_graph:
        nx.draw(graph, node_size=20, pos=nx.spring_layout(graph), )
        plt.show()
    return graph


class SecModel:
    sec_constraints: int = 0

    def __init__(self, env: gp.Env, cities: city.City.cities, distances: dict, start_solution: list,
                 give_initial_solution: bool = False):
        self.tsp: gp.Model() = None
        self.cityFromTo: gp.Env = None
        self.cities: city.City.cities = None
        self.distances: {} = None
        self.indexes = None
        self.optimal_gap: float = None
        self.time_elapsed: float = None
        self.environment = env
        self.cities = cities
        self.distances = distances
        self.indexes = list(self.distances.keys())
        self.initialSolution = start_solution
        self.buildModel()
        if give_initial_solution:
            self.__giveInitialSolution()

    def buildModel(self):
        model_name = 'SEC_Cities-' + str(len(self.cities))
        self.tsp = gp.Model(env=self.environment, name=model_name)
        self.cityFromTo = self.tsp.addVars(self.indexes, vtype=GRB.BINARY, name='cityFromTo')
        if self.initialSolution:
            self.__giveInitialSolution()
        # add constraints:
        for cityA in self.cities:
            self.tsp.addConstr(gp.quicksum(
                self.cityFromTo[(cityA, cityB)] for cityB in self.cities if (cityA, cityB) in self.indexes) == 1)
            self.tsp.addConstr(gp.quicksum(
                self.cityFromTo[(cityB, cityA)] for cityB in self.cities if (cityA, cityB) in self.indexes) == 1)

        self.tsp.setObjective(gp.quicksum(self.cityFromTo[key] * self.distances[key] for key in self.indexes),
                              GRB.MINIMIZE)

    def extractTour(self, solution) -> city.City.cities:
        """
        Helps in retrieving the tsp tour.
        :param solution: value of decision variables with index as (cityA, cityB), will have value 1 if we go from A to B
        :return:
        """
        # start from 1st city
        tour = [self.cities[0]]
        current_city = self.cities[0]

        while True:
            for indexer in self.indexes:
                if indexer[0] == current_city and solution[indexer] >= 1 - 1e-6:
                    # found the next city
                    tour.append(indexer[1])
                    solution[indexer] = 0
                    current_city = indexer[1]

            if current_city == self.cities[0]:
                break

        return tour

    def __addSecConstraint(self, solution) -> bool:
        graph = buildGraph(self.cities, solution)
        number_connected_nodes = nx.number_connected_components(graph)

        if number_connected_nodes == 1:
            return True
        else:
            connect_components = nx.connected_components(graph)
            # add SEC constraint
            for nodes in connect_components:
                self.tsp.addConstr(gp.quicksum(self.cityFromTo[cityA, cityB] for cityA in nodes for cityB in nodes if
                                               (cityA, cityB) in self.indexes or (cityB, cityA) in self.indexes) <= len(
                    nodes) - 1)
                self.sec_constraints += 1

    def __giveInitialSolution(self):
        for i in range(len(self.initialSolution)):
            start = self.initialSolution[i]
            if i + 1 < len(self.initialSolution):
                end = self.initialSolution[i + 1]
            else:
                end = self.initialSolution[0]
            self.cityFromTo[(start, end)].start = 1

    def solve(self) -> object:
        self.tsp.update()
        start_time = time.time()
        while True:
            self.tsp.optimize()
            solution = self.tsp.getAttr('x', self.cityFromTo)
            if self.__addSecConstraint(solution):
                break
        self.time_elapsed = time.time() - start_time
        self.optimal_gap = self.tsp.MIPGap*100
        self.tsp.dispose()
