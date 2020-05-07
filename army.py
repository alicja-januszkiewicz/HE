"""The army module describes the logic of the army dataclass.
The only function it exports for external use is the issue_order()
function, which provides the Player class with a high level logic
for interacting with the game world. Some other modules might also
need to import some of the constants or the army dataclass itself.
"""
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
    """The army dataclass.

    Players interact with the game world by issuing commands to tiles containing an army,
    effectively moving armies across tiles.
    """
    manpower: int = 0
    morale: int = 0
    owner: object = None
    can_move: bool = True

    def __str__(self):
        return f'{self.manpower}/{self.morale}'

def extend_borders(world_map, origin_tile, target_cube):
    """Sets the owner of the nearest neighbours (NN) of the target tile,
    to the owner of the origin tile, subject to conditions.

    Conditions: The NN tile does not contain any armies or localities,
    and does not already belong to origin.owner.
    """
    # Find the NN of the target cube
    neighbours_cube = cubic.get_nearest_neighbours(target_cube)
    neighbours_tile = [world_map.get(x) for x in neighbours_cube if x in world_map]

    morale_bonus = 0
    # Check the conditions and if satisfied, change the ownership
    for neighbour in neighbours_tile:
        if not neighbour.army and not neighbour.locality and neighbour.owner != origin_tile.owner:
            neighbour.owner = origin_tile.owner
            morale_bonus += 1

    # Apply the morale bonus
    for tile in world_map.values():
        if tile.owner == origin_tile.owner and tile.army:
            tile.army.morale = min(tile.army.manpower, tile.army.morale + morale_bonus)

def issue_order(world, origin, target):
    """Issues an appropriate order to the origin tile,
    with the target tile as the order target.

    This function is called from within the Player.click_on_tile() method,
    and the order to be issued is determined based on the following conditions:
    move() - the target tile has no army and belongs to the origin tile owner.
    capture_tile() - the target tile has no army.
    regroup() - the target tile has an allied army.
    attack() - the target tile has a hostile army.
    """
    _, origin_tile = origin
    target_cube, target_tile = target
    world_tiles = world.values()
    origin_tile.owner.actions -= 1
    if not target_tile.army and origin_tile.owner != target_tile.owner:
        capture_tile(world_tiles, origin_tile, target_tile)
        extend_borders(world, origin_tile, target_cube)

    elif not target_tile.army and origin_tile.owner == target_tile.owner:
        move(origin_tile, target_tile)
        extend_borders(world, origin_tile, target_cube)

    elif target_tile.owner == origin_tile.owner:
        if target_tile.army.manpower < MAX_STACK_SIZE:
            regroup(origin_tile, target_tile)
            extend_borders(world, origin_tile, target_cube)

    else:
        attack(world_tiles, origin_tile, target_tile)
        if origin_tile.owner == target_tile.owner:
            extend_borders(world, origin_tile, target_cube)

def move(origin, target):
    """Moves the origin tile army to the target tile."""
    target.army = origin.army
    target.army.can_move = False
    origin.army = None

def regroup(origin, target):
    """Combines the origin tile army with an allied target tile army."""
    total_manpower = origin.army.manpower + target.army.manpower
    army_over_max_stack = total_manpower - MAX_STACK_SIZE
    if army_over_max_stack <= 0:
        target.army.manpower = total_manpower
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
    target.army.can_move = False

def attack(game_world_tiles, origin, target):
    """Attacks the target tile from the origin tile."""
    print(origin.owner, "attacks", target.owner,
          "with", origin.army, "against", target.army)

    origin.army.can_move = False

    diff = calculate_combat_strength(origin.army) - calculate_combat_strength(target.army)
    combat_strength_to_army = ceil(diff/2)
    if diff > 0:
        losing_player = target.owner
        manpower_lost = target.army.manpower
        origin.army.manpower = combat_strength_to_army
        origin.army.morale = combat_strength_to_army
        target.army = None
        capture_tile(game_world_tiles, origin, target)
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

    apply_morale_penalty_losing_combat(game_world_tiles, losing_player, manpower_lost)

def calculate_combat_strength(army):
    """Calculates the combat strength of an army oject."""
    return army.manpower + army.morale

def calculate_minimum_morale(game_world_tiles, army):
    """Calculates the minimum morale value an army can have."""
    total_manpower = 0
    for tile in game_world_tiles:
        if tile.army and tile.owner == army.owner:
            total_manpower += tile.army.manpower
    minimum_value = floor(total_manpower / 50)
    return min(army.manpower, minimum_value)

def apply_morale_penalty_losing_combat(game_world_tiles, losing_player, manpower_lost):
    """Calculates and applies the morale penalty to every army of the losing player."""
    penalty = floor(MORALE_PENALTY_PER_MANPOWER_LOSING_BATTLE * manpower_lost)
    print("Player", losing_player, "suffers", penalty, "morale penalty")
    for tile in game_world_tiles:
        if tile.owner == losing_player and tile.army:
            minimum_morale = calculate_minimum_morale(game_world_tiles, tile.army)
            tile.army.morale = (max(minimum_morale, tile.army.morale - penalty))

def capture_tile(game_world_tiles, origin, target):
    """Change the owner of the target tile to that of the origin tile,
    and apply appropriate morale modifiers to the owners of those tiles."""
    print(origin.owner, "captures", target, "from", target.owner)

    # Apply morale bonus/penalty
    if target.locality:
        if target.locality.category == "Capital":
            origin.army.morale = min(origin.army.manpower, origin.army.morale + MORALE_BONUS_ANNEX_SOVEREIGN_CAPITAL_ORIGIN)
            for tile in game_world_tiles:
                if tile.owner == origin.owner and tile != origin and tile.army:
                    tile.army.morale = min(tile.army.manpower, tile.army.morale + MORALE_BONUS_ANNEX_SOVEREIGN_CAPITAL_ALL)

        elif target.locality.category == "City":
            origin.army.morale = min(origin.army.manpower, origin.army.morale + MORALE_BONUS_ANNEX_CITY_ORIGIN)
            for tile in game_world_tiles:
                if tile.owner == origin.owner and tile != origin and tile.army:
                    tile.army.morale = min(tile.army.manpower, tile.army.morale + MORALE_BONUS_ANNEX_CITY_ALL)
            if target.owner:
                for tile in game_world_tiles:
                    if tile.owner == target.owner and tile.army:
                        tile.army.morale = round(max(calculate_minimum_morale(game_world_tiles, tile.army), tile.army.morale - MORALE_PENALTY_LOSING_CITY))
    elif target.category == 'farmland':
        for tile in game_world_tiles:
            if tile.owner == origin.owner and tile.army:
                tile.army.morale = min(tile.army.manpower, tile.army.morale + MORALE_BONUS_ANNEX_RURAL)

    target.owner = origin.owner
    move(origin, target)
