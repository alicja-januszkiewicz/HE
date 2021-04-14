"""Drawing routines used by the gfx module."""
import ctypes
from math import pi, sin, floor, sqrt, ceil

import sdl2.sdlgfx

import cubic
from gfx import sprite_factory
from playergen import set_color

RESOURCES = sdl2.ext.Resources(__file__, "resources")
army_sprite = sprite_factory.from_image(RESOURCES.get_path("army.png"))
font_manager = sdl2.ext.FontManager('resources/Iceberg-Regular.ttf', size=18)
tile_sprite = sprite_factory.from_image(RESOURCES.get_path('basetile3.png'))

def hexagon(context, layout, cube, color):
    corners = cubic.polygon_corners(layout, cube)
    n = len(corners)

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i, corner in enumerate(corners):
        xlist[i] = int(floor(corner.x))
        ylist[i] = int(floor(corner.y))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    sdl2.sdlgfx.filledPolygonColor(context.sdlrenderer, xptr, yptr, n, color)
    #sdl2.sdlgfx.polygonColor(context.sdlrenderer, xptr, yptr, n, 0x99999999)

def hexagon_rgba(context, layout, cube, color):
    corners = cubic.polygon_corners(layout, cube)
    n = len(corners)

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i, corner in enumerate(corners):
        xlist[i] = int(floor(corner.x))
        ylist[i] = int(floor(corner.y))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    sdl2.sdlgfx.filledPolygonRGBA(context.sdlrenderer, xptr, yptr,
                                  n, color.r, color.g, color.b, 120)

def hexagon_rgba2(context, layout, cube, color):
    corners = cubic.polygon_corners(layout, cube)
    n = len(corners)

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i, corner in enumerate(corners):
        xlist[i] = int(floor(corner.x))
        ylist[i] = int(floor(corner.y))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    sdl2.sdlgfx.filledPolygonRGBA(context, xptr, yptr,
                                  n, color[0], color[1], color[2], 120)

def hexagon_black(context, layout, cube):
    corners = cubic.polygon_corners(layout, cube)
    n = len(corners)

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i, corner in enumerate(corners):
        xlist[i] = int(floor(corner.x))
        ylist[i] = int(floor(corner.y))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    sdl2.sdlgfx.filledPolygonColor(context.sdlrenderer, xptr, yptr, n, 0x00000000)

def hexagon_textured(context, layout, cube, texture):
    corners = cubic.polygon_corners(layout, cube)
    n = len(corners)

    # Casting to ctypes
    xlist, ylist = (sdl2.Sint16 * n)(), (sdl2.Sint16 * n)()
    for i, corner in enumerate(corners):
        xlist[i] = int(floor(corner.x))
        ylist[i] = int(floor(corner.y))
    xptr = ctypes.cast(xlist, ctypes.POINTER(sdl2.Sint16))
    yptr = ctypes.cast(ylist, ctypes.POINTER(sdl2.Sint16))

    sdl2.sdlgfx.texturedPolygon(context.renderer, xptr, yptr, n, texture, 0, 0)

def circle(context, x, y, radius, color):
    x, y = int(floor(x)), int(floor(y))
    radius = int(floor(radius))
    sdl2.sdlgfx.filledCircleColor(context.sdlrenderer, x, y, radius, color)

def game_tile_primitive(context, layout, tilepair):
    cube, tile = tilepair
    color = set_color(tile)
    hexagon_rgba(context, layout, cube, color)

def game_tile_sprite(context, layout, tilepair):
    cube, tile = tilepair
    corners = cubic.polygon_corners(layout, cube)
    heigth = ceil(corners[4].y - corners[2].y) +1
    width = ceil(corners[0].x - corners[3].x) +1
    rect = (floor(corners[3].x), floor(corners[2].y), width, heigth)

    color = set_color(tile)
    sprite = tile_sprite
    sdl2.SDL_SetTextureColorMod(sprite.texture, color.r, color.g, color.b)
    context.copy(sprite, None, rect)
    #hexagon_textured(context, layout, cube, sfcbasetile.surface) <--- this function is broken

def tile_army(context, layout, tilepair):
    cube, tile = tilepair
    pos = cubic.cube_to_pixel(layout, cube)
    x, y = pos.x, pos.y
    h = sin(pi/3)
    r = layout.size.x / 8
    x = (pos.x + 1/4 * r)
    y = (pos.y + h * 1/2 * r)
    width = round(layout.size.x * 3/2)
    heigth = round(layout.size.y * 3/2)
    rect = (round(x-width/2), round(y-heigth/2), width, heigth)

    color = set_color(tile)
    sprite = army_sprite
    sdl2.SDL_SetTextureColorMod(sprite.texture, color.r, color.g, color.b)

    context.copy(sprite.texture, None, rect)

def tile_locality(context, layout, tilepair):
    cube, tile = tilepair
    pos = cubic.cube_to_pixel(layout, cube)
    x = pos.x
    y = pos.y
    r = sqrt(layout.size.x**2 + layout.size.y**2) / 5*sqrt(2)
    color = 0xFFDD0000

    if tile.locality.category == "City":
        if tile.army:
            x += 2/3 * layout.size.x
        circle(context, x, y, r/2, color)
    elif tile.locality.category == "Capital":
        if tile.army:
            x += 2/3 * layout.size.x
            r /= 2
        circle(context, x, y, r, color)

def tile_selector(context, layout, cube):
    color = 0x88d0e040
    hexagon(context, layout, cube, color)

def legal_move_indicator(context, layout, cube):
    color = 0x8800ffff
    hexagon(context, layout, cube, color)

def army_can_move_indicator(context, layout, cube):
    legal_move_indicator(context, layout, cube)

def text(context, layout, string_to_render, x, y, width=None, color=None):
    sfc = font_manager.render(string_to_render, size=round(layout.size.x/2),
                              width=width, color=color)
    texture = sdl2.render.SDL_CreateTextureFromSurface(context.sdlrenderer,
                                                       sfc)
    sprite = sdl2.ext.TextureSprite(texture)
    dx = round(-1/2 * sprite.size[0]) # centers the text
    context.copy(texture.contents, dstrect=(x + dx, y,
                                            sprite.size[0], sprite.size[1]))

def city_name(context, layout, tilepair):
    cube, tile = tilepair
    pos = cubic.cube_to_pixel(layout, cube)
    x = pos.x
    y = pos.y - layout.size.y * 1.15

    text(context, layout, tile.locality.name, round(x), round(y), 100)

def army_info_text(context, layout, tilepair):
    coord, tile = tilepair
    pos = cubic.cube_to_pixel(layout, coord)
    x = round(pos.x - layout.size.x * 0.2)
    y = round(pos.y - layout.size.y/2)
    text(context, layout, str(tile.army.manpower), x, y)
    x = round(pos.x + layout.size.x * 0.2)
    y = round(pos.y)
    text(context, layout, str(tile.army.morale), x, y, color=(255, 0, 0))

def army_info_backdrop(context, layout, tilepair):
    coord, _ = tilepair
    pos = cubic.cube_to_pixel(layout, coord)
    r = round(layout.size.x * sqrt(3)/2 * 0.8)
    x = round(pos.x)
    y = round(pos.y)
    sdl2.sdlgfx.filledPieColor(context.sdlrenderer, x, y, r, 315, 135, 0xBBFFFFFF)
    sdl2.sdlgfx.filledPieColor(context.sdlrenderer, x, y, r, 135, 315, 0xBB000000)

def army_info(context, layout, tilepair):
    army_info_backdrop(context, layout, tilepair)
    army_info_text(context, layout, tilepair)
