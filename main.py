"""Honeycomb Empire!"""
import sys, random
from math import sin, pi, floor, sqrt
import ctypes

import sdl2.ext
import sdl2.sdlgfx

import gfx
import cube
import logic
import draw

ZOOM_LEVEL = 50

context = gfx.context

def update_screen(game, selector_pos=None):
    context.clear(0)
    for tile in game.world.tiles.items():
        draw.game_tile(tile, context)
        draw.tile_units(tile, context)
        draw.tile_structs(tile, context)
    if selector_pos in game.world.tiles:
        draw.tile_selector(selector_pos, context)
        if game.world.tiles.get(selector_pos).units > 0:
            for cube_ in cube.get_all_neighbours(selector_pos, logic.MAX_TRAVEL_DISTANCE):
                if cube_ in game.world.tiles:
                    draw.legal_move_indicator(cube_, context)
    context.present()

def run():
    turn = 0
    game = logic.Game()
    game.initialise()

    running = len(game.players) > 1
    while running:
        turn += 1
        if turn >= 100000: break
        for tile in game.world.tiles.values():
            tile.generate_units()
        #game.world.expand_borders()
        update_screen(game)
        #sdl2.SDL_Delay(500)
        if (turn % 1000 == 0):
            print("Turn:", turn)
            game.world.print_world_state()
        for player in game.players:
            player.actions = logic.ACTIONS_PER_TURN
            while player.actions > 0 and game.world.check_for_any_units(player):
                if player.ai == True:
                    logic.ai_controller(game.world, player)
                    update_screen(game)
                else:
                    for event in sdl2.ext.get_events():
                        if event.type == sdl2.SDL_QUIT:
                            running = False
                            break
                        if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                            # get mouse coord
                            x, y = ctypes.c_int(0), ctypes.c_int(0)
                            _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
                            mousepos = cube.Point(x.value, y.value)
                            mousepos_cube = cube.cube_round(cube.pixel_to_cube(logic.LAYOUT, mousepos))

                            # do things
                            selected_tile = game.world.tiles.get(mousepos_cube)
                            if selected_tile != None:
                                player.click_on_tile((mousepos_cube, selected_tile))

                            update_screen(game, mousepos_cube)

        if len(game.players) <= 1:
            for player in game.players:
                print(player, "wins!")
            running = False
            break

    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())

# bug: starting positions can overwrite one another
# bug: player is defeated when ANY of his capitals are captured
# feature: players release other players when defeated
# feature: area controlled by a player expands each turn by 1 tile
# feature: units should be able to move by 2 tiles, unless blocked by an obstacle

# feature: fog of war