"""Camera/layout controls"""
#from math import ceil

import cubic
#from gfx import SCREEN_WIDTH, SCREEN_HEIGHT
#from opengl import SCREEN_WIDTH, SCREEN_HEIGHT
SCREEN_WIDTH, SCREEN_HEIGHT = (1920,1440)
# SCREEN_WIDTH = 1920 # 2048
# SCREEN_HEIGHT = 1080 # 1152

class Camera:
    """The Camera allows a Player to change their view."""
    def __init__(self, layout, world):
        self.layout = layout
        self.world = world
        self.boundary = set()
        self.update_boundary()

    def pan(self, direction):
        """Camera pan."""
        x = direction.x
        y = direction.y
        x *= self.layout.size.x / 1000
        y *= self.layout.size.y / 1000
        self.layout.origin.x += x
        self.layout.origin.y += y

        #self.update_boundary()

    def zoom(self, sign):
        """Camera zoom."""
        self.layout.size.x += sign/150
        #self.layout.origin.x += sign/100
        self.layout.size.x = max(self.layout.size.x, 0.01)
        self.layout.size.x = min(self.layout.size.x, 1)

        self.layout.size.y += sign/150
        #self.layout.origin.y += sign/50
        self.layout.size.y = max(self.layout.size.y, 0.01)
        self.layout.size.y = min(self.layout.size.y, 1)

        #self.update_boundary()

    def update_boundary(self):
        """Calculate cubes within screen bounds."""
        top_left_pixel = cubic.Point(0, 0)
        top_left_cube = cubic.pixel_to_cube(self.layout, top_left_pixel)
        bottom_right_pixel = cubic.Point(SCREEN_WIDTH, SCREEN_HEIGHT)
        bottom_right_cube = cubic.pixel_to_cube(self.layout, bottom_right_pixel)
        self.boundary.clear()
        if self.layout.orientation == cubic.orientation_pointy:
            for cube in self.world:
                if(top_left_cube.q <= cube.q <= bottom_right_cube.q
                   or top_left_cube.r <= cube.r <= bottom_right_cube.r
                   or top_left_cube.s >= cube.s >= bottom_right_cube.s
                   ):
                    self.boundary.add(cube)

        # top_left_cube.r <= cube.r <= bottom_right_cube.r
        # or top_left_cube.q <= cube.q <= bottom_right_cube.q
        # or top_left_cube.s +1 >= cube.s >= bottom_right_cube.s -1

        #else:
        #    pass
        #print('top-left-cube:', top_left_cube, 'bottom-right-rube:', bottom_right_cube)
        #print('top-left-pix:', top_left_pixel, 'bottom-right-pix:', bottom_right_pixel)
        #return cubes_on_screen

#layout = cubic.Layout(cubic.layout_flat, cubic.Point(40,40), cubic.Point(-10,10))
#layout = cubic.Layout(cubic.layout_pointy, cubic.Point(50, 50), cubic.Point(800, 550))
