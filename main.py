"""Honeycomb Empire!"""
import sys, random
from math import sin, pi, floor
import ctypes

import sdl2.ext
import sdl2.sdlgfx

import graphics
import logic
import draw

ZOOM_LEVEL = 40
SCREEN_WIDTH = 2048
SCREEN_HEIGHT = 1152

context = graphics.context

#def cube_to_oddq(cube):
#    col = cube.x
#    row = cube.z + (cube.x - (cube.x&1)) / 2
#    return OffsetCoord(col, row)

#def oddq_to_cube(hex):
#    x = hex.col
#    z = hex.row - (hex.col - (hex.col&1)) / 2
#    y = -x-z
#    return Cube(x, y, z)

def run():
    #sdl_init()

    #draw_hex_grid(20,10)
    #graphics.context.present()
    
    turn = 0
    game = logic.Game()
    game.initialise()

    running = len(game.players) > 1
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        turn += 1
        if turn >= 100000: break
        for tile in game.world.tiles:
            draw.draw_game_tile(tile, context)
            draw.draw_tile_units(tile, context)
            tile.generate_units()
        context.present()
        sdl2.SDL_Delay(300)
        if (turn % 2 == 0):
            print("Turn:", turn)
            logic.print_world_state(game.world)
        for player in game.players:
            player.actions = 5
            if player.ai == True:
                while player.actions > 0 and game.world.check_for_any_units(player):
                    logic.ai_controller(game.world.tiles, player)
        if len(game.players) <= 1:
            running = False
            break
            #else:
                #get_human_event()

    
    sdl2.ext.quit()
    print(sys.path)
    return 0

if __name__ == "__main__":
    sys.exit(run())