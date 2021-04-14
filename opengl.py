"""As of yet an unused module."""

import numpy as np
import moderngl
import moderngl_window
from moderngl_window.conf import settings

import cubic
from game import Game

settings.WINDOW['class'] = 'moderngl_window.context.sdl2.Window'

window = moderngl_window.create_window_from_settings()
ctx = window.ctx

prog = ctx.program(
    vertex_shader='''
        #version 330
        layout (location = 0) in vec2 in_cube;
        layout (location = 1) in vec3 in_color;

        uniform float orientation[9];
        uniform vec2 size;
        uniform vec2 origin;

        float M[9] = orientation;
        float x = (M[0] * in_cube[0] + M[1] * in_cube[1]) * size.x;
        float y = (M[2] * in_cube[0] + M[3] * in_cube[1]) * size.y;
        vec2 pos = vec2(x, y);
        
        out vec3 v_color;
        void main() {
            gl_Position = vec4(pos + origin, 0.0, 1.0);
            v_color = in_color;
        }
    ''',
    geometry_shader='''
        #version 330
        #define M_PI 3.1415926535897932384626433832795
        layout (points) in;
        layout (triangle_strip, max_vertices = 6) out;
        
        uniform float orientation[9];
        uniform vec2 size;
        uniform vec2 origin;
        
        in vec3 v_color[];
        out vec3 g_color;
        
        vec2 cube_corner_offset(float M[9], vec2 size, float corner)
        {
            float angle = 2.0 * M_PI * (M[8] - corner) / 6.0;
            return vec2(size.x * cos(angle), size.y * sin(angle));
        }
        
        void build_hexagon(vec4 pos, float M[9], vec2 size, vec2 origin)
        {
            g_color = v_color[0];
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 0), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 1), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 5), 0.0, 0.0);
            //g_color = vec3(1.0, 1.0, 1.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 2), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 4), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 3), 0.0, 0.0);
            EmitVertex();
            EndPrimitive();
        }
        
        void main() {
            g_color = v_color[0];
            build_hexagon(gl_in[0].gl_Position, orientation, size, origin);
        }
    ''',
    fragment_shader='''
        #version 330
        in vec3 g_color;
        out vec4 f_color;
        
        bool point_is_inside_inner_hexagon = true;
        
        //if (
        
        void main() {
            if (point_is_inside_inner_hexagon) {
                f_color = vec4(g_color, 1.0); 
            } else { f_color = vec4(0.0, 0.0, 0.0, 1.0); }
        }
    ''',
)


def get_offsets(visible_world):
    offsets = np.empty(0)
    for cube in visible_world:
        offsets = np.append(offsets, cube.q)
        offsets = np.append(offsets, cube.r)
    return offsets

def init(game, camera):
    # Vertex coordinates stored in primitive_corners_buffer
    #
    #     E--F
    #   D/| /|\A
    #    \|/ |/
    #     C--B

    world = game.world
    layout = camera.layout
    M = layout.orientation
    size = layout.size
    origin = layout.origin

    # Uniforms
    size_uniform = prog['size']
    origin_uniform = prog['origin']
    orientation_uniform = prog['orientation']

    size_uniform.value = size.x, size.y
    origin_uniform.value = origin.x, origin.y
    orientation_uniform.value = [M.f0, M.f1, M.f2, M.f3,
                           M.b0, M.b1, M.b2, M.b3,
                           M.start_angle]

    # (Per instance) offsets stored in offsets_uniform
    # There are n (x_position, y_position) coordinate pairs
    # World map -> cube(q,r,s) -> cube(x,y) -> offsets
    # Use a vbo in future instead, applying transformations where needed?

    # colors = np.array([
    #     1.0, 0.0, 0.0,
    #     1.0, 1.0, 0.0,
    #     1.0, 1.0, 1.0,
    #     1.0, 0.0, 1.0,
    #     0.0, 1.0, 1.0,
    #     0.0, 0.0, 1.0,
    # ])

    colors = np.empty(0)
    offsets = np.empty(0)
    for cube, tile in world.items():
        offsets = np.append(offsets, cube.q)
        offsets = np.append(offsets, cube.r)
        
        if not tile.owner:
            color = np.array([
                0.2, 0.2, 0.2,
            ])
        else:
            color = tile.owner.color
            color = np.array([color.r/255, color.g/255, color.b/255])

        colors = np.append(colors, color)

    offsets_buffer = ctx.buffer(offsets.astype('f4'))
    color_buffer = ctx.buffer(colors.astype('f4'))

    # The vao_content is a list of 3-tuples (buffer, format, attribs)
    # the format can have an empty or '/v', '/i', '/r' ending.
    # '/v' attributes are the default (per vertex)
    # '/i' attributes are per instance attributes
    # '/r' attributes are default values for the attributes (per render attributes)
    vao_content = [
        (offsets_buffer, '2f', 'in_cube'),
        (color_buffer, '3f', 'in_color'),
    ]

    # vao = ctx.vertex_array(prog, vao_content, index_buffer)
    vao = ctx.vertex_array(prog, vao_content)
    return vao

#def create_vao(camera):



def update_uniforms(camera):
    layout = camera.layout
    M = layout.orientation
    size = layout.size
    origin = layout.origin

    size_uniform = prog['size']
    origin_uniform = prog['origin']
    orientation_uniform = prog['orientation']

    size_uniform.value = size.x, size.y
    origin_uniform.value = origin.x, origin.y
    orientation_uniform.value = [M.f0, M.f1, M.f2, M.f3,
                           M.b0, M.b1, M.b2, M.b3,
                           M.start_angle]

def render(window, vao):
    # window.ctx.clear(0.5,0.2,0.1)
    #vao.render(instances=20000)
    vao.render(mode=moderngl.POINTS) #instances=10981,


def update_screen(vao, camera, world):
    #while not window.is_closing:
    update_uniforms(camera)
    window.clear()
    render(window, vao)
    window.swap_buffers()


# game = Game()
# camera = game.current_player.camera
# vao = init(game, camera)
# while not window.is_closing:
#     update_screen(vao, camera, game.world)
