from math import floor, ceil
import random

import army
import cubic
import data
import worldgen

ACTIONS_PER_TURN = 5

# A single Game() instance houses the game world and all players.
class Game:
    def __init__(self):
        self.turn = 0
        self.players = self.initialise_players()
        self.current_player = self.players[3]
        self.world = World(self)

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
        else:
            self.selection = None

    def skip_turn(self):
        self.actions = 0


# The game world is made of tiles. The tiles are mapped to cubic coordinates by using cubic coordinates as keys in the Map.map dictionary.
class World:
    def __init__(self, game):
        self.game = game
        self.tiles = worldgen.worldgen(shape='hexagon', radius=6, algorithm='random_ots', spawntype='random', players=self.game.players)#None

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

    def apply_idle_morale_penalty(self):
        for tile in self.tiles.values():
            if tile.army and tile.owner == self.game.current_player and tile.army.can_move:
                tile.army.morale -= army.MORALE_PENALTY_IDLE_ARMY

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


def update_world(game):
    if game.current_player.actions == 0:
        game.turn += 1
        print('turn:', game.turn, 'player', game.turn % 4)

        # Reset army movement points
        game.world.apply_idle_morale_penalty()
        for tile in game.world.tiles.values():
            if tile.army:
                tile.army.can_move = True

        if game.turn % len(game.players) == 1:
            game.world.train_armies()

        game.current_player = game.players[(game.turn - 1) % len(game.players)] # tutaj po pokonaniu gracza pętla sie pierdoli i moze dojsc do pominiecia czyjejs tury
        game.current_player.actions = 5

    # Force a player to skip a turn if he has no units to move
    if game.world.check_for_army(game.current_player) == False:
        game.current_player.actions = 0

    # Let AI make a move
    if game.current_player.ai == True and game.current_player.actions > 0:
        ai_controller(game.world, game.current_player)

    if len(game.players) <= 1:
        print(game.current_player, "wins!")

def main():
    """For testing purposes"""
    game = Game()
    game.current_player.actions = 0
    while len(game.players) > 1:
        update_world(game)