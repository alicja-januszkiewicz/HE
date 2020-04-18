"""Honeycomb Empire!"""
import sys, random
from math import sin, pi, floor, sqrt
import ctypes

import sdl2.ext
import sdl2.sdlgfx

import graphics
import cube
import logic
import draw

ZOOM_LEVEL = 50
SCREEN_WIDTH = 2048
SCREEN_HEIGHT = 1152

context = graphics.context

def update_screen(game):
    context.clear(0)
    for tile in game.world.tiles.items():
        draw.draw_game_tile(tile, context)
        draw.draw_tile_units(tile, context)
        draw.draw_tile_structs(tile, context)
    context.present()

def run():
    turn = 0
    game = logic.Game()
    game.initialise()

    # def human_mouseclick_event(mousepos, player):
    #     new_pos = cube.pixel_to_cube(logic.LAYOUT, cube.Point(mousepos[0], mousepos[1]))
    #     print(new_pos)
    #     selected_tile = game.world.tiles[new_pos]
    #     draw.draw_tile_selector(selected_tile, context)
    #     context.present()
    #     player.click_on_tile(selected_tile)

    running = len(game.players) > 1
    while running:
        turn += 1
        if turn >= 100000: break
        for tile in game.world.tiles.values():
            tile.generate_units()
        update_screen(game)
        #sdl2.SDL_Delay(500)
        if (turn % 1000 == 0):
            print("Turn:", turn)
            logic.print_world_state(game.world)
        for player in game.players:
            player.actions = 5
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
                            update_screen(game)
                            x, y = ctypes.c_int(0), ctypes.c_int(0)
                            _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
                            mousepos = cube.Point(x.value, y.value)

                            new_pos = cube.cube_round(cube.pixel_to_cube(logic.LAYOUT, mousepos))
                            print(new_pos)
                            draw.draw_tile_selector(new_pos, context)
                            context.present()
                            selected_tile = game.world.tiles[new_pos]
                            player.click_on_tile((new_pos, selected_tile))


        if len(game.players) <= 1:
            running = False
            break

    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())

# capitals dissapear -> possibly fixed
# screen doesnt seem to draw correctly?
# need to align game board with offset. changing LAYOUT.offset from (20,40) will break tile selection.