from math import floor
import random

import cube

MAP_WIDTH = 24
MAP_HEIGHT = 12
LAYOUT = cube.Layout(cube.layout_flat, cube.Point(40,40), cube.Point(20,40))

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
            
        self.world.generate_cities(self)
        self.world.add_starting_areas(self.players)

    def initialise_players(self):
        players = []
        players.append(Player("Redosia", ai=False))
        players.append(Player("Bluegaria"))
        players.append(Player("Greenland"))
        players.append(Player("Violetnam"))
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

    #def add_event_to_queue(self, event):
    #    self.event_queue.append(event)

    #def process_events(event_queue, self):
    #    pass

class Player:
    def __init__(self, id="None", ai=True):
        self.id = id
        self.ai = ai
        self.actions = 5
        self.selection = None

    def __str__(self):
        return self.id

    def get_selection_neighbours(self, selection):
        neighbours = []
        for i in range(6):
            neighbour = cube.cube_neighbour(selection, i)
            neighbours.append(neighbour)
        return neighbours

    def click_on_tile(self, tile):
        attack_condition = self.selection[1].owner == self and self.selection[1].units != 0
        if (attack_condition):
            legal_moves = self.get_selection_neighbours(self.selection[0])
            for coord in legal_moves:
                if tile[0] == coord:
                    self.selection[1].move_units(tile[1])
                    break
            self.selection = tile
        else:
            self.selection = tile


class Tile:
    def __init__(self, game):
        self.game = game
        self.owner = Player()
        self.structures = None
        self.units = 0

    def __str__(self):
        return str(self.structures) + " " + str(self.owner) + " " + str(self.units)

    def move_units(self, target):
        #assert isinstance(target, Tile)
        self.owner.actions -= 1
        if (target.owner.id == "None"):
            target.owner = self.owner
            target.units = self.units
            self.units = 0
        elif (target.owner == self.owner):
            target.units = self.units + target.units
            self.units = 0
        else: self.combat_system(self, target)

    def generate_units(self):
        if self.owner.id != "None" and self.units < 100:
            if self.structures != None: self.units += 14
            elif self.structures == "Capital": self.units += 14

    def combat_system(self, origin, target):
        print(origin.owner, "attacks", target.owner)
        if origin.units > target.units:
            origin.units -= target.units
            target.units = 0
            self.capture_tile(origin, target)
        elif origin.units == target.units:
            origin.units = 0
            target.units = 1
        else:
            target.units -= origin.units
            origin.units = 0

    def capture_tile(self, capturing_tile, captured_tile):
        print(capturing_tile.owner, "captures", captured_tile, 
        "from", captured_tile.owner)

        if (captured_tile.structures == "Capital"):
            self.game.defeat_player(captured_tile.owner)
            self.game.surrender_to_player(captured_tile.owner, capturing_tile.owner)
        else:
            captured_tile.owner = capturing_tile.owner

        captured_tile.units = capturing_tile.units
        capturing_tile.units = 0


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

    def generate_cities(self, game):
        for tile in game.world.tiles.values():
            if random.random() > 0.9:
                tile.structures = "City"

    def add_starting_areas(self, players):
        for player in players:
            starting_tile = random.choice(list(self.tiles.values()))
            starting_tile.owner = player
            starting_tile.structures = "Capital"
            #player.selection = starting_tile

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

    def find_units(self, player):
        for tile in self.tiles.values():
            if tile.owner == player:
                print(tile.units)

    def check_for_any_units(self, player):
        own_tiles = []
        for tile in self.tiles.values():
            if tile.owner == player and tile.units > 0:
                own_tiles.append(tile)
        if len(own_tiles) == 0:
            return False
        else: return True


class Event:
    def __init__(self, action, target, origin):
        self.action = action
        self.target = target
        self.origin = origin


def ai_controller(world, player):
    def pick_direction():
        direction = cube.cube_direction(random.randint(0,5))
        return direction

    tile = world.find_own_tile(player)
    player.click_on_tile(tile)

    direction = pick_direction()
    position = tile[0] + direction
    while position not in world.tiles:
        direction = pick_direction()
        position = tile[0] + direction

    tiledata = world.tiles.get(position)
    tile = (position, tiledata)

    #tile = random.choice(list(world.tiles.items()))
    player.click_on_tile(tile)

def print_world_state(world):
    for tile in world.tiles.values():
        if tile.units > 0:
            print("Tile:", tile, "units:", tile.units, "owner:", tile.owner)

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
            print_world_state(game.world)
        for player in game.players:
            player.actions = 5
            if player.ai == True:
                while player.actions > 0 and game.world.check_for_any_units(player):
                    ai_controller(game.world.tiles, player)
            #else:
                #get_human_event()

    for player in game.players:
        print(player, "wins!")

#run()