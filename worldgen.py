from math import sqrt, floor
import random

import cubic
import data
import camera
layout = camera.get_layout()

class AttrDict(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

class Tile:
    def __init__(self):
        self.owner = None
        self.type = 'farmland'
        self.locality = AttrDict()
        self.locality.type = None
        self.locality.name = None
        self.army = None

    def __str__(self):
        if self.locality.name:
            string = str(self.locality.name)
        else:
            string = str(self.type)
        return string

    def combat_strength(self):
        return self.army.manpower + self.army.morale

def align_hex_top_left(radius):
    # R = Layout.size
    # r = cos30 R = sqrt(3)/2 R
    factor = sqrt(3)/2
    r = cubic.Point(layout.size.x * factor, layout.size.y * factor)
    R = cubic.Point(layout.size.x, layout.size.y)
    if layout.orientation == cubic.layout_pointy:
        x = (2 * r.x * radius) - r.x
        # every 4 tiles skip one R
        y = (2 * R.y * radius) - (2 * R.y * radius/4) + R.y
    else:
        y = (2 * r.y * radius)
        # every 4 tiles skip one R
        x = (2 * R.x * radius) - (2 * R.x * radius/4) -R.x/2
    layout.origin = cubic.Point(x,y)

def shape_classic():
    layout.orientation = cubic.layout_flat
    layout.origin = cubic.Point(-10,10)
    MAP_WIDTH = 20
    MAP_HEIGHT = 11
    map = dict()
    q = 0
    while (q < MAP_WIDTH):
        q += 1
        q_offset = floor((q+1)/2) # or q>>1
        r = -q_offset
        while (r < MAP_HEIGHT - q_offset):
            r += 1
            map[(cubic.Cube(q, r, -q-r))] = Tile()
    return map

def shape_hexagon(map_radius):
    align_hex_top_left(map_radius)
    map = dict()
    q = -map_radius
    while q <= map_radius:
        r1 = max(-map_radius, -q - map_radius)
        r2 = min(map_radius, -q + map_radius)
        r = r1
        q += 1
        while r <= r2:
            map[(cubic.Cube(q, r, -q-r))] = Tile()
            r += 1
    return map

def choose_shape(shape, radius):
    if shape == 'classic': res = shape_classic()
    elif shape == 'hexagon': res = shape_hexagon(radius)
    return res

def localgen_random(empty_world):
    for tile in empty_world.values():
        if random.random() > 0.9:
            tile.locality.type = "City"
            tile.locality.name = data.choose_random_city_name()

def localgen_random_ots(empty_world):
    """Ensures there is a one tile of space between every locality"""
    for cube, tile in empty_world.items():
        flag = True
        for neighbour in cubic.get_nearest_neighbours(cube):
            if neighbour in empty_world and empty_world.get(neighbour).locality.type:
                flag = False
        if flag and random.random() > 0.9:
            tile.locality.type = "City"
            tile.locality.name = data.choose_random_city_name()

def choose_localgen_algorithm(empty_world, algorithm):
    if algorithm == 'random': localgen_random(empty_world)
    elif algorithm == 'random_ots': localgen_random_ots(empty_world)

def playerspawn_classic(filled_world, players):
    starting_positions = (cubic.Cube(2,1,-3), cubic.Cube(2,9,-11), cubic.Cube(19, -8, -11), cubic.Cube(19,0,-19))
    for player, pos in zip(players, starting_positions):
        tile = filled_world[pos]
        tile.owner = player
        tile.locality.type = "Capital"
        tile.locality.name = data.choose_random_city_name()
        player.starting_cube = pos

        for neighbour in cubic.get_nearest_neighbours(pos):
            tile = filled_world.get(neighbour)
            tile.owner = player

def playerspawn_random(filled_world, players):
    for player in players:
        starting_cube = random.choice(list(filled_world.keys()))
        starting_tile = filled_world.get(starting_cube)
        starting_tile.owner = player
        starting_tile.locality.type = "Capital"
        starting_tile.locality.name = data.choose_random_city_name()
        player.starting_cube = starting_cube

def choose_playerspawn(filled_world, players, spawntype):
    if spawntype == 'classic': playerspawn_classic(filled_world, players)
    #elif spawntype == 'maxdist': playerspawn_maxdist(filled_world, players)
    elif spawntype == 'random': playerspawn_random(filled_world, players)

def worldgen(shape, radius, algorithm, spawntype, players):
    game_world = choose_shape(shape, radius)
    choose_localgen_algorithm(game_world, algorithm)
    choose_playerspawn(game_world, players, spawntype)
    return game_world