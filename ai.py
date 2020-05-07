"""The AI module"""
from collections import namedtuple
import operator

import army
import cubic

SCORES = {
    'farmland':1,
    'City':10,
    'Capital_satellite':15,
    'Capital':100,
    'manpower':1,
    }

TargetListElement = namedtuple("TargetListElement",
                               ["score", "origin", "target"])

def calculate_tile_capture_score(tile):
    """Calculates the base score for capturing a tile."""
    # need to implement distinguishing satelite capitals
    if tile.locality:
        score = SCORES.get(tile.locality.category)
    else:
        score = SCORES.get(tile.category)
    return score

def calculate_extended_border_score(game, cube):
    """Calculates the bonus score for capturing neighbouring tiles."""
    score = 0
    neighbours = cubic.get_nearest_neighbours(cube)
    for neighbour in neighbours:
        neighbour_tile = game.world.get(neighbour)
        if  (not cubic.is_blocked(game.world, neighbour)
             and neighbour_tile.owner != game.current_player):
            score += SCORES.get(neighbour_tile.category)
    return score

def calculate_combat_score(game, origin_cube, target_cube):
    """Calculates the combat score component."""
    origin_tile = game.world.get(origin_cube)
    target_tile = game.world.get(target_cube)
    diff = army.calculate_combat_strength(origin_tile.army) - army.calculate_combat_strength(target_tile.army)
    score = diff/10
    if diff > 0:
        score += target_tile.army.manpower/10
    else:
        score -= origin_tile.army.manpower/10
    return score

def calculate_score(game, origin_cube, target_cube):
    """Calculates and returns a score value for a move."""
    origin_tile = game.world.get(origin_cube)
    target_tile = game.world.get(target_cube)
    if target_tile.owner != game.current_player:
        if target_tile.army:
            diff = army.calculate_combat_strength(origin_tile.army) - army.calculate_combat_strength(target_tile.army)
            if diff > 0:
                score = calculate_tile_capture_score(target_tile)
                score += calculate_extended_border_score(game, target_cube)
                score += calculate_combat_score(game, origin_cube, target_cube)
            else:
                score = calculate_combat_score(game, origin_cube, target_cube)
        else:
            score = calculate_tile_capture_score(target_tile)
            score += calculate_extended_border_score(game, target_cube)
    else:
        score = calculate_extended_border_score(game, target_cube)
    return score

def is_army_likely_to_be_useful(game, army_tilepair):
    """Don't waste cycles exploring paths that aren't likely to be useful."""
    cube, tile = army_tilepair
    valid_targets = cubic.get_reachable_cubes(game.world, cube, army.MAX_TRAVEL_DISTANCE)
    for target in valid_targets:
        target_tile = game.world.get(target)
        if target_tile.owner != tile.owner:
            return True
    return False


def create_owned_armies_world_subset(game):
    """Creates a subset of the game world containing only entries with own armies."""
    world_subset = {}
    for cube, tile in game.world.items():
        if tile.army and tile.army.can_move and tile.owner == game.current_player:
            if is_army_likely_to_be_useful(game, (cube, tile)):
                world_subset[cube] = tile
    return world_subset

def explore_army_targets(game, cube):
    """Explores the scores a tile containing an army can achieve for all valid targets."""
    res = []
    # cube, tile = tilepair
    valid_targets = cubic.get_reachable_cubes(game.world, cube, army.MAX_TRAVEL_DISTANCE)
    for target in valid_targets:
        score = calculate_score(game, cube, target)
        element = TargetListElement(score, cube, target)
        res.append(element)
    return res

def create_target_list(game):
    """Score every possible valid move."""
    subset = create_owned_armies_world_subset(game)
    target_list = []
    for cube in subset:
        target_list += explore_army_targets(game, cube)
    return target_list

def generate_targets(game):
    """Based on the target list, pick generate the most optimal targets."""
    target_list = create_target_list(game)
    target_list.sort(key=operator.itemgetter(0), reverse=True)
    for target_list_element in target_list:
        yield target_list_element

def controller(game, target):
    """Attempts to calculate the most optimal move and performs the necessary
    click_on_tile() Player method calls to execute them.
    """
    origin_tile = game.world.get(target.origin)
    target_tile = game.world.get(target.target)
    tilepair_origin = (target.origin, origin_tile)
    tilepair_target = (target.target, target_tile)
    game.current_player.click_on_tile(tilepair_origin)
    game.current_player.click_on_tile(tilepair_target)

# def create_threat_list():
#     """For every hostile army in the game world, calculate the threat level."""
#     pass

# def pick_important_threats():
#     """Based on the threat list, pick 5 most dangerous threats."""
#     pass

# def pick_actions():
#     """Pick """
