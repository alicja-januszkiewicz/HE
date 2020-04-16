import random

MAP_WIDTH = 20
MAP_HEIGHT = 10

class Player:
    def __init__(self, id="None", ai=True):
        self.id = id
        self.ai = ai
        self.actions = 5
        self.selection = None

    def __str__(self):
        return self.id
    
    def click_on_tile(self, tile):
        if (self.selection.owner == self and self.selection.units != 0):
            self.selection.move_units(tile)
        else:
            self.selection = tile


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.position = (x,y)
        self.owner = Player()
        self.structures = None
        self.units = 0

    def __str__(self):
        return str(self.position)

    def move_units(self, target):
        self.owner.actions -= 1
        if (target.owner.id == "None"):
            target.owner = self.owner
            target.units = self.units
            self.units = 0
        elif (target.owner == self.owner):
            target.units = self.units + target.units
            self.units = 0
        else: combat_system(self, target)

    def generate_units(self):
        if self.structures != None: self.units += 14
        if self.structures == "Capital": self.units += 14


def combat_system(origin, target):
    print(origin.owner, "attacks", target.owner)
    if origin.units > target.units:
        origin.units -= target.units
        target.units = 0
        change_tile_owner(target, origin.owner)
    elif origin.units == target.units:
        origin.units = 0
        target.units = 1
    else:
        target.units -= origin.units
        origin.units = 0

def change_tile_owner(tile, new_owner):
    print(new_owner, "captures", tile, "from", tile.owner)
    if (tile.structures == "Capital"):
        defeat_player(tile.owner)
        surrender_to_player(tile.owner, new_owner)
    else: tile.owner = new_owner

def defeat_player(player):
    for i in range(len(players)):
        if players[i] == player:
            del players[i]
            break
    print(player, "has been defeated!")


def surrender_to_player(defeated_player, player):
    for tile in world:
        if (tile.owner == defeated_player):
            tile.units = 0
            tile.owner = player

def initialise_players():
    players = []
    players.append(Player("Redosia"))
    players.append(Player("Bluegaria"))
    players.append(Player("Greenland"))
    players.append(Player("Violetnam"))
    return players

# This func will need to be coupled with map generation,
# as to remove the need for the redundant search
def get_tile(pos, game_world):
    for tile in game_world:
        if (tile.x == pos[0] and tile.y == pos[1]):
            return tile

def generate_empty_world():
    res=[]
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
            res.append(Tile(j, i))
    return res

def add_starting_areas(game_world, players):
    for player in players:
        starting_pos = (random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1))
        random_tile = get_tile(starting_pos, game_world)
        random_tile.owner = player
        random_tile.structures = "Capital"

def find_own_tile(world, player):
    own_tiles = []
    for tile in world:
        if tile.owner == player and tile.units > 0:
            own_tiles.append(tile)
    if len(own_tiles) <= 1:
        i = 0
    else:
        i = random.randint(0,len(own_tiles)-1)
    return own_tiles[i]

def find_units(world, player):
    for tile in world:
        if tile.owner == player:
            print(tile.units)

def check_for_any_units(world, player):
    own_tiles = []
    for tile in world:
        if tile.owner == player and tile.units > 0:
            own_tiles.append(tile)
    if len(own_tiles) == 0:
        return False
    else: return True

def ai_controller(world, player):
    #while (player.actions > 0):
    #tile = find_own_tile(world, player)
    #player.click_on_tile(tile)
    tile = world[random.randrange(0, len(world))]
    #print(player, "selects", tile)
    player.click_on_tile(tile)

def get_human_event():
    print("humanoid player skips turn")
    pass

def print_world_state(world):
    for tile in world:
        if tile.units > 0:
            print("Tile:", tile, "units:", tile.units, "owner:", tile.owner)

def run():
    turn = 0

    players = initialise_players()
    world = generate_empty_world()

    for player in players:
        player.selection = world[0]
        
    add_starting_areas(world, players)

    while len(players) > 1:
        turn += 1
        if turn >= 100000: break
        for tile in world:
            tile.generate_units()
        if (turn % 2 == 0):
            print("Turn:", turn)
            print_world_state(world)
        for player in players:
            player.actions = 5
            if player.ai == True:
                while player.actions > 0 and check_for_any_units(world, player):
                    ai_controller(world, player)
            #else:
                #get_human_event()

    for player in players:
        print(player, "wins!")