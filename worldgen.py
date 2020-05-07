"""The worldgen module contains random world generation functions.
It exports the generate_world() function for the Game class __init__()
method. In the future it will be used by some other module that will
allow the user to tweak the worldgen settings from within the game.
"""
from dataclasses import dataclass
from math import sqrt, floor
import random

import cubic
import data
# from playergen import Player

layout = cubic.Layout(cubic.layout_pointy, cubic.Point(50, 50), cubic.Point(800, 550))

@dataclass
class Locality:
    name: str = ''
    category: str = ''

@dataclass
class Tile:
    """Represents the data held by a game tile

    Attributes
    ----------
    owner : Player | None
        The tile owner.
    category : str
        Tile type - i.e. water/land.
    locality: Locality | None
        Can be a City or a Capital.
    army : Army | None
        Armies can move between tiles.
    """
    owner: object = None
    category: str = 'farmland'
    locality: object = None
    army: object = None

    def __str__(self):
        if self.locality:
            string = str(self.locality.name)
        else:
            string = str(self.category)
        return string

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
    """Generates a cube:tile dict to be used as the game world map,
    identical to the original hex empire 1 world map. Returns the dict.
    """
    layout.orientation = cubic.layout_flat
    layout.origin = cubic.Point(-10, 10)
    MAP_WIDTH = 20
    MAP_HEIGHT = 11
    world_map = dict()
    q = 0
    while (q < MAP_WIDTH):
        q += 1
        q_offset = floor((q+1)/2) # or q>>1
        r = -q_offset
        while (r < MAP_HEIGHT - q_offset):
            r += 1
            world_map[(cubic.Cube(q, r, -q-r))] = Tile()
    return world_map

def shape_hexagon(map_radius):
    """Generates a cube:tile dictionary with a hexagonal shape.
    Returns the dictionary."""
    align_hex_top_left(map_radius)
    world_map = dict()
    q = -map_radius
    while q <= map_radius:
        r1 = max(-map_radius, -q - map_radius)
        r2 = min(map_radius, -q + map_radius)
        r = r1
        q += 1
        while r <= r2:
            world_map[(cubic.Cube(q, r, -q-r))] = Tile()
            r += 1
    return world_map

def choose_shape(shape, radius):
    """Shape interface"""
    if shape == 'classic': res = shape_classic()
    elif shape == 'hexagon': res = shape_hexagon(radius)
    return res

def localgen_random(empty_world):
    for tile in empty_world.values():
        if random.random() > 0.9:
            tile.locality = Locality(data.choose_random_city_name(), "City")

def localgen_random_ots(empty_world):
    """Same as localgen_random(), but ensures there is one tile of space between every locality."""
    for cube, tile in empty_world.items():
        flag = True
        if empty_world.get(cube).locality:
            flag = False
        for neighbour in cubic.get_nearest_neighbours(cube):
            if neighbour in empty_world and empty_world.get(neighbour).locality:
                flag = False
        if flag and random.random() > 0.9:
            tile.locality = Locality(data.choose_random_city_name(), "City")


def choose_localgen_algorithm(empty_world, algorithm):
    if algorithm == 'random':
        localgen_random(empty_world)
    elif algorithm == 'random_ots':
        localgen_random_ots(empty_world)

def playerspawn_classic(filled_world, players):
    """Spawn positions hardcoded to correspond to the original hex empire 1 spawn positions."""
    starting_positions = (
        cubic.Cube(2, 1, -3),
        cubic.Cube(2, 9, -11),
        cubic.Cube(19, -8, -11),
        cubic.Cube(19, 0, -19))

    for player, pos in zip(players, starting_positions):
        tile = filled_world[pos]
        tile.owner = player
        tile.locality = Locality(data.choose_random_city_name(), "Capital")
        player.starting_cube = pos

        for neighbour in cubic.get_nearest_neighbours(pos):
            tile = filled_world.get(neighbour)
            tile.owner = player

def playerspawn_random(filled_world, players):
    for player in players:
        starting_cube = random.choice(list(filled_world.keys()))
        starting_tile = filled_world.get(starting_cube)
        starting_tile.owner = player
        starting_tile.locality = Locality(data.choose_random_city_name(), "Capital")
        player.starting_cube = starting_cube

def choose_playerspawn(filled_world, players, spawntype):
    if spawntype == 'classic': playerspawn_classic(filled_world, players)
    #elif spawntype == 'maxdist': playerspawn_maxdist(filled_world, players)
    elif spawntype == 'random': playerspawn_random(filled_world, players)

def generate_world(shape, radius, algorithm, spawntype, players):
    game_world = choose_shape(shape, radius)
    choose_playerspawn(game_world, players, spawntype)
    choose_localgen_algorithm(game_world, algorithm)
    return game_world
