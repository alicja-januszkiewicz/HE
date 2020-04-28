import json
import random

with open("resources/cities.json", "r") as read_file:
    raw = json.load(read_file)

cities = raw['data']

CITY_NAMES = []

for city in cities:
    CITY_NAMES.append(city['asciiname'])

def choose_random_city_name():
    max = len(CITY_NAMES) - 1
    city_name = "a very very long city name that will get overwritten in the loop"
    while len(city_name) > 12:
        randint = random.randint(0,max)
        city_name = CITY_NAMES[randint]
    return city_name