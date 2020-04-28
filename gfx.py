import sys
import sdl2.ext

SCREEN_WIDTH = 1920#2048
SCREEN_HEIGHT = 1080#1152

sdl2.ext.init()
#, flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
window = sdl2.ext.Window("Hello World!", size=(SCREEN_WIDTH, SCREEN_HEIGHT))
window.show()
    # Create a rendering context for the window. The sdlgfx module requires it.
    # NOTE: Defaults to software rendering to avoid flickering on some systems.
if "-hardware" in sys.argv:
    renderflags = sdl2.render.SDL_RENDERER_ACCELERATED | sdl2.render.SDL_RENDERER_PRESENTVSYNC
else:
    renderflags = sdl2.render.SDL_RENDERER_SOFTWARE
#renderflags = sdl2.render.SDL_RENDERER_ACCELERATED

context = sdl2.ext.Renderer(window, flags=renderflags)


sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=context)

#sprite_renderer = sprite_factory.create_sprite_render_system(window)
#sdl2.SDL_SetRenderDrawColor(context.renderer, 0, 0, 255, 255)
