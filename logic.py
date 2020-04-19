from math import floor
import random

from draw import LAYOUT
import cube

MAP_WIDTH = 30
MAP_HEIGHT = 15
ACTIONS_PER_TURN = 5
MAX_TRAVEL_DISTANCE = 2

#LAYOUT = cube.Layout(cube.layout_flat, cube.Point(40,40), cube.Point(0,0))

# Every game object lives in a single Game() instance.
class Game:
    def __init__(self):
        self.turn = 0
        self.players = []
        self.world = []
        # self.event_queue = []

    def initialise(self):
        self.players = self.initialise_players()
        self.world = World(self)

        for player in self.players:
            player.selection = (cube.Cube(24,0,-24), self.world.tiles[cube.Cube(24,0,-24)]) #self.world.tiles[cube.Cube(24,0,-24)]
            #print(player.selection)
            
        self.world.generate_cities()
        self.world.add_starting_areas(self.players)

    def initialise_players(self):
        players = []
        players.append(Player(self, "Redosia", ai=True))
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
                tile.units = 0
                tile.owner = player

class Player:
    def __init__(self, game=None, id="None", ai=True):
        self.game = game
        self.id = id
        self.ai = ai
        self.actions = ACTIONS_PER_TURN
        self.selection = None

    def __str__(self):
        return self.id

    def click_on_tile(self, tile):
        attack_condition = self.selection[1].owner == self and self.selection[1].units != 0
        if (attack_condition):
            legal_moves = cube.get_all_neighbours(self.selection[0], MAX_TRAVEL_DISTANCE)
            for coord in legal_moves:
                if tile[0] == coord:
                    self.game.world.move_units(self.selection, tile)
                    break
            self.selection = tile
        else:
            self.selection = tile


class Tile:
    def __init__(self, game):
        self.game = game
        self.owner = None #Player()
        self.structures = None
        self.units = 0

    def __str__(self):
        return str(self.structures) + " " + str(self.owner) + " " + str(self.units)


    def generate_units(self):
        if self.owner != None and self.units < 100:
            if self.structures != None: self.units += 14
            elif self.structures == "Capital": self.units += 14


class Map():
    def __init__(self, game, layout=LAYOUT):
        self.map = dict()
        # for r in range(MAP_HEIGHT):
        #     r_offset = floor(r/2) # or r>>1
        #     q = -r_offset
        #     while q < MAP_WIDTH - r_offset:
        #         q += 1
        #         self.map[cube.Cube(q, r, -q-r)] = Tile(game)

        q = 0
        while (q < MAP_WIDTH):
            q += 1
            q_offset = floor((q+1)/2) # or q>>1
            r = -q_offset
            while (r < MAP_HEIGHT - q_offset):
                r += 1
                self.map[(cube.Cube(q, r, -q-r))] = Tile(game)

        # s = 0
        # while (s < MAP_WIDTH):
        #     s += 1
        #     s_offset = floor((s+1)/2) # or q>>1
        #     r = -s_offset
        #     while (r < MAP_HEIGHT - s_offset):
        #         r += 1
        #         self.map[(cube.Cube(-s-r, r, s))] = Tile(game)


# The game world is made of tiles. The tiles are mapped to cubic coordinates by using cubic coordinates as keys in the Map.map dictionary.
class World:
    def __init__(self, game):
        self.game = game
        self.tiles = Map(game).map

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

    def add_starting_areas(self, players):
        for player in players:
            starting_tile = random.choice(list(self.tiles.values()))
            starting_tile.owner = player
            starting_tile.structures = "Capital"
            #player.selection = starting_tile

    # def expand_borders(self):
    #     for cube_, tile in self.tiles.copy().items():
    #         if tile.owner.id != "None":
    #             neighbours_cubes = cube.get_nearest_neighbours(cube_)
    #             neighbours = [self.tiles.get(x) for x in neighbours_cubes if x in self.tiles]
    #             for neighbour in neighbours:
    #                 if neighbour.owner.id == "None":
    #                     neighbour.owner = tile.owner 

    def find_own_tile(self, player):
        own_tiles = []
        for cube, tile in self.tiles.items():
            if tile.owner == player and tile.units > 0:
                own_tiles.append((cube, tile))
        if len(own_tiles) <= 1:
            i = 0
        else:
            i = random.randint(0,len(own_tiles)-1)
        return own_tiles[i]

    def check_for_any_units(self, player):
        own_tiles = []
        for tile in self.tiles.values():
            if tile.owner == player and tile.units > 0:
                own_tiles.append(tile)
        if len(own_tiles) == 0:
            return False
        else: return True

    def move_units(self, origin, target):
        #assert isinstance(target, Tile)
        origin[1].owner.actions -= 1
        if (target[1].owner == None):
            self.capture_tile(origin, target)

        elif (target[1].owner == origin[1].owner):
            target[1].units = origin[1].units + target[1].units
            origin[1].units = 0
        
        else: self.combat_system(origin, target)

    def combat_system(self, origin, target):
        print(origin[1].owner, "attacks", target[1].owner, "with", origin[1].units, "against", target[1].units)
        if origin[1].units > target[1].units:
            origin[1].units -= target[1].units
            target[1].units = 0
            self.capture_tile(origin, target)
        elif origin[1].units == target[1].units:
            origin[1].units = 0
            target[1].units = 1
        else:
            target[1].units -= origin[1].units
            origin[1].units = 0

    def capture_tile(self, origin, target):
        print(origin[1].owner, "captures", target[0], 
        "from", target[1].owner)

        #check victory condition
        if (target[1].structures == "Capital"):
            self.game.defeat_player(target[1].owner)
            self.game.surrender_to_player(target[1].owner, origin[1].owner)
        else:
            target[1].owner = origin[1].owner

        target[1].units = origin[1].units
        origin[1].units = 0

        # extend borders around target tile
        neighbours_cube = cube.get_nearest_neighbours(target[0])
        neighbours = [self.tiles.get(x) for x in neighbours_cube if x in self.tiles]
        for neighbour in neighbours:
            if neighbour.units == 0 and neighbour.structures == None:
                neighbour.owner = origin[1].owner
        
    def print_world_state(self):
        for tile in self.tiles.values():
            if tile.units > 0:
                print("Tile:", tile, "units:", tile.units, "owner:", tile.owner)


def ai_controller(world, player):
    def pick_direction(number_of_directions):
        directions = []
        for _ in range(number_of_directions):
            direction = cube.cube_direction(random.randint(0,5))
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
    game.initialise()
    #event_queue = []

    while len(game.players) > 1:
        turn += 1
        if turn >= 100000: break
        for tile in game.world.tiles:
            tile.generate_units()
        if (turn % 2 == 0):
            print("Turn:", turn)
            game.world.print_world_state()
        for player in game.players:
            player.actions = 5
            if player.ai == True:
                while player.actions > 0 and game.world.check_for_any_units(player):
                    ai_controller(game.world.tiles, player)
    for player in game.players:
        print(player, "wins!")