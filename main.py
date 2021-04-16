"""Honeycomb Empire: The main loop."""
import sys
import ctypes
import time

import sdl2
import sdl2.ext

import opengl
#import gfx
import cubic
from game import Game

def get_pixel_mousepos():
    """Returns the mouse position in pixel coordinates."""
    x, y = ctypes.c_int(0), ctypes.c_int(0)
    _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
    return cubic.Point(x.value, y.value)

def translate_pixel_coordinates(point):
    # 1440x900 -> -1, 0, +1
    x = (point.x / opengl.SCREEN_WIDTH)*2 - 1
    y = -(point.y / opengl.SCREEN_HEIGHT)*2 + 1
    res = cubic.Point(x, y)
    return res

def get_cube_mousepos(layout):
    """Returns the mouse position in cubic coordinates."""
    pixel_mousepos = get_pixel_mousepos()
    pixel_mousepos = translate_pixel_coordinates(pixel_mousepos)
    cube_mousepos = cubic.pixel_to_cube(layout, pixel_mousepos) # 3 floats
    nearest_cube = cubic.cube_round(cube_mousepos)
    print(pixel_mousepos)
    return nearest_cube

def poll_inputs(game, camera):
    """Listens for user input."""

    # event = sdl2.SDL_MOUSEWHEEL
    # event = sdl2.SDL_Event(sdl2.SDL_MOUSEWHEEL)
    # while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
    #     camera.zoom(event.wheel.y)

    for event in sdl2.ext.get_events():
        #print(event)
        if event.type == sdl2.SDL_QUIT:
            sdl2.ext.quit()

        elif event.type == sdl2.SDL_MOUSEWHEEL:
            camera.zoom(event.wheel.y)

        elif (event.type == sdl2.SDL_MOUSEBUTTONDOWN
            and not game.current_player.ai):
            mousepos_cube = get_cube_mousepos(game.current_player.camera.layout)
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
            else:
                print('clic')
            if mousepos_tile:
                print('click on tile')
                game.current_player.click_on_tile(tilepair)

    #sdl2.SDL_PumpEvents() # unsure if necessary
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
    sdl2.SDL_GL_SetSwapInterval(0)

    game = Game()
    game.current_player.actions = 0
    camera = game.current_player.camera
    vao_content = opengl.get_vao_content(game.world)

    minimum_fps = 30
    target_pps = 60
    target_tps = 1
    target_fps = 60
    fps_values = []

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

        poll_inputs(game, camera)

        # if accumulator_pps >= time_per_poll:
        #     poll_inputs(game, camera)
        #     # player logic goes here
        #     achieved_pps += 1
        #     accumulator_pps -= time_per_poll

        while accumulator_tps >= time_per_tick and loops < max_frame_skip:
            vao_content = game.update_world()
            achieved_tps += 1
            accumulator_tps -= time_per_tick
            loops += 1

        # Max 1 render per loop so player movement stays fluent
        if accumulator_fps >= time_per_frame:
            #gfx.update_screen(game, camera)
            #print('tpf: ', time_per_frame)
            #print('acc fps: ', accumulator_fps)
            opengl.update_screen(vao_content, game)
            achieved_fps += 1
            accumulator_fps -= time_per_frame

        if timer - sdl2.SDL_GetTicks() < 1000:
            timer += 1000
            fps_values.append(achieved_fps)
            ave_fps = int(sum(fps_values) / len(fps_values))
            print(achieved_tps, 'TPS,', achieved_fps, 'FPS,',
                 achieved_pps, 'Polls,', achieved_loops, 'Loops,',
                 ave_fps, 'ave FPS')
            #print(camera.layout.origin)
            achieved_tps = 0
            achieved_fps = 0
            achieved_pps = 0
            achieved_loops = 0

        achieved_loops += 1

# def run():
#     """The main game loop."""
#     game = Game()
#     game.current_player.actions = 0
#     camera = game.current_player.camera
#     vao_content = opengl.get_vao_content(game, camera)

#     sdl2.SDL_GL_SetSwapInterval(0)

#     start = time.time()
#     n = 0
#     all_fps = []
#     while is_running(game):
#         n += 1
#         current = time.time()
#         poll_inputs(game, camera)
#         game.update_world()
#         opengl.update_screen(vao_content, camera, game.world)
#         if n > 10:
#             dt = current - start
#             fps = (1/dt)
#             all_fps.append(fps)
#             print('fps:', fps)
#             print('average fps:', sum(all_fps)/len(all_fps))
#             start = current

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