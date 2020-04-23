from math import floor
import random

from draw import LAYOUT
import cubic

MAP_WIDTH = 20
MAP_HEIGHT = 11
ACTIONS_PER_TURN = 5
MAX_TRAVEL_DISTANCE = 2

class AttrDict(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

# A single Game() instance houses the game world and all players.
class Game:
    def __init__(self):
        self.turn = 0
        self.players = self.initialise_players()
        self.current_player = self.players[0]
        self.world = World(self)
        self.world.generate_cities()
        self.world.add_starting_areas(self.players)

    def initialise_players(self):
        players = []
        players.append(Player(self, "Redosia", ai=False))
        players.append(Player(self, "Bluegaria"))
        players.append(Player(self, "Greenland"))
        players.append(Player(self, "Violetnam"))
        return players

    def defeat_player(self, player):
        for i in range(len(self.players)):
            if self.players[i] == player:
                del self.players[i]
                break
        print(player, "has been defeated!")

    def surrender_to_player(self, defeated_player, player):
        for tile in self.world.tiles.values():
            if (tile.owner == defeated_player):
                tile.army.manpower = 0
                tile.army.morale = 0
                tile.owner = player

    #def check_victory_condition():
    #    pass
        

class Player:
    def __init__(self, game=None, id="None", ai=True):
        self.game = game
        self.id = id
        self.ai = ai
        self.actions = ACTIONS_PER_TURN
        self.selection = None

    def __str__(self):
        return self.id

    def calc_army_growth(self):
        growth = 0
        for tile in self.game.world.tiles.values():
            if tile.owner == self: growth += 1
        return growth

    def click_on_tile(self, tilepair):
        cube, _ = tilepair
        if tilepair == self.selection:
            # deselects currently selected tile
            self.selection = None
            return 0
        
        if (self.selection != None and self.selection[1].owner == self and self.selection[1].army.manpower > 0):
            legal_moves = cubic.get_all_neighbours(self.selection[0], MAX_TRAVEL_DISTANCE)
            for coord in legal_moves:
                if cube == coord:
                    self.game.world.move_army(self.selection, tilepair)
                    # after capturing, deselects the tile clicked on.
                    self.selection = None
                    break
            else:
                # selects a different unit without having to click twice on it to deselect current selection
                self.selection = tilepair
        else:
            self.selection = tilepair


    def skip_turn(self):
        self.actions = 0


class Tile:
    def __init__(self, game):
        self.game = game
        self.owner = None #Player()
        self.structures = None
        self.army = AttrDict()
        self.army.manpower = 0
        self.army.morale = 0

    def __str__(self):
        return str(self.structures) + " " + str(self.owner) + " " + str(self.army.manpower)

    def combat_strength(self):
        diff = self.army.manpower - self.army.morale
        return self.army.manpower + diff/2

    def train_army(self):
        if self.owner != None and self.army.manpower < 100:
            if self.structures != None: self.army.manpower += 14
            elif self.structures == "Capital": self.army.manpower += 14


class Map():
    def __init__(self, game, layout=LAYOUT):
        self.map = dict()
        q = 0
        while (q < MAP_WIDTH):
            q += 1
            q_offset = floor((q+1)/2) # or q>>1
            r = -q_offset
            while (r < MAP_HEIGHT - q_offset):
                r += 1
                self.map[(cubic.Cube(q, r, -q-r))] = Tile(game)


# The game world is made of tiles. The tiles are mapped to cubic coordinates by using cubic coordinates as keys in the Map.map dictionary.
class World:
    def __init__(self, game):
        self.game = game
        self.tiles = Map(game).map
        # remove random tiles so as to add obstacles
        # for k in self.tiles.copy():
        #     if k not in starting_pos and random.random() > 0.86:
        #         self.tiles.pop(k)

    # This method will need to be coupled with map generation,
    # as to remove the need for the redundant search
    def get_tile(self, pos):
        for tile in self.tiles:
            if (tile.x == pos[0] and tile.y == pos[1]):
                return tile

    def generate_cities(self):
        for tile in self.tiles.values():
            if random.random() > 0.9:
                tile.structures = "City"

    def add_starting_areas(self, players, flag="vanilla"):
        if flag == "vanilla":
            starting_positions = (cubic.Cube(2,1,-3), cubic.Cube(2,9,-11), cubic.Cube(19, -8, -11), cubic.Cube(19,0,-19))
            for player, pos in zip(players, starting_positions):
                tile = self.tiles[pos]
                tile.owner = player
                tile.structures = "Capital"
        else:
            for player in players:
                starting_tile = random.choice(list(self.tiles.values()))
                starting_tile.owner = player
                starting_tile.structures = "Capital"

    # def expand_borders(self):
    #     for cube, tile in self.tiles.copy().items():
    #         if tile.owner.id != "None":
    #             neighbours_cubes = cubic.get_nearest_neighbours(cube)
    #             neighbours = [self.tiles.get(x) for x in neighbours_cubes if x in self.tiles]
    #             for neighbour in neighbours:
    #                 if neighbour.owner.id == "None":
    #                     neighbour.owner = tile.owner 

    def find_own_tile(self, player):
        own_tiles = []
        for cube, tile in self.tiles.items():
            if tile.owner == player and tile.army.manpower > 0:
                own_tiles.append((cube, tile))
        if len(own_tiles) <= 1:
            i = 0
        else:
            i = random.randint(0,len(own_tiles)-1)
        return own_tiles[i]

    def check_for_army(self, player):
        own_tiles = []
        for tile in self.tiles.values():
            if tile.owner == player and tile.army.manpower > 0:
                own_tiles.append(tile)
        if len(own_tiles) == 0:
            return False
        else: return True

    def move_army(self, origin, target):
        #assert isinstance(target, Tile)
        origin[1].owner.actions -= 1
        if (target[1].owner == None):
            self.capture_tile(origin, target)

        elif (target[1].owner == origin[1].owner):
            target[1].army.manpower = origin[1].army.manpower + target[1].army.manpower
            origin[1].army.manpower = 0
            self.extend_borders(origin, target)
        
        else: self.combat_system(origin, target)

    def combat_system(self, origin, target):
        print(origin[1].owner, "attacks", target[1].owner, "with", origin[1].army.manpower, "against", target[1].army.manpower)
        if origin[1].army.manpower > target[1].army.manpower:
            origin[1].army.manpower -= target[1].army.manpower
            target[1].army.manpower = 0
            self.capture_tile(origin, target)
        elif origin[1].army.manpower == target[1].army.manpower:
            origin[1].army.manpower = 0
            target[1].army.manpower = 1
        else:
            target[1].army.manpower -= origin[1].army.manpower
            origin[1].army.manpower = 0

    def capture_tile(self, origin, target):
        print(origin[1].owner, "captures", target[0], 
        "from", target[1].owner)

        #check victory condition
        if (target[1].structures == "Capital"):
            self.game.defeat_player(target[1].owner)
            self.game.surrender_to_player(target[1].owner, origin[1].owner)
        else:
            target[1].owner = origin[1].owner

        target[1].army.manpower = origin[1].army.manpower
        origin[1].army.manpower = 0

        self.extend_borders(origin, target)


    def extend_borders(self, origin, target):
        neighbours_cube = cubic.get_nearest_neighbours(target[0])
        neighbours = [self.tiles.get(x) for x in neighbours_cube if x in self.tiles]
        for neighbour in neighbours:
            if neighbour.army.manpower == 0 and neighbour.structures == None:
                neighbour.owner = origin[1].owner

    def print_world_state(self):
        for tile in self.tiles.values():
            if tile.army.manpower > 0:
                print("Tile:", tile, "army:", tile.army, "owner:", tile.owner)


def ai_controller(world, player):
    def pick_direction(number_of_directions):
        directions = []
        for _ in range(number_of_directions):
            direction = cubic.cube_direction(random.randint(0,5))
            directions.append(direction)
        return directions

    tile = world.find_own_tile(player)
    player.click_on_tile(tile)

    direction = pick_direction(2)
    target_cube = tile[0] + direction[0] + direction[1]
    while target_cube not in world.tiles:
        direction = pick_direction(2)
        target_cube = tile[0] + direction[0] + direction[1]

    tile = world.tiles.get(target_cube)
    tiles = (target_cube, tile)

    player.click_on_tile(tiles)


def run():
    turn = 0

    game = Game()
    while len(game.players) > 1:
        turn += 1
        if turn >= 100000: break
        for tile in game.world.tiles:
            tile.train_army()
        if (turn % 2 == 0):
            print("Turn:", turn)
            game.world.print_world_state()
        for player in game.players:
            player.actions = 5
            if player.ai == True:
                while player.actions > 0 and game.world.check_for_army(player):
                    ai_controller(game.world.tiles, player)
    for player in game.players:
        print(player, "wins!")