import ctypes
import random
from math import pi, sin, floor, sqrt

import sdl2.sdlgfx

import cubic
from gfx import SCREEN_HEIGHT, SCREEN_WIDTH, sprite_factory, sprite_renderer
from main import ZOOM_LEVEL

RESOURCES = sdl2.ext.Resources(__file__, "resources")
sprite = sprite_factory.from_image(RESOURCES.get_path("army.bmp"))

LAYOUT = cubic.Layout(cubic.layout_flat, cubic.Point(40,40), cubic.Point(-10,0))
SIZE = LAYOUT.size

def hexagon(context, cube, color):
    corners = cubic.polygon_corners(LAYOUT, cube)
    n = len(corners)

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i, corner in enumerate(corners):
        xlist[i] = int(floor(corner.x))
        ylist[i] = int(floor(corner.y))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    sdl2.sdlgfx.filledPolygonColor(context.sdlrenderer, xptr, yptr, n, color)
    sdl2.sdlgfx.polygonColor(context.sdlrenderer, xptr, yptr, n, 0xFF000000)

def circle(context, x, y, radius, color):
    x, y = int(floor(x)), int(floor(y))
    radius = int(floor(radius))
    sdl2.sdlgfx.filledCircleColor(context.sdlrenderer, x, y, radius, color)

def army_info(context, tilepair):
    coord, tile = tilepair
    pos = cubic.cube_to_pixel(LAYOUT, coord)
    r = round(SIZE.x * sqrt(3)/2)
    x = round(pos.x)
    y = round(pos.y)
    sdl2.sdlgfx.filledPieColor(context.sdlrenderer, x, y, r, 315, 135, 0xBBFFFFFF)
    sdl2.sdlgfx.filledPieColor(context.sdlrenderer, x, y, r, 135, 315, 0xBB000000)

def game_tile(context, tilepair):
    cube, tile = tilepair
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
    hexagon(context, cube, color)

def base_game_tile(context, tilepair):
    cube, _ = tilepair
    color = 0xFFAAAAAA
    hexagon(context, cube, color)

def tile_army(context, tilepair):
    cube, tile = tilepair
    if tile.army.manpower > 0:
        pos = cubic.cube_to_pixel(LAYOUT, cube)
        x, y = pos[0], pos[1]
        #sprite_renderer.render(sprite, round(x)-30, round(y)-30)
        h = sin(pi/3)
        r = SIZE.x / 8
        x = (pos.x + 1/4 * r)
        y = (pos.y + h * 1/2 * r)
        color = 0xFF000000
        circle(context, x, y, r, color)

def tile_structs(context, tilepair):
    cube, tile = tilepair
    pos = cubic.cube_to_pixel(LAYOUT, cube)
    x = pos[0]
    y = pos[1]
    size = SIZE
    r = sqrt(size.x**2 + size.y**2) / 5*sqrt(2)
    color = 0xFFDD0000

    is_army_present = tile.army.manpower > 0
    if tile.structures == "City":
        if (is_army_present == True):
            x += 1/2 * size.x
        circle(context, x, y, r/2, color)
    elif tile.structures == "Capital":
        if (is_army_present == True):
            x += 1/2 * size.x
            r /= 2
        circle(context, x, y, r, color)

def tile_selector(context, cube):
    color = 0x88d0e040
    hexagon(context, cube, color)

def legal_move_indicator(context, cube):
    color = 0x8800ffff
    hexagon(context, cube, color)