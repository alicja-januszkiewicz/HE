"""Honeycomb Empire!"""
import sys, random
from math import sin, pi, floor, sqrt
import ctypes

import sdl2.ext
import sdl2.sdlgfx

import gfx
import cubic
import logic
import draw

ZOOM_LEVEL = 50

context = gfx.context

def update_screen(game, mousepos_cube=cubic.Cube(0,0,0)):
    context.clear(0)
    selection = game.current_player.selection
    selection_cube = cubic.Cube(0,0,0)
    if selection != None: selection_cube = selection[0]
    for tilepair in game.world.tiles.items():
        draw.game_tile(context, tilepair)
        draw.tile_army(context, tilepair)
        draw.tile_structs(context, tilepair)

    # draw army selector and legal move indicators
    if selection_cube in game.world.tiles:
        draw.tile_selector(context, selection_cube)
        if game.world.tiles.get(selection_cube).army.manpower > 0:
            for cube in cubic.get_all_neighbours(selection_cube, logic.MAX_TRAVEL_DISTANCE):
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
            if tile.army.manpower > 0:
                tilepair = cube, tile
                draw.army_info(context, tilepair)
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

    running = len(game.players) > 1
    while running:
        turn += 1

        for tile in game.world.tiles.values():
            tile.train_army()
        
        update_screen(game)

        for player in game.players:
            game.current_player = player
            player.actions = logic.ACTIONS_PER_TURN
            while player.actions > 0 and game.world.check_for_army(player):
                if player.ai == True:
                    logic.ai_controller(game.world, player)
                    update_screen(game)
                    sdl2.SDL_Delay(30)
                else:
                    for event in sdl2.ext.get_events():
                        if event.type == sdl2.SDL_QUIT:
                            running = False
                            sdl2.ext.quit()
                            return 0

                        if event.type == sdl2.SDL_MOUSEMOTION:
                            update_screen(game, get_cube_mousepos())

                        if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                            mousepos_cube = get_cube_mousepos()
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

# To do:
# obstacles, morale, fonts, unit growth, max stacks, AI, unit tiers, scrolling, panning, rotating
# replace mousemotion event with mouse-changes-cube-coord event
# bug: starting positions can overwrite one another
# bug: player is defeated when ANY of his capitals are captured
# feature: players release other players when defeated
# feature: area controlled by a player expands each turn by 1 tile
# feature: units should be able to move by 2 tiles, unless blocked by an obstacle

# feature: fog of war