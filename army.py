from dataclasses import dataclass
from math import ceil, floor

import cubic

MAX_TRAVEL_DISTANCE = 2
MAX_STACK_SIZE = 99
BASE_GROWTH_CITY = 5
BASE_GROWTH_CAPITAL = 10
BONUS_GROWTH_PER_TILE = 1

MORALE_BONUS_ANNEX_RURAL = 1
MORALE_BONUS_ANNEX_CITY_ORIGIN = 20
MORALE_BONUS_ANNEX_CITY_ALL = 10
MORALE_BONUS_ANNEX_SOVEREIGN_CAPITAL_ORIGIN = 80
MORALE_BONUS_ANNEX_SOVEREIGN_CAPITAL_ALL = 50
MORALE_PENALTY_LOSING_CITY = 10
MORALE_PENALTY_PER_MANPOWER_LOSING_BATTLE = 0.1
MORALE_PENALTY_IDLE_ARMY = 1

@dataclass
class Army:
    manpower: int = 0
    morale: int = 0
    can_move: bool = True

    def __str__(self):
        return f'{self.manpower}/{self.morale}'

def extend_borders(world_map, origin, target):
    # Find the cube key corresponding to the target tile
    for cube in world_map:
        if world_map.get(cube) == target:
            target_cube = cube
    
    # Find the nn of the target cube and expand
    neighbours_cube = cubic.get_nearest_neighbours(target_cube)
    neighbours = [world_map.get(x) for x in neighbours_cube if x in world_map]
    morale_bonus = 0
    for neighbour in neighbours:
        if not neighbour.army and neighbour.locality.type == None and neighbour.owner != origin.owner:
            neighbour.owner = origin.owner
            morale_bonus += 1

    # Apply the morale bonus
    for tile in world_map.values():
        if tile.owner == origin.owner and tile.army:
            tile.army.morale = min(tile.army.manpower, tile.army.morale + morale_bonus)

def issue_order(world_map, origin, target):
    tiles = world_map.values()
    origin.owner.actions -= 1
    if not target.army and origin.owner != target.owner:
        capture_tile(tiles, origin, target)
        target.army.can_move = False
        extend_borders(world_map, origin, target)

    elif not target.army and origin.owner == target.owner:
        move(origin, target)
        target.army.can_move = False
        extend_borders(world_map, origin, target)

    elif target.owner == origin.owner:
        if target.army.manpower < MAX_STACK_SIZE:
            regroup(origin, target)
            target.army.can_move = False
            extend_borders(world_map, origin, target)
    
    else: 
        origin.army.can_move = False
        attack(tiles, origin, target)
        if origin.owner == target.owner:
            extend_borders(world_map, origin, target)

def move(origin, target):
    target.army = origin.army
    origin.army = None

def regroup(origin, target):
    sum = origin.army.manpower + target.army.manpower
    army_over_max_stack = sum - MAX_STACK_SIZE
    if army_over_max_stack <= 0:
        target.army.manpower = sum
        if target.army.manpower > 0:
            target.army.morale = round(origin.army.morale + target.army.morale /2)
        else:
            target.army.morale = origin.army.morale
        origin.army = None
    if army_over_max_stack > 0:
        origin_morale_per_manpower = origin.army.morale / origin.army.manpower
        target.army.manpower += origin.army.manpower - army_over_max_stack
        target.army.morale = round((origin.army.morale - army_over_max_stack * origin_morale_per_manpower + target.army.morale) / 2)
        origin.army.manpower = army_over_max_stack
        origin.army.morale = round(army_over_max_stack * origin_morale_per_manpower)

def attack(tiles, origin, target):
    print(origin.owner, "attacks", target.owner, 
    "with", origin.army, "against", target.army)

    diff = origin.combat_strength() - target.combat_strength()
    combat_strength_to_army = ceil(diff/2)
    if diff > 0:
        losing_player = target.owner
        manpower_lost = target.army.manpower
        origin.army.manpower = combat_strength_to_army
        origin.army.morale = combat_strength_to_army
        target.army = None
        capture_tile(tiles, origin, target)
    elif diff == 0:
        losing_player = origin.owner
        manpower_lost = origin.army.manpower
        origin.army = None
        target.army.manpower = 1
        target.army.morale = 1
    else:
        losing_player = origin.owner
        manpower_lost = origin.army.manpower
        target.army.manpower = max(1, -combat_strength_to_army)
        target.army.morale = max(1, -combat_strength_to_army)
        origin.army = None
    
    apply_morale_penalty_losing_combat(tiles, losing_player, manpower_lost)

def calculate_minimum_morale(tiles, player):
    total_manpower = 0
    for tile in tiles:
        if tile.owner == player and tile.army:
            total_manpower += tile.army.manpower
    return floor(total_manpower / 50)

def apply_morale_penalty_losing_combat(tiles, losing_player, manpower_lost):
    penalty = floor(MORALE_PENALTY_PER_MANPOWER_LOSING_BATTLE * manpower_lost)
    print("Player", losing_player, "suffers", penalty, "morale penalty")
    for tile in tiles:
        if tile.owner == losing_player and tile.army:
            minimum_morale = min(calculate_minimum_morale(tiles, losing_player),tile.army.manpower)
            tile.army.morale = (max(minimum_morale, tile.army.morale - penalty))

def capture_tile(tiles, origin, target):
    print(origin.owner, "captures", target, "from", target.owner)

    # Apply morale bonus/penalty
    if target.locality.type == "Capital":
        origin.army.morale = min(origin.army.manpower, origin.army.morale + MORALE_BONUS_ANNEX_SOVEREIGN_CAPITAL_ORIGIN)
        for tile in tiles:
            if tile.owner == origin.owner and tile != origin and tile.army:
                tile.army.morale = min(tile.army.manpower, tile.army.morale + MORALE_BONUS_ANNEX_SOVEREIGN_CAPITAL_ALL)

    elif target.locality.type == "City":
        origin.army.morale = min(origin.army.manpower, origin.army.morale + MORALE_BONUS_ANNEX_CITY_ORIGIN)
        for tile in tiles:
            if tile.owner == origin.owner and tile != origin and tile.army:
                tile.army.morale = min(tile.army.manpower, tile.army.morale + MORALE_BONUS_ANNEX_CITY_ALL)
        if target.owner != None:
            for tile in tiles:
                if tile.owner == target.owner and tile.army:
                    tile.army.morale = round(max(calculate_minimum_morale(tiles, target.owner), tile.army.morale - MORALE_PENALTY_LOSING_CITY))

    elif target.locality.type == None:
        for tile in tiles:
            if tile.owner == origin.owner and tile.army:
                tile.army.morale = min(tile.army.manpower, tile.army.morale + MORALE_BONUS_ANNEX_RURAL)

    target.owner = origin.owner
    move(origin, target)