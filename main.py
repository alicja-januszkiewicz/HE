"""The almighty Hello World! example"""
import sys, random
from math import sin, pi, floor
import ctypes

import sdl2.ext
import sdl2.sdlgfx
#from draw import drawRegularHexagon

import logic

SCREEN_WIDTH = 2048
SCREEN_HEIGHT = 1152

def sdl_init():
    sdl2.ext.init()
    global window, renderflags, context
    window = sdl2.ext.Window("Hello World!", size=(SCREEN_WIDTH, SCREEN_HEIGHT))
    window.show()
    # Create a rendering context for the window. The sdlgfx module requires it.
    # NOTE: Defaults to software rendering to avoid flickering on some systems.
    if "-hardware" in sys.argv:
        renderflags = sdl2.render.SDL_RENDERER_ACCELERATED | sdl2.render.SDL_RENDERER_PRESENTVSYNC
    else:
        renderflags = sdl2.render.SDL_RENDERER_SOFTWARE
    context = sdl2.ext.Renderer(window, flags=renderflags)

def fun():
        context.clear(0)
        draw_random_hexagons()
        context.present()
        sdl2.SDL_Delay(100)

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

def draw_random_hexagons():
    for _ in range(1000):
        color = random.randint(0, 0xFFFFFFFF)
        x = random.randint(0,SCREEN_WIDTH)
        y = random.randint(0,SCREEN_HEIGHT)
        size = random.randint(10,100)
        draw_regular_hexagon(context, x, y, size, color)

def draw_hex_grid(maxx, maxy):
    size = 40
    color = 0xFF00FFFF
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




def run():
    sdl_init()

    draw_hex_grid(20,10)
    context.present()
    turn = 0
    players = logic.initialise_players()
    world = logic.generate_empty_world()
    for player in players:
        player.selection = world[0]
    logic.add_starting_areas(world, players)

    running = len(players) > 1
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        turn += 1
        if turn >= 100000: break
        for tile in world:
            tile.generate_units()
        if (turn % 2 == 0):
            print("Turn:", turn)
            logic.print_world_state(world)
        for player in players:
            player.actions = 5
            if player.ai == True:
                while player.actions > 0 and logic.check_for_any_units(world, player):
                    logic.ai_controller(world, player)
        if len(players) <= 1:
            for i in range(1000):
                print(i, len(players), running)
            break
            #else:
                #get_human_event()

    
    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())