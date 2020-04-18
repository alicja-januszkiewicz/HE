import ctypes
import random
from math import pi, sin, floor, sqrt

import sdl2.sdlgfx

import cube
from main import SCREEN_HEIGHT, SCREEN_WIDTH, ZOOM_LEVEL

LAYOUT = cube.Layout(cube.layout_flat, cube.Point(40,40), cube.Point(0,0))
SIZE = LAYOUT.size

def draw_regular_hexagon(context, x, y, size, color):
    # Geometry
    h = -sin(pi/3)
    vx = (x, x+size.x, x+3*size.x/2, x+size.x, x, x-size.x/2)
    vy = (y, y, y-h*size.y, y-2*h*size.y, y-2*h*size.y, y-h*size.y)
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

def draw_game_tile(tilepair, context):
    coord, tile = tilepair
    pos = cube.cube_to_pixel(LAYOUT, coord)
    x, y = pos[0], pos[1]
    size = LAYOUT.size
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

def draw_tile_units(tilepair, context):
    coord, tile = tilepair
    pos = cube.cube_to_pixel(LAYOUT, coord)
    x, y = pos[0], pos[1]
    h = sin(pi/3)
    size = cube.Point(int(SIZE.x/2), int(SIZE.y/2))
    x = (pos[0] + 1/4 * size.x)
    y = (pos[1] + h * 1/2 * size.y)
    color = 0xFF000000
    if tile.units > 0:
        draw_regular_hexagon(context, x, y, cube.Point(size.x/2, size.y/2), color)

def draw_tile_structs(tilepair, context):
    coord, tile = tilepair
    pos = cube.cube_to_pixel(LAYOUT, coord)
    h = sin(pi/3)
    size = SIZE
    x = pos[0] + 1/2 * size.x
    y = pos[1] + h * size.y
    color = 0xFFDD0000
    are_units_present = tile.units > 0
    r = sqrt(size.x**2 + size.y**2) / 3*sqrt(2)
    if tile.structures == "City":
        if (are_units_present == True):
            x += 1/2 * size.x
        draw_circle(context, x, y, r/3, color)
    elif tile.structures == "Capital":
        if (are_units_present == True):
            x += 1/2 * size.x
            r /= 2
        draw_circle(context, x, y, r, color)

def draw_tile_selector(cube_, context):
    pos = cube.cube_to_pixel(LAYOUT, cube_)
    x, y = pos[0], pos[1]
    size = SIZE
    color = 0x33d0e040
    draw_regular_hexagon(context, x, y, size, color)

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