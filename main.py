"""Honeycomb Empire: The main loop."""
import sys

import sdl2.ext
import sdl2.sdlgfx

import gfx
import cubic
from game import Game

def poll_inputs(game, camera):
    """Listens for user input."""
    sdl2.SDL_PumpEvents() # unsure if necessary
    keystatus = sdl2.SDL_GetKeyboardState(None)
    # continuous-response keys
    if keystatus[sdl2.SDL_SCANCODE_LEFT]:
        camera.pan(cubic.Point(1, 0))
    if keystatus[sdl2.SDL_SCANCODE_RIGHT]:
        camera.pan(cubic.Point(-1, 0))
    if keystatus[sdl2.SDL_SCANCODE_UP]:
        camera.pan(cubic.Point(0, 1))
    if keystatus[sdl2.SDL_SCANCODE_DOWN]:
        camera.pan(cubic.Point(0, -1))

    for event in sdl2.ext.get_events():
        if event.type == sdl2.SDL_QUIT:
            sdl2.ext.quit()

        elif (event.type == sdl2.SDL_MOUSEBUTTONDOWN
              and not game.current_player.ai):
            mousepos_cube = gfx.get_cube_mousepos(game.current_player.camera.layout)
            mousepos_tile = game.world.get(mousepos_cube)
            tilepair = mousepos_cube, mousepos_tile
            if mousepos_cube in game.world:
                print(mousepos_cube, mousepos_tile, mousepos_tile.owner)
                if mousepos_tile.army:
                    print(mousepos_tile.army, mousepos_tile.army.owner)
                neighbours = str()
                for neighbour in cubic.get_nearest_neighbours(mousepos_cube):
                    neighbours += str(neighbour)
                print('neighbours:', neighbours)
            if mousepos_tile:
                game.current_player.click_on_tile(tilepair)

        elif event.type == sdl2.SDL_MOUSEWHEEL:
            camera.zoom(event.wheel.y)

def is_running(game):
    """Returns False if there is one or less undefeated players."""
    count = 0
    for player in game.players:
        if not player.is_defeated:
            count += 1
    if count > 1:
        return True
    return False

def run():
    """The main game loop.

    Credit: https://gamedev.stackexchange.com/questions/81767/
    """
    game = Game()
    game.current_player.actions = 0
    camera = game.current_player.camera

    minimum_fps = 40
    target_pps = 100
    target_tps = 1
    target_fps = 60

    # Time that must elapse before a new run
    time_per_poll = 1000 / target_pps
    time_per_tick = 1000/ target_tps
    time_per_frame = 1000 / target_fps
    max_frame_skip = (1000 / minimum_fps) / time_per_tick

    achieved_pps = 0
    achieved_fps = 0
    achieved_tps = 0

    timer = sdl2.SDL_GetTicks()

    loops = 0

    achieved_loops = 0

    curr_time = 0
    loop_time = 0

    accumulator_pps = 0
    accumulator_tps = 0
    accumulator_fps = 0

    last_time = sdl2.SDL_GetTicks()

    while is_running(game):
        curr_time = sdl2.SDL_GetTicks()
        loop_time = curr_time - last_time
        last_time = curr_time

        loops = 0

        accumulator_pps += loop_time
        accumulator_tps += loop_time
        accumulator_fps += loop_time

        if accumulator_pps >= time_per_poll:
            poll_inputs(game, camera)
            # player logic goes here
            achieved_pps += 1
            accumulator_pps -= time_per_poll

        while accumulator_tps >= time_per_tick and loops < max_frame_skip:
            game.update_world()
            achieved_tps += 1
            accumulator_tps -= time_per_tick
            loops += 1

        # Max 1 render per loop so player movement stays fluent
        if accumulator_fps >= time_per_frame:
            gfx.update_screen(game, camera)
            achieved_fps += 1
            accumulator_fps -= time_per_frame

        if timer - sdl2.SDL_GetTicks() < 1000:
            timer += 1000
            print(achieved_tps, "TPS,", achieved_fps, "FPS,",
                  achieved_pps, "Polls,", achieved_loops, " Loops")
            achieved_tps = 0
            achieved_fps = 0
            achieved_pps = 0
            achieved_loops = 0

        achieved_loops += 1

if __name__ == "__main__":
    sys.exit(run())

# To do:
# Finish off playergen and worldgen modules
# Gameplay: water, unit tiers, releasing nations, choosing a starting nation
# Camera: rotating, better camera boundary calculation
# Art: sprites, sounds, music, gradual fade-in of locality names
# Multiplayer
# Map editor
# Campaign mode
# UI: game menu, settings menu
# Settings: map dimensions, map generation (bug: starting positions can overwrite one another), map seeds, player generation, colors
# Alternative ruleset: fog of war, border expansion
# AI: more efficient, more skilled
# Spinoff idea: encircling enemy armies liquidates them. Cutting an army off from supply lines (cities) drains manpower. New mobile units. Terrain defense modifiers. Semi-automatic railroad transport system.

# Bugs:
# sort out alpha blending (most likely not possible in sld.gfx - will need to switch to openGL eventually)
# zooming in clips locality names

# Code quality:
# cubic.Cube as a dataclass?
# type hinting
# docstrings
# 140 pylint issues left to resolve

# Done:
# Improved AI, but very inefficient
# Added some docstrings
# Many pylint code quality issues solved
# Merged Game and World classes into one Game class
# Rewrote the click_on_tile Player method
# Transformed regular classes into dataclasses where appropriate
# Player armies are now trained immediatly after the player's turn ends.
# Drawing is now only performed on pixels within camera range (mostly)
# Rendering rate decoupled from the tick rate (to some extent)
# Playergen module which generates players with randomly assigned colors.
# bugfix: negative morale by applying idle army penalty
# bugfix: double turns after defeating a player
# bugfix: stuck legal move indicator
# bugfix: negative morale
# bugfix: zooming could set layout.size to (0,0), causing division by zero error
# bugfix: extending borders now works every time (this bug was caused by a reverse dict lookup)
# bugfix: a rounding error allowing a 0/0 army to persist
# bugfix: floating point morale for some units after applying losing battle morale penalty
# bugfix: morale could surpass max value due to faulty 'minimum morale per 50 manpower' implementation
