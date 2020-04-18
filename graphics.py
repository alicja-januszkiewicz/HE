import sys
import sdl2.ext

SCREEN_WIDTH = 2048
SCREEN_HEIGHT = 1152

sdl2.ext.init()
window = sdl2.ext.Window("Hello World!", size=(SCREEN_WIDTH, SCREEN_HEIGHT))
window.show()
    # Create a rendering context for the window. The sdlgfx module requires it.
    # NOTE: Defaults to software rendering to avoid flickering on some systems.
if "-hardware" in sys.argv:
    renderflags = sdl2.render.SDL_RENDERER_ACCELERATED | sdl2.render.SDL_RENDERER_PRESENTVSYNC
else:
    renderflags = sdl2.render.SDL_RENDERER_SOFTWARE
context = sdl2.ext.Renderer(window, flags=renderflags)