"""As of yet an unused module."""
import math
import numpy as np

import sdl2
import moderngl
import moderngl_window
from moderngl_window.conf import settings

# (math.sin(time) + 1.0) / 2,
# (math.sin(time + 2) + 1.0) / 2,
# (math.sin(time + 3) + 1.0) / 2,

settings.WINDOW['class'] = 'moderngl_window.context.sdl2.Window'
settings.WINDOW['gl_version'] = (4, 5)

window = moderngl_window.create_window_from_settings()
ctx = window.ctx

vertices = np.array([
    # x, y, red, green, blue
    0.0, 1.0, 1.0, 0.1, 0.3,
    -1.0, -1.0, 0.5, 0.5, 0.3,
    1.0, -1.0, 0.1, 1.0, 0.3,
], dtype='f4')

vbo = ctx.buffer(vertices)

prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                in vec3 in_color;
                out vec3 v_color;    // Goes to the fragment shader
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_color = in_color;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_color;
                out vec4 f_color;
                void main() {
                    // We're not interested in changing the alpha value
                    f_color = vec4(v_color, 1.0);
                }
            ''',
        )

# We control the 'in_vert' and `in_color' variables
vao = ctx.vertex_array(
    prog,
    [
        # Map in_vert to the first 2 floats
        # Map in_color to the next 3 floats
        (vbo, '2f 3f', 'in_vert', 'in_color')
    ],
)

def render(window):
    #window.ctx.clear(0.5,0.2,0.1)
    vao.render()

while not window.is_closing:
    window.clear()
    render(window)
    window.swap_buffers()
