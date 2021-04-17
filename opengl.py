"""As of yet an unused module."""

import numpy as np
import moderngl
import moderngl_window
from moderngl_window.conf import settings

import cubic
from game import Game

SCREEN_WIDTH, SCREEN_HEIGHT = (2048,1152)
SCREEN_RESOLUTION = cubic.Point(SCREEN_WIDTH, SCREEN_HEIGHT)

settings.WINDOW['class'] = 'moderngl_window.context.sdl2.Window'
#settings.WINDOW['size'] = (1920,1440)
settings.WINDOW['size'] = (SCREEN_WIDTH, SCREEN_HEIGHT)

window = moderngl_window.create_window_from_settings()
ctx = window.ctx

vertex_shader = '''
        #version 330
        layout (location = 0) in vec2 in_cube;
        //layout (location = 1) in int owners;
        layout (location = 1) in vec3 in_color;

        uniform float orientation[9];
        uniform vec2 size;
        uniform vec2 origin;
        //uniform int owners[10981];

        float M[9] = orientation;
        float x = (M[0] * in_cube[0] + M[1] * in_cube[1]) * size.x;
        float y = (M[2] * in_cube[0] + M[3] * in_cube[1]) * size.y;
        vec2 pos = vec2(x, y);
        
        out vec3 v_color;
        void main() {
            gl_Position = vec4(pos + origin, 0.0, 1.0);
            //if (owners == 1) {
            //    v_color = vec3(0.5, 0, 0);
            //} else if (owners == 2) {
            //    v_color = vec3(0, 0.5, 0);
            //} else if (owners == 3) {
            //    v_color = vec3(0, 0, 0.5);
            //} else if (owners == 4) {
            //    v_color = vec3(0, 0.5, 0.5);
            //} else if (owners == 5) {
            //    v_color = vec3(0.2, 0.2, 0.2);
            //} else {
            //    v_color = vec3(1, 1, 1);
            //}

            v_color = in_color;
        }
    '''

geometry_shader_1 = '''
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
    '''

geometry_shader_2 = '''
        #version 330
        #define M_PI 3.1415926535897932384626433832795
        layout (points) in;
        layout (line_strip, max_vertices = 7) out;
        
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

        void build_outline(vec4 pos, float M[9], vec2 size, vec2 origin)
        {
            g_color = vec3(0.5, 0.5, 0.5);
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 0), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 1), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 2), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 3), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 4), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 5), 0.0, 0.0);
            EmitVertex();
            gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 0), 0.0, 0.0);
            EmitVertex();
            EndPrimitive();
        }

        void main() {
            build_outline(gl_in[0].gl_Position, orientation, size, origin);
            g_color = v_color[0];
        }
        '''

# geometry_shader_3 = '''
#         #version 330
#         #define M_PI 3.1415926535897932384626433832795
#         layout (points) in;
#         layout (line_strip, max_vertices = 20) out;
        
#         uniform float orientation[9];
#         uniform vec2 size;
#         uniform vec2 origin;
        
#         in vec3 v_color[];
#         out vec3 g_color;
        
#         vec2 cube_corner_offset(float M[9], vec2 size, float corner)
#         {
#             float angle = 2.0 * M_PI * (M[8] - corner) / 6.0;
#             return vec2(size.x * cos(angle), size.y * sin(angle));
#         }

#         void build_outline(vec4 pos, float M[9], vec2 size, vec2 origin)
#         {
#             g_color = vec3(0.5, 1, 1);
#             gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 0), 0.0, 0.0);
#             EmitVertex();
#             gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 1), 0.0, 0.0);
#             EmitVertex();
#             gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 2), 0.0, 0.0);
#             EmitVertex();
#             gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 3), 0.0, 0.0);
#             EmitVertex();
#             gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 4), 0.0, 0.0);
#             EmitVertex();
#             gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 5), 0.0, 0.0);
#             EmitVertex();
#             gl_Position = pos + vec4(origin + cube_corner_offset(M, size, 0), 0.0, 0.0);
#             EmitVertex();
#             //EndPrimitive();
#         }

#         void main() {
#             build_outline(gl_in[0].gl_Position, orientation, size, origin);
#             g_color = vec3(1,0,1);
#             gl_Position = gl_in[0].gl_Position + vec4(origin,0.0,0.0);
#             EmitVertex();
#             EndPrimitive();
#             g_color = v_color[0];
#         }
#         '''

fragment_shader = '''
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
    '''

def get_vertex_ubo(world):
    coords = [[cube.q, cube.r] for cube in world.keys()]
    offsets = np.array(coords, dtype='f4')
    offsets_buffer = ctx.buffer(offsets)
    return offsets_buffer

def calc_colors_buffer(world):
    tiles = [tile.owner.color for tile in world.values()]
    colors = np.array(tiles, dtype='f4')
    return colors

def get_colors_ubo(world):
    colors = calc_colors_buffer(world)
    colors_buffer = ctx.buffer(colors.astype('f4'))
    return colors_buffer

def init_vao_content(offsets_buffer, colors_buffer):#owners_buffer):
    # The vao_content is a list of 3-tuples (buffer, format, attribs)
    # the format can have an empty or '/v', '/i', '/r' ending.
    # '/v' attributes are the default (per vertex)
    # '/i' attributes are per instance attributes
    # '/r' attributes are default values for the attributes (per render attributes)
    vao_content = [
        (offsets_buffer, '2f', 'in_cube'),
        #(owners_buffer, 'i', 'owners'),
        (colors_buffer, '3f', 'in_color'),
    ]

    return vao_content

# def init_vao_content(world):
#     # Vertex coordinates stored in primitive_corners_buffer
#     #
#     #     E--F
#     #   D/| /|\A
#     #    \|/ |/
#     #     C--B

#     # (Per instance) offsets stored in offsets_uniform
#     # There are n (x_position, y_position) coordinate pairs
#     # World map -> cube(q,r,s) -> cube(x,y) -> offsets
#     # Use a vbo in future instead, applying transformations where needed?

#     # colors = np.array([
#     #     1.0, 0.0, 0.0,
#     #     1.0, 1.0, 0.0,
#     #     1.0, 1.0, 1.0,
#     #     1.0, 0.0, 1.0,
#     #     0.0, 1.0, 1.0,
#     #     0.0, 0.0, 1.0,
#     # ])

#     colors = np.empty(0)
#     offsets = np.empty(0)
#     for cube, tile in world.items():
#         offsets = np.append(offsets, [cube.q, cube.r])
        
#         if not tile.owner:
#             color = np.array([
#                 0.2, 0.2, 0.2,
#             ])
#         else:
#             color = tile.owner.color
#             color = np.array([color.r/255, color.g/255, color.b/255])
#         colors = np.append(colors, color)

#     offsets_buffer = ctx.buffer(offsets.astype('f4'))
#     colors_buffer = ctx.buffer(colors.astype('f4'))

#     #owners = get_owners_buffer(world)
#     #owners_buffer = ctx.buffer(owners.astype('i'))

#     # The vao_content is a list of 3-tuples (buffer, format, attribs)
#     # the format can have an empty or '/v', '/i', '/r' ending.
#     # '/v' attributes are the default (per vertex)
#     # '/i' attributes are per instance attributes
#     # '/r' attributes are default values for the attributes (per render attributes)
#     vao_content = [
#         (offsets_buffer, '2f', 'in_cube'),
#         #(owners_buffer, 'i', 'owners')
#         (colors_buffer, '3f', 'in_color'),
#     ]

#     return vao_content
#     # vao = ctx.vertex_array(prog, vao_content, index_buffer)

#     # vao = ctx.vertex_array(prog, vao_content)
#     # return vao

def single_hex_vao(cube):
    # if cube in world.items()
    # pos = cubic.cube_to_pixel(cube)
    # x = pos.x / SCREEN_WIDTH
    # y = pos.y / SCREEN_HEIGHT
    # pos = cubic.Point(x, y)
    
    color = np.array([1, 1, 0,])
    offsets = np.array([cube.q, cube.r])
    offsets_buffer = ctx.buffer(offsets.astype('f4'))
    color_buffer = ctx.buffer(color.astype('f4'))

    vao_content = [
        (offsets_buffer, '2f', 'in_cube'),
        (color_buffer, '3f', 'in_color'),
    ]
    return vao_content

def update_uniforms(program, camera, world):
    layout = camera.layout
    M = layout.orientation
    size = layout.size
    origin = layout.origin
    owners = []#[tile.owner.name for tile in world.values()]
    for tile in world.values():
        if tile.owner:
            if tile.owner.name == 'Redosia':
                owners.append(1)
            elif tile.owner.name == 'Bluegaria':
                owners.append(2)
            elif tile.owner.name == 'Greenland':
                owners.append(3)
            elif tile.owner.name == 'Violetnam':
                owners.append(4)
        else:
            owners.append(5)

    size_uniform = program['size']
    origin_uniform = program['origin']
    orientation_uniform = program['orientation']
    # if program.get('owners', False):
    #     tile_owners_uniform = program['owners']
    #     tile_owners_uniform.value = owners

    size_uniform.value = size.x, size.y
    origin_uniform.value = origin.x, origin.y
    orientation_uniform.value = [M.f0, M.f1, M.f2, M.f3,
                           M.b0, M.b1, M.b2, M.b3,
                           M.start_angle]
    

# def render(window, vao):
#     # window.ctx.clear(0.5,0.2,0.1)
#     #vao.render(instances=20000)
#     vao.render(mode=moderngl.POINTS) #instances=10981,

def update_screen(vao_content, game):
    #while not window.is_closing:
    window.clear()
    camera = game.current_player.camera
    selection = game.current_player.selection

    prog = ctx.program(
    vertex_shader=vertex_shader,
    geometry_shader=geometry_shader_1,
    fragment_shader=fragment_shader,
    )
    vao1 = ctx.vertex_array(prog, vao_content)

    prog_2 = ctx.program(
        vertex_shader=vertex_shader,
        geometry_shader=geometry_shader_2,
        fragment_shader=fragment_shader,
    )
    vao2 = ctx.vertex_array(prog_2, vao_content)

    # prog_3 = ctx.program(
    #     vertex_shader=vertex_shader,
    #     geometry_shader=geometry_shader_3,
    #     fragment_shader=fragment_shader,
    # )
    # vao3 = ctx.vertex_array(prog_3, vao_content)

    update_uniforms(prog, camera, game.world)
    vao1.render(mode=moderngl.POINTS)

    update_uniforms(prog_2, camera, game.world)
    vao2.render(mode=moderngl.POINTS)

    # update_uniforms(prog_3, camera)
    # vao3.render(mode=moderngl.POINTS)

    if selection:
        #print(selection[0])
        cube = selection[0]
        vao4 = ctx.vertex_array(prog, single_hex_vao(cube))
        vao4.render(mode=moderngl.POINTS)

    window.swap_buffers()


# game = Game()
# camera = game.current_player.camera
# vao = init(game, camera)
# while not window.is_closing:
#     update_screen(vao, camera, game.world)
