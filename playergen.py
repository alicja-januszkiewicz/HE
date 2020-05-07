"""Provides the Player class and functions for random
player generation, to be used in a future settings module."""
from collections import namedtuple
import random

import army
import cubic
import camera

ACTIONS_PER_TURN = 5

ColorRGB = namedtuple("ColorRGB", ["r", "g", "b"])

RED = ColorRGB(255, 0, 0)
GREEN = ColorRGB(0, 255, 0)
BLUE = ColorRGB(0, 0, 255)
MAGENTA = ColorRGB(255, 0, 255)

class Player:
    """The player class.

    Players interact with the game by clicking on tiles and issuing
    commands to the corresponding armies."""
    def __init__(self, game=None, name="None", color=None, ai=True):
        self.game = game
        self.camera = None
        self.name = name
        self.ai = ai
        self.actions = ACTIONS_PER_TURN
        self.selection = None
        self.starting_cube = None
        self.color = color
        self.is_defeated = False

    def __str__(self):
        return self.name

    def calc_army_growth(self):
        """Calculates the army growth rate based on tiles controlled."""
        growth = 0
        for tile in self.game.world.values():
            if tile.owner == self:
                growth += 1
        return growth

    def click_on_tile(self, tilepair):
        """
        Clicking on a tile with an army selects it. If the player
        already has a selection, it will issue a command with the
        clicked tile as the target of the command. If no command can
        be issued, and the clicked tile has an army, it will be
        selected. If it does not, the player's selection will be set
        to None. Clicking on the selected tile deselects it.
        """
        clicked_cube, clicked_tile = tilepair
        is_clicked_tile_selectable = (
            clicked_tile.army
            and clicked_tile.owner == self.game.current_player
            and clicked_tile.army.can_move
            and tilepair != self.selection
            )
        if self.selection:
            legal_moves = cubic.get_reachable_cubes(self.game.world, self.selection[0], army.MAX_TRAVEL_DISTANCE)
            if clicked_cube in legal_moves:
                army.issue_order(self.game.world, self.selection, tilepair)
                self.game.check_victory_condition()
                self.selection = None # deselect
            elif is_clicked_tile_selectable:
                self.selection = tilepair
            else: self.selection = None
        elif is_clicked_tile_selectable:
            self.selection = tilepair
        else:
            self.selection = None

    def skip_turn(self):
        self.actions = 0

# if (tile.owner == None):
#     color = 0xFFAAAAAA
# elif (tile.owner.name == "Redosia"):
#     color = 0x660000FF
# elif (tile.owner.name == "Bluegaria"):
#     color = 0x66d0e040
# elif (tile.owner.name == "Greenland"):
#     color = 0x6600FF00
# elif (tile.owner.name == "Violetnam"):
#     color = 0x66800080

def set_color(tile):
    if tile.owner is None:
        color = ColorRGB(255, 255, 255)
    else:
        color = tile.owner.color
    return color

def random_color():
    levels = range(0, 256)
    color = ColorRGB(random.choice(levels), random.choice(levels), random.choice(levels))
    return color

def random_player(game):
    player = Player(game, "unnamed player", random_color())
    return player

def classic(game):
    """Hex Empire 1 players."""
    players = []
    players.append(Player(game, "Redosia", ColorRGB(255, 102, 102), ai=False))
    players.append(Player(game, "Bluegaria", ColorRGB(51, 204, 204)))
    players.append(Player(game, "Greenland", ColorRGB(102, 255, 102)))
    players.append(Player(game, "Violetnam", ColorRGB(128, 0, 128)))
    return players

def maxdist(game, number_of_players):
    """Spawn players maximum distance apart."""
    # Generate random players
    players = []
    for _ in range(number_of_players):
        players.append(random_player(game))

    # Find n points maximum distance apart
    #
    # Create a bounding box
    max_q, max_r, max_s = 0, 0, 0
    for cube in game.world:
        max_q = max(max_q, cube.q)
        max_r = max(max_r, cube.q)
        max_s = max(max_s, cube.q)
        min_q = min(min_q, cube.q)
        min_r = min(min_r, cube.r)
        min_s = min(min_s, cube.s)

def create_player_cameras(game):
    for player in game.players:
        player.camera = camera.Camera(game.initial_layout, game.world)
