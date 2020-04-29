import ctypes
import random
from math import pi, sin, floor, sqrt

import sdl2.sdlgfx

import cubic
from gfx import SCREEN_HEIGHT, SCREEN_WIDTH, sprite_factory
from main import ZOOM_LEVEL

RESOURCES = sdl2.ext.Resources(__file__, "resources")
sprite = sprite_factory.from_image(RESOURCES.get_path("army.bmp"))
#sprite.size = (64,64)

LAYOUT = cubic.Layout(cubic.layout_flat, cubic.Point(40,40), cubic.Point(-10,10))
SIZE = LAYOUT.size

font_manager = sdl2.ext.FontManager('resources/Iceberg-Regular.ttf', size=18)

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
    sdl2.sdlgfx.polygonColor(context.sdlrenderer, xptr, yptr, n, 0x99999999)

def circle(context, x, y, radius, color):
    x, y = int(floor(x)), int(floor(y))
    radius = int(floor(radius))
    sdl2.sdlgfx.filledCircleColor(context.sdlrenderer, x, y, radius, color)

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
    if tile.army:
        pos = cubic.cube_to_pixel(LAYOUT, cube)
        x, y = pos[0], pos[1]
        h = sin(pi/3)
        r = SIZE.x / 8
        x = (pos.x + 1/4 * r)
        y = (pos.y + h * 1/2 * r)
        rect = (round(x)-32, round(y)-32, 64, 64)
        context.copy(sprite.texture, None, rect)

def tile_locality(context, tilepair):
    cube, tile = tilepair
    pos = cubic.cube_to_pixel(LAYOUT, cube)
    x = pos[0]
    y = pos[1]
    size = SIZE
    r = sqrt(size.x**2 + size.y**2) / 5*sqrt(2)
    color = 0xFFDD0000

    if tile.locality.type == "City":
        if (tile.army):
            x += 2/3 * size.x
        circle(context, x, y, r/2, color)
    elif tile.locality.type == "Capital":
        if (tile.army):
            x += 2/3 * size.x
            r /= 2
        circle(context, x, y, r, color)

def tile_selector(context, cube):
    color = 0x88d0e040
    hexagon(context, cube, color)

def legal_move_indicator(context, cube):
    color = 0x8800ffff
    hexagon(context, cube, color)

def text(context, string_to_render, x, y, width=None, color=None):
    sfc = font_manager.render(string_to_render, width=width, color=color)
    texture = sdl2.render.SDL_CreateTextureFromSurface(context.sdlrenderer, sfc)
    sprite = sdl2.ext.TextureSprite(texture)
    dx = round(-1/2 * sprite.size[0]) # centers the text
    context.copy(texture.contents, dstrect=(x + dx , y, sprite.size[0], sprite.size[1]))

def city_name(context, tilepair):
    cube, tile = tilepair
    pos = cubic.cube_to_pixel(LAYOUT, cube)
    x = pos[0]
    y = pos[1] - SIZE.y * 1.15

    if tile.locality.type != None:
        text(context, tile.locality.name, round(x), round(y), 100)

def army_info_text(context, tilepair):
    coord, tile = tilepair
    pos = cubic.cube_to_pixel(LAYOUT, coord)
    x = round(pos.x - SIZE.x * 0.2)
    y = round(pos.y - SIZE.y/2)
    text(context, str(tile.army.manpower), x, y)
    x = round(pos.x + SIZE.x * 0.2)
    y = round(pos.y)
    text(context, str(tile.army.morale), x, y, color=(255,0,0))

def army_info_backdrop(context, tilepair):
    coord, _ = tilepair
    pos = cubic.cube_to_pixel(LAYOUT, coord)
    r = round(SIZE.x * sqrt(3)/2 * 0.8)
    x = round(pos.x)
    y = round(pos.y)
    sdl2.sdlgfx.filledPieColor(context.sdlrenderer, x, y, r, 315, 135, 0xBBFFFFFF)
    sdl2.sdlgfx.filledPieColor(context.sdlrenderer, x, y, r, 135, 315, 0xBB000000)

def army_info(context, tilepair):
    army_info_backdrop(context, tilepair)
    army_info_text(context, tilepair)