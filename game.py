"""Game class definition."""
import itertools

import army
import ai
import worldgen
import playergen

class Game:
    """The game class represents the game state.

    Attributes
    ----------
    turn : int
        the turn number
    players : list
        list of player instances
    playergen : object
        an infinite generator provided by itertools.cycle
    current_player : player object
        the current player
    world : dict
        a cube:tile map between a cubic coordinate object and a tile object
    """
    def __init__(self):
        self.turn = 0
        self.players = playergen.classic(self)
        self.playergen = itertools.cycle(self.players)
        self.current_player = self.players[0]
        #self.world = worldgen.generate_world(shape='classic', radius=6, algorithm='random_ots', spawntype='classic', players=self.players)
        self.world = worldgen.generate_world(shape='hexagon', radius=60, algorithm='random_ots', spawntype='random', players=self.players)
        self.initial_layout = worldgen.layout
        playergen.create_player_cameras(self)

    def update_world(self):
        """The main game logic loop which runs every turn."""
        if self.current_player.actions == 0:
            self.current_player.selection = None
            self.current_player.actions = 5

            self.train_armies()
            # Reset army movement points
            self.apply_idle_morale_penalty()
            for tile in self.world.values():
                if tile.army:
                    tile.army.can_move = True

            self.current_player = next(self.playergen)
            while self.current_player.is_defeated:
                self.current_player = next(self.playergen)
            self.turn += 1
            print('turn:', self.turn, 'player', self.current_player)

        # Force a player to skip a turn if he has no units to move
        if not self.can_player_issue_a_command(self.current_player):
            self.current_player.actions = 0

        # Let AI make a move
        if self.current_player.ai:
            target_generator = ai.generate_targets(self)
            for target in target_generator:
                if self.current_player.actions > 0:
                    ai.controller(self, target)
                else:
                    break
            self.current_player.skip_turn()

        if len(self.players) <= 1:
            print(self.current_player, "wins!")

    def defeat_player(self, player):
        """Removes a player instance from the players list."""
        player.is_defeated = True
        print(player, "has been defeated!")

    def surrender_to_player(self, defeated_player, player):
        """Transfer the ownership of all of defeated_player tiles to player."""
        for tile in self.world.values():
            if tile.owner == defeated_player:
                tile.army = None
                tile.owner = player

    def train_armies(self):
        """Trains appropriate armies for every player.
        To be called at the end of every turn by the update_world() method."""
        player = self.current_player
        tiles_owned_by_player = []
        for tile in self.world.values():
            if tile.owner == player:
                tiles_owned_by_player.append(tile)

        # First apply base growth
        for tile in tiles_owned_by_player:
            if not tile.locality:
                continue
            if tile.locality.category == "City":
                if not tile.army:
                    tile.army = army.Army(army.BASE_GROWTH_CITY, 1/2 * army.BASE_GROWTH_CITY, tile.owner)
                elif tile.army.manpower < army.MAX_STACK_SIZE:
                    tile.army.manpower += army.BASE_GROWTH_CITY
                    tile.army.morale += 1/2 * army.BASE_GROWTH_CITY
            elif tile.locality.category == "Capital":
                if not tile.army:
                    tile.army = army.Army(army.BASE_GROWTH_CAPITAL, 1/2 * army.BASE_GROWTH_CAPITAL, tile.owner)
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
                if tile.locality and tile.army.manpower < army.MAX_STACK_SIZE:
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
        for tile in self.world.values():
            if tile.army:
                tile.army.morale = min(army.MAX_STACK_SIZE, tile.army.morale)
                tile.army.morale = round(tile.army.morale)

    def can_player_issue_a_command(self, player):
        own_tiles = []
        for tile in self.world.values():
            if tile.owner == player and tile.army and tile.army.can_move:
                own_tiles.append(tile)
        if len(own_tiles) == 0:
            return False
        return True

    def check_victory_condition(self):
        for player in self.players:
            starting_tile = self.world.get(player.starting_cube)
            if starting_tile.owner != player and not player.is_defeated:
                self.defeat_player(player)
                self.surrender_to_player(player, starting_tile.owner)

    def apply_idle_morale_penalty(self):
        """Applies a morale penalty to idle armies."""
        for tile in self.world.values():
            if  (tile.army and tile.army.can_move
                 and tile.owner == self.current_player):

                tile.army.morale -= army.MORALE_PENALTY_IDLE_ARMY
                tile.army.morale = max(tile.army.morale, army.calculate_minimum_morale(self.world.values(), tile.army))

    def print_world_state(self):
        """A debugging function used in graphicless mode."""
        for tile in self.world.values():
            if tile.army:
                print(tile, tile.owner, tile.army)

def main():
    """For debugging purposes"""
    game = Game()
    game.current_player.actions = 0
    while len(game.players) > 1:
        game.update_world()
