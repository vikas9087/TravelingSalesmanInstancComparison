import gurobipy as gp
from gurobipy import GRB
import city as city
import networkx as nx
import matplotlib.pyplot as plt
import time


class SecModel:

    sec_constraints: int = 0

    def __init__(self, env: gp.Env, cities: city.City.cities, distances: dict, startSoltution:list,
                 giveInitialSolution:bool = False):
        self.tsp: gp.Model() = None
        self.cityFromTo: gp.Env = None
        self.variables: gp.Var
        self.cities: city.City.cities = None
        self.distances: {} = None
        self.indexes = None
        self.total_distance: float = None
        self.time_elapsed: float = None
        self.environment = env
        self.cities = cities
        self.distances = distances
        self.indexes = list(self.distances.keys())
        self.initialSoltution = startSoltution
        print('Started building Model')
        self.buildModel()
        print('Model is Built')

    def buildModel(self):
        model_name = 'SEC_Cities-' + str(len(self.cities))
        tsp = gp.Model(env=self.environment, name=model_name)
        cityFromTo = tsp.addVars(self.indexes, vtype=GRB.BINARY, name='cityFromTo')
        self.cityFromTo = cityFromTo
        if self.initialSoltution:
            self.__giveInitialSolution()
        # add constraints:
        for cityA in self.cities:
            tsp.addConstr(gp.quicksum(
                cityFromTo[(cityA, cityB)] for cityB in self.cities if (cityA, cityB) in self.indexes) == 1)
            tsp.addConstr(gp.quicksum(
                cityFromTo[(cityB, cityA)] for cityB in self.cities if (cityA, cityB) in self.indexes) == 1)

        tsp.setObjective(gp.quicksum(cityFromTo[key] * self.distances[key] for key in self.indexes), GRB.MINIMIZE)

        self.tsp = tsp

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

    def __buildGraph(self, solution) -> nx.Graph:
        var_dict = {}
        for sol in solution:
            if solution[sol] >= 1 - 1e-6:
                var_dict[sol] = solution[sol]

        # Build a graph
        graph = nx.Graph()
        # add nodes to graph
        for i in range(len(self.cities)):
            graph.add_node(i, pos=self.cities[i])
        # add edges
        for key in var_dict:
            graph.add_edge(key[0], key[1])

        nx.draw(graph, node_size=20, pos=nx.spring_layout(graph), )
        plt.show()
        return graph

    def __addSecConstraint(self, solution) -> bool:
        graph = self.__buildGraph(solution)
        number_connected_nodes = nx.number_connected_components(graph)

        if number_connected_nodes == 1:
            return True
        else:
            print(f'Number of Sub tours: {number_connected_nodes-1}')
            connect_components = nx.connected_components(graph)
            # add SEC constraint
            for nodes in connect_components:
                self.tsp.addConstr(gp.quicksum(self.cityFromTo[cityA, cityB] for cityA in nodes for cityB in nodes if (cityA, cityB) in self.indexes or (cityB, cityA) in self.indexes) <= len(nodes)-1)
                self.sec_constraints += 1

    def __giveInitialSolution(self):
        for i in self.initialSoltution:
            start = i
            if i+1 < len(self.initialSoltution):
                end = i+1
            else:
                end = self.initialSoltution[0]
            self.cityFromTo[(i,i+1)].start = 1

    def solve(self):
        self.tsp.update()
        start_time = time.time()
        print('#' * 80)
        while True:
            self.tsp.optimize()
            solution = self.tsp.getAttr('x', self.cityFromTo)
            if self.__addSecConstraint(solution):
                break
        self.time_elapsed = time.time() - start_time
        self.total_distance = self.tsp.objVal
        print('#'*80)