"""The module responsible for initialising a graphics context and
 updating the screen.
 """
import ctypes
import sys

import sdl2.ext

from army import MAX_TRAVEL_DISTANCE
import cubic

SCREEN_WIDTH = 1920 # 2048
SCREEN_HEIGHT = 1080 # 1152

sdl2.ext.init()
window = sdl2.ext.Window(
    "Honeycomb Empire",
    size=(SCREEN_WIDTH, SCREEN_HEIGHT),
    #flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
    )
window.show()

# Create a rendering context for the window. The sdlgfx module requires it.
# NOTE: Defaults to software rendering to avoid flickering on some systems.
if "-hardware" in sys.argv:
    renderflags = sdl2.render.SDL_RENDERER_ACCELERATED | sdl2.render.SDL_RENDERER_PRESENTVSYNC
else:
    renderflags = sdl2.render.SDL_RENDERER_SOFTWARE

context = sdl2.ext.Renderer(window, flags=renderflags)
sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=context)

import draw

def get_pixel_mousepos():
    """Returns the mouse position in pixel coordinates."""
    x, y = ctypes.c_int(0), ctypes.c_int(0)
    _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
    return cubic.Point(x.value, y.value)

def get_cube_mousepos(layout):
    """Returns the mouse position in cubic coordinates."""
    pixel_mousepos = get_pixel_mousepos()
    cube_mousepos = cubic.pixel_to_cube(layout, pixel_mousepos) # 3 floats
    nearest_cube = cubic.cube_round(cube_mousepos)
    return nearest_cube

def update_tile(visible_world, layout,):
    """Draws the base of the tiles making up the game world."""
    for tilepair in visible_world.items():
        draw.game_tile_primitive(context, layout, tilepair)

def update_army_can_move_indicator(game, visible_world, layout, selection):
    """Draws indicators for armies that can still be moved this turn."""
    for tilepair in visible_world.items():
        cube, tile = tilepair
        if (not selection
            and tile.army
            and tile.army.can_move
            and tile.owner == game.current_player
           ):
            draw.army_can_move_indicator(context, layout, cube)

def update_tile_overlay(visible_world, layout):
    """Draws tile objects - armies and localities."""
    for tilepair in visible_world.items():
        _, tile = tilepair
        if tile.army:
            draw.tile_army(context, layout, tilepair)
        if tile.locality:
            draw.tile_locality(context, layout, tilepair)

def update_army_selection(visible_world, layout, selection):
    """Draws legal move indicators for the currently selected army."""
    selection_cube = cubic.Cube(0, 0, 0)
    if selection:
        selection_cube = selection[0]
        for cube in cubic.get_reachable_cubes(visible_world, selection_cube,
                                              MAX_TRAVEL_DISTANCE):
            draw.legal_move_indicator(context, layout, cube)

def update_army_info(visible_world, layout, mousepos_cube):
    """Draws army info overlay for every army within 2 cubes of the cursor."""
    if mousepos_cube in visible_world:
        affected_cubes = set(cubic.get_all_neighbours(mousepos_cube, 2))
        affected_cubes.add(mousepos_cube)
        for cube in affected_cubes:
            if cube not in visible_world:
                continue

            tile = visible_world[cube]
            if tile.army:
                tilepair = cube, tile
                draw.army_info(context, layout, tilepair)

def update_city_names(visible_world, layout, mousepos_cube):
    """Draws names of all localities within 5 cubes of the cursor."""
    if mousepos_cube in visible_world:
        affected_cubes = set(cubic.get_all_neighbours(mousepos_cube, 5))
        affected_cubes.add(mousepos_cube)
        for cube in affected_cubes:
            if cube not in visible_world:
                continue

            tile = visible_world[cube]
            if tile.locality:
                tilepair = cube, tile
                draw.city_name(context, layout, tilepair)

def update_screen(game, camera):
    """The screen drawing routine used in main()."""
    context.clear(0)

    layout = camera.layout
    selection = game.current_player.selection
    mousepos_cube = get_cube_mousepos(layout)

    # Camera boundary is a set of all cubes - tile positions,
    # that can fit on the screen.
    # Here we are checking if they actually do exist, that is,
    # whether they have a tile object associated with them.
    visible_world = dict()
    for cube in camera.boundary:
        tile = game.world.get(cube)
        if tile:
            visible_world[cube] = tile

    update_tile(visible_world, layout)
    update_army_can_move_indicator(game, visible_world, layout, selection)
    update_tile_overlay(visible_world, layout)
    draw.tile_selector(context, layout, mousepos_cube)
    update_army_selection(visible_world, layout, selection)
    update_army_info(visible_world, layout, mousepos_cube)
    update_city_names(visible_world, layout, mousepos_cube)

    context.present()
