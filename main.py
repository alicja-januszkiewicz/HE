"""Honeycomb Empire!"""
import sys, random
from math import sin, pi, floor, sqrt
import ctypes

import sdl2.ext
import sdl2.sdlgfx

import gfx
import cubic
import army
import logic
import draw
import data

ZOOM_LEVEL = 50

context = gfx.context

def update_screen(game):
    context.clear(0)

    selection = game.current_player.selection
    selection_cube = cubic.Cube(0,0,0)
    #selection_cube = mousepos_cube
    mousepos_cube = get_cube_mousepos()

    if selection != None: selection_cube = selection[0]
    for tilepair in game.world.tiles.items():
        draw.game_tile(context, tilepair)
        draw.tile_army(context, tilepair)
        draw.tile_locality(context, tilepair)

    # draw army selector and legal move indicators
    draw.tile_selector(context, mousepos_cube)
    if selection_cube in game.world.tiles:
        #draw.tile_selector(context, mousepos_cube)
        if game.world.tiles.get(selection_cube).army.manpower > 0:
            for cube in cubic.get_all_neighbours(selection_cube, army.MAX_TRAVEL_DISTANCE):
                if cube in game.world.tiles:
                    draw.legal_move_indicator(context, cube)

    # draw army info
    if mousepos_cube in game.world.tiles:
        range = set(cubic.get_all_neighbours(mousepos_cube, 2))
        range.add(mousepos_cube)
        for cube in range:
            if cube not in game.world.tiles:
                continue

            tile = game.world.tiles[cube]
            if tile.army.manpower > 0 or tile.army.morale > 0:
                tilepair = cube, tile
                draw.army_info(context, tilepair)

    # draw city names
    if mousepos_cube in game.world.tiles:
        range = set(cubic.get_all_neighbours(mousepos_cube, 5))
        range.add(mousepos_cube)
        for cube in range:
            if cube not in game.world.tiles:
                continue

            tile = game.world.tiles[cube]
            tilepair = cube, tile
            draw.city_name(context, tilepair)

    context.present()

def get_pixel_mousepos():
    x, y = ctypes.c_int(0), ctypes.c_int(0)
    _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
    return cubic.Point(x.value, y.value)

def get_cube_mousepos():
    pixel_mousepos = get_pixel_mousepos()
    cube_mousepos = cubic.cube_round(cubic.pixel_to_cube(logic.LAYOUT, pixel_mousepos))
    return cube_mousepos

def run():
    turn = 0
    game = logic.Game()
    game.current_player.actions = 0
    old_cube_mousepos = None

    running = len(game.players) > 1
    while running:
        if game.current_player.actions == 0:
            turn += 1
            if turn % len(game.players) == 1:
                game.world.train_armies()
            update_screen(game)

            game.current_player = game.players[(turn - 1) % len(game.players)]
            game.current_player.actions = 5

        # Force a player to skip a turn if he has no units to move
        if game.world.check_for_army(game.current_player) == False:
            game.current_player.actions = 0

        # Let AI make a move
        if game.current_player.ai == True and game.current_player.actions > 0:
            logic.ai_controller(game.world, game.current_player)
            update_screen(game)
            sdl2.SDL_Delay(10)

        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                sdl2.ext.quit()

            if event.type == sdl2.SDL_MOUSEMOTION:
                # mouse changes cube pos pseudo event
                current_mousepos_cube = get_cube_mousepos()
                if current_mousepos_cube != old_cube_mousepos:
                    old_cube_mousepos = current_mousepos_cube
                    update_screen(game)

            if event.type == sdl2.SDL_MOUSEBUTTONDOWN and game.current_player.ai == False:
                mousepos_cube = get_cube_mousepos()
                selected_tile = game.world.tiles.get(mousepos_cube)
                if selected_tile != None:
                    game.current_player.click_on_tile((mousepos_cube, selected_tile))

                update_screen(game)

        if len(game.players) <= 1:
            print(game.current_player, "wins!")
            running = False
            break

    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())

# To do:
# collision, water, AI, unit tiers, (camera: scrolling, panning, rotating), sprites, multiplayer
# done: morale, fonts, unit growth, max stacks,
# replace mousemotion event with mouse-changes-cube-coord event
# bug: starting positions can overwrite one another
# bug: player is defeated when ANY of his capitals are captured
# feature: players release other players when defeated
# feature: area controlled by a player expands each turn by 1 tile
# feature: fog of war