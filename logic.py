from math import floor, ceil
import random

from draw import LAYOUT
import army
import cubic
import data

MAP_WIDTH = 20
MAP_HEIGHT = 11
ACTIONS_PER_TURN = 5

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
        self.current_player = self.players[3]
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
                tile.army = None
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
        self.starting_cube = None

    def __str__(self):
        return self.id

    def calc_army_growth(self):
        growth = 0
        for tile in self.game.world.tiles.values():
            if tile.owner == self: growth += 1
        return growth

    def click_on_tile(self, tilepair):
        clicked_cube, clicked_tile = tilepair
        if tilepair == self.selection:
            # deselects currently selected tile
            self.selection = None
            return 0
        
        if (
            self.selection != None 
            and self.selection[1].owner == self 
            and self.selection[1].army
            and self.selection[1].army.can_move
        ):
            legal_moves = cubic.reachable_cubes(self.game.world.tiles, self.selection[0], army.MAX_TRAVEL_DISTANCE)
            for coord in legal_moves:
                if clicked_cube == coord:
                    army.issue_order(self.game.world.tiles, self.selection[1], clicked_tile)
                    self.game.world.check_victory_condition()
                    # after capturing, deselects the tile clicked on.
                    self.selection = None
                    break
            else:
                # selects a different unit without having to click twice on it to deselect current selection
                if clicked_tile.army and clicked_tile.army.can_move:
                    self.selection = tilepair
                else: self.selection = None
        elif clicked_tile.army and clicked_tile.army.can_move:
            self.selection = tilepair


    def skip_turn(self):
        self.actions = 0


class Tile:
    def __init__(self, game):
        self.game = game
        self.owner = None #Player()
        self.locality = AttrDict()
        self.locality.type = None
        self.locality.name = data.choose_random_city_name()
        self.army = None

    def __str__(self):
        return str(self.locality.name) + " " + str(self.owner)# + " " + [self.army if self.army]

    def combat_strength(self):
        return self.army.manpower + self.army.morale


class Map:
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
        #     if k not in (cubic.Cube(2,1,-3), cubic.Cube(2,9,-11), cubic.Cube(19, -8, -11), cubic.Cube(19,0,-19)) and random.random() > 0.86:
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
                tile.locality.type = "City"

    def add_starting_areas(self, players, flag="vanilla"):
        if flag == "vanilla":
            starting_positions = (cubic.Cube(2,1,-3), cubic.Cube(2,9,-11), cubic.Cube(19, -8, -11), cubic.Cube(19,0,-19))
            for player, pos in zip(players, starting_positions):
                tile = self.tiles[pos]
                tile.owner = player
                tile.locality.type = "Capital"
                player.starting_cube = pos

                for neighbour in cubic.get_nearest_neighbours(pos):
                    tile = self.tiles.get(neighbour)
                    tile.owner = player
        else:
            for player in players:
                starting_tile = random.choice(list(self.tiles.values()))
                starting_tile.owner = player
                starting_tile.locality.type = "Capital"

    # def expand_borders(self):
    #     for cube, tile in self.tiles.copy().items():
    #         if tile.owner.id != "None":
    #             neighbours_cubes = cubic.get_nearest_neighbours(cube)
    #             neighbours = [self.tiles.get(x) for x in neighbours_cubes if x in self.tiles]
    #             for neighbour in neighbours:
    #                 if neighbour.owner.id == "None":
    #                     neighbour.owner = tile.owner 

    def train_armies(self):
        for player in self.game.players:
            tiles_owned_by_player = []
            for tile in self.tiles.values():
                if tile.owner == player:
                    tiles_owned_by_player.append(tile)

            # First apply base growth
            for tile in tiles_owned_by_player:
                if tile.locality.type == "City":
                    if not tile.army:
                        tile.army = army.Army(army.BASE_GROWTH_CITY, 1/2 * army.BASE_GROWTH_CITY)
                    elif tile.army.manpower < army.MAX_STACK_SIZE:
                        tile.army.manpower += army.BASE_GROWTH_CITY
                        tile.army.morale += 1/2 * army.BASE_GROWTH_CITY
                elif tile.locality.type == "Capital":
                    if not tile.army:
                        tile.army = army.Army(army.BASE_GROWTH_CAPITAL, 1/2 * army.BASE_GROWTH_CAPITAL)
                    elif tile.army.manpower < army.MAX_TRAVEL_DISTANCE:
                        tile.army.manpower += army.BASE_GROWTH_CITY
                        tile.army.morale += 1/2 * army.BASE_GROWTH_CITY
                if tile.army:
                    if tile.army.manpower > army.MAX_STACK_SIZE:
                        tile.army.manpower = army.MAX_STACK_SIZE
                    if tile.army.morale > army.MAX_STACK_SIZE:
                        tile.army.morale = army.MAX_STACK_SIZE

            # Then apply bonus growth
            player_bonus_growth = len(tiles_owned_by_player) * army.BONUS_GROWTH_PER_TILE
            while player_bonus_growth > 0:
                tiles_with_max_army_stack = 0
                for tile in tiles_owned_by_player:
                    if tile.locality.type != None and tile.army.manpower < army.MAX_STACK_SIZE:
                        tile.army.manpower += 1
                        tile.army.morale += 0.5
                        player_bonus_growth -= 1
                    else:
                        tiles_with_max_army_stack += 1

                    # break if we can't apply the bonus anywhere
                    if len(tiles_owned_by_player) == tiles_with_max_army_stack:
                        player_bonus_growth = 0
                        break

            # Round morale values
            for tile in self.tiles.values():
                if tile.army:
                    tile.army.morale = min(army.MAX_STACK_SIZE, tile.army.morale)
                    tile.army.morale = round(tile.army.morale)

    def find_own_tile(self, player):
        own_tiles = []
        for cube, tile in self.tiles.items():
            if tile.owner == player and tile.army:
                own_tiles.append((cube, tile))
        if len(own_tiles) <= 1:
            i = 0
        else:
            i = random.randint(0,len(own_tiles)-1)
        return own_tiles[i]

    def check_for_army(self, player):
        own_tiles = []
        for tile in self.tiles.values():
            if tile.owner == player and tile.army and tile.army.can_move:
                own_tiles.append(tile)
        if len(own_tiles) == 0:
            return False
        else: return True

    def check_victory_condition(self):
        for player in self.game.players:
            starting_tile = self.tiles.get(player.starting_cube)
            if starting_tile.owner != player:       
                self.game.defeat_player(player)
                self.game.surrender_to_player(player, starting_tile.owner)

    def print_world_state(self):
        for tile in self.tiles.values():
            if tile.army:
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