import random as rn
from geopy.distance import great_circle
from itertools import product

rn.seed(0)


def createCity() -> tuple:
    latitude = round(rn.uniform(-90, 90), ndigits=2)
    longitude = round(rn.uniform(-180, 180), ndigits=2)

    return latitude, longitude


class City:
    cities = {}
    pairwise_distance = {}

    def __init__(self, number_cities: int):
        self.number_cities: int = number_cities
        self.cities = {i:createCity() for i in range(number_cities)}
        self.__pairWiseDistance()

    def __pairWiseDistance(self):
        for keyA in self.cities.keys():
            for keyB in self.cities.keys():
                if keyA != keyB:
                    distance = great_circle(self.cities[keyA], self.cities[keyB]).miles
                    self.pairwise_distance[(keyA, keyB)] = round(distance, ndigits=0)
