import ctypes
import random
from math import pi, sin, floor, sqrt

import sdl2.sdlgfx

import cube
from gfx import SCREEN_HEIGHT, SCREEN_WIDTH
from main import ZOOM_LEVEL

LAYOUT = cube.Layout(cube.layout_flat, cube.Point(40,40), cube.Point(-10,0))
SIZE = LAYOUT.size

def hexagon(context, cube_, color):
    corners = cube.polygon_corners(LAYOUT, cube_)
    n = len(corners)

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i in range(n):
        xlist[i] = int(floor(corners[i].x))
        ylist[i] = int(floor(corners[i].y))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    sdl2.sdlgfx.filledPolygonColor(context.sdlrenderer, xptr, yptr, n, color)

def circle(context, x, y, radius, color):
    x, y = int(floor(x)), int(floor(y))
    radius = int(floor(radius))
    sdl2.sdlgfx.filledCircleColor(context.sdlrenderer, x, y, radius, color)

def game_tile(tilepair, context):
    coord, tile = tilepair
    if (tile.owner == None):
        color = 0xFFAAAAAA
    elif (tile.owner.id == "Redosia"):
        color = 0xAA0000FF
    elif (tile.owner.id == "Bluegaria"):
        color = 0xAAd0e040
    elif (tile.owner.id == "Greenland"):
        color = 0xAA00FF00
    elif (tile.owner.id == "Violetnam"):
        color = 0xAA800080
    hexagon(context, coord, color)

def tile_units(tilepair, context):
    coord, tile = tilepair
    if tile.units > 0:
        pos = cube.cube_to_pixel(LAYOUT, coord)
        x, y = pos[0], pos[1]
        h = sin(pi/3)
        r = SIZE.x / 8
        x = (pos[0] + 1/4 * r)
        y = (pos[1] + h * 1/2 * r)
        color = 0xFF000000
        circle(context, x, y, r, color)

def tile_structs(tilepair, context):
    coord, tile = tilepair
    pos = cube.cube_to_pixel(LAYOUT, coord)
    x = pos[0]
    y = pos[1]
    size = SIZE
    r = sqrt(size.x**2 + size.y**2) / 5*sqrt(2)
    color = 0xFFDD0000

    are_units_present = tile.units > 0
    if tile.structures == "City":
        if (are_units_present == True):
            x += 1/2 * size.x
        circle(context, x, y, r/2, color)
    elif tile.structures == "Capital":
        if (are_units_present == True):
            x += 1/2 * size.x
            r /= 2
        circle(context, x, y, r, color)

def tile_selector(cube_, context):
    color = 0x88d0e040
    hexagon(context, cube_, color)

def legal_move_indicator(cube_, context):
    color = 0x8800ffff
    hexagon(context, cube_, color)