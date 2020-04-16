import ctypes
import random
from math import pi, sin, floor

import sdl2.sdlgfx

from main import SCREEN_HEIGHT, SCREEN_WIDTH, ZOOM_LEVEL

def draw_regular_hexagon(context, x, y, size, color):
    # Geometry
    h = -sin(pi/3)
    vx = (x, x+size, x+3*size/2, x+size, x, x-size/2)
    vy = (y, y, y-h*size, y-2*h*size, y-2*h*size, y-h*size)
    n = 6

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i in range(n):
        xlist[i] = int(floor(vx[i]))
        ylist[i] = int(floor(vy[i]))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    # Calling gfx drawing function
    sdl2.sdlgfx.filledPolygonColor(context.sdlrenderer, xptr, yptr, n, color)

def draw_circle(context, x, y, radius, color):
    x, y = int(floor(x)), int(floor(y))
    radius = int(floor(radius))
    sdl2.sdlgfx.filledCircleColor(context.sdlrenderer, x, y, radius, color)

def draw_random_hexagons(context):
    for _ in range(1000):
        color = random.randint(0, 0xFFFFFFFF)
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(10,100)
        draw_regular_hexagon(context, x, y, size, color)

def draw_hex_grid(maxx, maxy, context):
    size = ZOOM_LEVEL
    color = 0xFFAAAAAA
    x,y = size/2,0
    h = sin(pi/3)
    ydelta = 2*size*h
    xdelta = 3*size/2
    shift = 1/2*ydelta
    for column in range(maxx):
        if (column % 2 == 1):
            y += shift
        for _rowElem in range(maxy):
            #color = random.randint(0, 0xFFFFFFFF)
            draw_regular_hexagon(context, x, y, size, color)
            y += ydelta +2
        x += xdelta +2
        y = 0

def draw_game_tile(tile, context):
    pos = map_game_coord_to_pixel_pos(tile.x, tile.y)
    x, y = pos[0], pos[1]
    size = ZOOM_LEVEL
    color = 0xFFAAAAAA
    if (tile.owner.id == "Redosia"):
        color = 0xAA0000FF
    if (tile.owner.id == "Bluegaria"):
        color = 0xAAd0e040
    if (tile.owner.id == "Greenland"):
        color = 0xAA00FF00
    if (tile.owner.id == "Violetnam"):
        color = 0xAA800080
    draw_regular_hexagon(context, x, y, size, color)
    #main.context.present()

def draw_tile_units(tile, context):
    pos = map_game_coord_to_pixel_pos(tile.x, tile.y)
    h = sin(pi/3)
    size = ZOOM_LEVEL
    x = pos[0] + 1/4 * size
    y = pos[1] + h * 1/2 * size
    color = 0xFF000000
    if tile.units > 0:
        draw_regular_hexagon(context, x, y, size/2, color)
        #main.context.present()

def draw_tile_structs(tile, context):
    pos = map_game_coord_to_pixel_pos(tile.x, tile.y)
    h = sin(pi/3)
    size = ZOOM_LEVEL
    x = pos[0] + 1/2 * size
    y = pos[1] + h * size
    color = 0xFFDD0000
    if tile.structures == "Capital":
        draw_circle(context, x, y, size/2, color)
    if tile.structures == "city":
        draw_circle(context, x, y, size/5, color)

def map_game_coord_to_pixel_pos(world_x,world_y):
    size = ZOOM_LEVEL
    h = sin(pi/3)
    ydelta = 2*size*h
    xdelta = 3*size/2
    shift = 1/2*ydelta
    y = world_y * ydelta
    if (world_x % 2 == 1):
        y += shift
    x = world_x * xdelta + size/2
    return x, y

#def fun():
#        context.clear(0)
#        draw_random_hexagons()
#        main.context.present()
#        sdl2.SDL_Delay(100)