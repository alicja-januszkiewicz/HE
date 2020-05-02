"""Honeycomb Empire!"""
import sys, random
from math import sin, pi, floor, sqrt
import ctypes

import sdl2.ext
import sdl2.sdlgfx

import gfx
import camera
import cubic
import army
import logic
import draw
import data

context = gfx.context

def update_screen(game, layout):
    context.clear(0)

    selection = game.current_player.selection
    selection_cube = cubic.Cube(0,0,0)
    #selection_cube = mousepos_cube
    mousepos_cube = get_cube_mousepos()

    if selection != None: selection_cube = selection[0]
    for tilepair in game.world.tiles.items():
        draw.game_tile(context, layout, tilepair)

        # draw army.can_move indicator
        cube, tile = tilepair
        if selection == None:
            if (tile.army and tile.army.can_move and tile.owner == game.current_player):
                draw.army_can_move_indicator(context, layout, cube)

        draw.tile_army(context, layout, tilepair)
        draw.tile_locality(context, layout, tilepair)

    # draw army selector and legal move indicators
    draw.tile_selector(context, layout, mousepos_cube)
    if selection_cube in game.world.tiles:
        #draw.tile_selector(context, mousepos_cube)
        if game.world.tiles.get(selection_cube).army:
            for cube in cubic.reachable_cubes(game.world.tiles, selection_cube, army.MAX_TRAVEL_DISTANCE): #cubic.get_all_neighbours(selection_cube, army.MAX_TRAVEL_DISTANCE):
                if cube in game.world.tiles:
                    draw.legal_move_indicator(context, layout, cube)

    # draw army info
    if mousepos_cube in game.world.tiles:
        range = set(cubic.get_all_neighbours(mousepos_cube, 2))
        range.add(mousepos_cube)
        for cube in range:
            if cube not in game.world.tiles:
                continue

            tile = game.world.tiles[cube]
            if tile.army:
                tilepair = cube, tile
                draw.army_info(context, layout, tilepair)

    # draw city names
    if mousepos_cube in game.world.tiles:
        range = set(cubic.get_all_neighbours(mousepos_cube, 5))
        range.add(mousepos_cube)
        for cube in range:
            if cube not in game.world.tiles:
                continue

            tile = game.world.tiles[cube]
            tilepair = cube, tile
            draw.city_name(context, layout, tilepair)

    context.present()

def get_pixel_mousepos():
    x, y = ctypes.c_int(0), ctypes.c_int(0)
    _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
    return cubic.Point(x.value, y.value)

def get_cube_mousepos():
    pixel_mousepos = get_pixel_mousepos()
    cube_mousepos = cubic.cube_round(cubic.pixel_to_cube(camera.get_layout(), pixel_mousepos))
    return cube_mousepos

def processInput(game):
    sdl2.SDL_PumpEvents()
    keystatus = sdl2.SDL_GetKeyboardState(None)
    if keystatus[sdl2.SDL_SCANCODE_W]:
        print("the w key was pressed")
    # continuous-response keys
    if keystatus[sdl2.SDL_SCANCODE_LEFT]:
        camera.pan(cubic.Point(1,0))
    if keystatus[sdl2.SDL_SCANCODE_RIGHT]:
        camera.pan(cubic.Point(-1,0))
    if keystatus[sdl2.SDL_SCANCODE_UP]:
        camera.pan(cubic.Point(0,1))
    if keystatus[sdl2.SDL_SCANCODE_DOWN]:
        camera.pan(cubic.Point(0,-1))

    for event in sdl2.ext.get_events():
        if event.type == sdl2.SDL_QUIT:
            sdl2.ext.quit()

        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN and game.current_player.ai == False:
            mousepos_cube = get_cube_mousepos()
            selected_tile = game.world.tiles.get(mousepos_cube)
            if selected_tile != None:
                game.current_player.click_on_tile((mousepos_cube, selected_tile))

        elif event.type == sdl2.SDL_MOUSEWHEEL:
            camera.zoom(event.wheel.y)

def run():
    timeStepMs = 1000 / 30 # refresh rate eg. 30Hz

    game = logic.Game()
    game.current_player.actions = 0
    timeCurrentMs = 0
    timeAccumulatedMs = 0

    layout = camera.get_layout()

    running = len(game.players) > 1
    while running:
        timeLastMs = timeCurrentMs
        timeCurrentMs = sdl2.SDL_GetTicks()
        timeDeltaMs = timeCurrentMs - timeLastMs
        timeAccumulatedMs += timeDeltaMs

        while (timeAccumulatedMs >= timeStepMs):
            processInput(game)
            logic.update_world(game)
            running = len(game.players) > 1
            timeAccumulatedMs -= timeStepMs

        update_screen(game, layout)

    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())

# To do:
# Gameplay: water, AI, unit tiers, releasing nations, train player's armies immediatly after he ends his turn, choosing starting nation
# Camera: rotating 
# Art: sprites, sounds, music, gradual fade-in of locality names
# Multiplayer
# Map editor
# Campaign mode
# UI: game menu, settings menu
# Settings: map dimensions, map generation (bug: starting positions can overwrite one another), map seeds, variable no of players
# Alternative ruleset: fog of war, border expansion
# Code quality: decouple refresh rate from game speed

# Bugs:
# rounding error: 0/0 army still possible (possibly fixed)
# floating point morale for some units after applying losing battle morale penalty (possibly fixed)
# sometimes the human player seems to get two turns in a row
# sort out alpha blending
# very rarely legal move indicator gets stuck
# negative morale spotted on a very large map
# zooming may set layout.size to (0,0), causing the game to crash

# Done: idle morale penalty, only tiles with localities have names, camera panning and rotating, worldgen, new main loop