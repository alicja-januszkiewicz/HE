import random

MAP_WIDTH = 24
MAP_HEIGHT = 12

class Game:
    def __init__(self):
        self.turn = 0
        self.players = []
        self.world = []
        self.event_queue = []

    def initialise(self):
        self.players = self.initialise_players()
        self.world = World(self)

        for player in self.players:
            player.selection = self.world.tiles[0]
            
        self.world.add_starting_areas(self.players)
        self.world.generate_cities(self)

    def initialise_players(self):
        players = []
        players.append(Player("Redosia"))
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
        for tile in self.world.tiles:
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

    #def check_if_legal():
    #    pass

    def click_on_tile(self, tile):
        if (self.selection.owner == self and self.selection.units != 0):
            pos = (tile.x, tile.y)
            legal_moves = self.selection.get_neighbours_pos()
            for coord in legal_moves:
                #print("pos:", pos, "legal:", legal_moves)
                if pos == coord:
                    self.selection.move_units(tile)
                    break
        else:
            self.selection = tile


class Tile:
    DIRECTIONS = ( 
        ( (1,0), (-1,1), (0,-1), (-1,0), (0,1), (1,1) ),
        ( (1,0), (0,-1), (-1,-1), (-1,0), (1,-1), (0,1) )
        
    )

    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.position = (x,y)
        self.game = game
        self.owner = Player()
        self.structures = None
        self.units = 0

    def __str__(self):
        return str(self.position)

    def get_neighbours_pos(self):
        neighbours = []
        parity = self.y & 1
        for direction in Tile.DIRECTIONS[parity]:
            x = self.x + direction[0]
            y = self.y + direction[1]
            pos = (x,y)
            neighbours.append(pos)
        return neighbours

    def move_units(self, target):
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
        if self.owner.id != "None":
            if self.structures != None: self.units += 14
            if self.structures == "Capital": self.units += 14

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


class World:
    def __init__(self, game):
        self.game = game
        self.tiles = self.generate_empty_world(self.game)

    # This method will need to be coupled with map generation,
    # as to remove the need for the redundant search
    def get_tile(self, pos, game_world):
        for tile in game_world:
            if (tile.x == pos[0] and tile.y == pos[1]):
                return tile

    def generate_empty_world(self, game):
        res=[]
        for i in range(MAP_HEIGHT):
            for j in range(MAP_WIDTH):
                res.append(Tile(j, i, game))
        return res

    def generate_cities(self, game):
        for tile in game.world.tiles:
            if random.random() > 0.9:
                tile.structures = "city"

    def add_starting_areas(self, players):
        for player in players:
            starting_pos = (random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1))
            random_tile = self.get_tile(starting_pos, self.tiles)
            random_tile.owner = player
            random_tile.structures = "Capital"
            player.selection = random_tile

    def find_own_tile(self, player):
        own_tiles = []
        for tile in self.tiles:
            if tile.owner == player and tile.units > 0:
                own_tiles.append(tile)
        if len(own_tiles) <= 1:
            i = 0
        else:
            i = random.randint(0,len(own_tiles)-1)
        return own_tiles[i]

    def find_units(self, player):
        for tile in self.tiles:
            if tile.owner == player:
                print(tile.units)

    def check_for_any_units(self, player):
        own_tiles = []
        for tile in self.tiles:
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
    #while (player.actions > 0):
    #tile = find_own_tile(world, player)
    #player.click_on_tile(tile)
    tile = world[random.randrange(0, len(world))]
    #print("AI selects", tile)
    #print(player, "selects", tile)
    player.click_on_tile(tile)

def get_human_event():
    print("humanoid player skips turn")
    pass

def print_world_state(world):
    for tile in world.tiles:
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