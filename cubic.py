from collections import namedtuple
from dataclasses import dataclass
from math import sin, cos, sqrt, pi#, floor, ceil

# def round(value):
#     x = floor(value)
#     if (value - x) < .50:
#         return x
#     else:
#         return ceil(value)

class Cube():
    def __init__(self, q, r, s):
        self.q = q
        self.r = r
        self.s = s
        assert (round(q + r + s) == 0), "q + r + s must be 0"

    def __eq__(self, other):
        t = isinstance(other, Cube)
        if not t: return False
        q = self.q == other.q
        r = self.r == other.r
        s = self.s == other.s
        return(q and r and s)

    def __str__(self):
        return str((self.q, self.r, self.s))

    def __hash__(self):
        return hash((self.q, self.r))

    def __add__(self, other):
        q = self.q + other.q
        r = self.r + other.r
        s = self.s + other.s
        return(Cube(q,r,s))

    def __sub__(self, other):
        q = self.q - other.q
        r = self.r - other.r
        s = self.s - other.s
        return(Cube(q,r,s))

    def get_coord(self):
        return self.q, self.r, self.s


def cube_length(cube):
    return int((abs(cube.q) + abs(cube.r) + abs(cube.s)) / 2)

def cube_distance(cube_a, cube_b):
    return cube_length(cube_a - cube_b)

def cube_direction(direction):
    cube_directions = (
    Cube(+1, -1, 0), Cube(+1, 0, -1), Cube(0, +1, -1), 
    Cube(-1, +1, 0), Cube(-1, 0, +1), Cube(0, -1, +1), 
)
    assert (0 <= direction and direction < 6)
    return cube_directions[direction]

def get_neighbour(cube, direction):
    return cube + cube_direction(direction) #try mul

def get_nearest_neighbours(cube):
    neighbours = []
    for i in range(6):
        neighbours.append(get_neighbour(cube, i))
    return neighbours

def get_all_neighbours(cube, order):
    neighbours = set( (cube,) )
    for _ in range(order):
        for neighbour in neighbours.copy():
            i = set(get_nearest_neighbours(neighbour))
            neighbours.update(i)
    return neighbours.difference(set((cube,)))

def cube_lerp(a, b, t):
    return Cube(int(round(a.q * (1.0 - t) + b.q * t)),
    int(round(a.r * (1.0 - t) + b.r * t)),
    int(round(a.s * (1.0 - t) + b.s * t)))

def cube_round(h):
    qi = int(round(h.q))
    ri = int(round(h.r))
    si = int(round(h.s))
    q_diff = abs(qi - h.q)
    r_diff = abs(ri - h.r)
    s_diff = abs(si - h.s)
    if q_diff > r_diff and q_diff > s_diff:
        qi = -ri - si
    else:
        if r_diff > s_diff:
            ri = -qi - si
        else:
            si = -qi - ri
    return Cube(qi, ri, si)

ntPoint = namedtuple("Point", ["x", "y"])
Orientation = namedtuple('Orientation', 
["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])
ntLayout = namedtuple("Layout", ["orientation", "size", "origin"])

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Layout:
    orientation: Orientation
    size: Point
    origin: Point

    # def __str__(self):
    #     return f'{self.manpower}/{self.morale}'

layout_pointy = Orientation(sqrt(3.0), sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0, 
                            sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5)
layout_flat = Orientation(3.0 / 2.0, 0.0, sqrt(3.0) / 2.0, sqrt(3.0),
                          2.0 / 3.0, 0.0, -1.0 / 3.0, sqrt(3.0) / 3.0, 0.0)

def cube_to_pixel(layout, h):
    M = layout.orientation
    size = layout.size
    origin = layout.origin
    x = (M.f0 * h.q + M.f1 * h.r) * size.x
    y = (M.f2 * h.q + M.f3 * h.r) * size.y
    return Point(x + origin.x, y + origin.y)

def pixel_to_cube(layout, p):
    M = layout.orientation
    size = layout.size
    origin = layout.origin
    pt = Point((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
    q = M.b0 * pt.x + M.b1 * pt.y
    r = M.b2 * pt.x + M.b3 * pt.y
    return Cube(q, r, -q - r)

def cube_corner_offset(layout, corner):
    M = layout.orientation
    size = layout.size
    angle = 2.0 * pi * (M.start_angle - corner) / 6.0
    return Point(size.x * cos(angle), size.y * sin(angle))

def polygon_corners(layout, h):
    corners = []
    center = cube_to_pixel(layout, h)
    for i in range(0, 6):
        offset = cube_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners

# HE-specific functions

def is_blocked(game_world, cube):
    tile = game_world.get(cube)
    if not tile:
        return False
    if tile.army or tile.locality.type != None:
        return True
    else: return False

def reachable_cubes(game_world, start_cube, movement_range):
    visited = set((start_cube,)) # set of cubes
    fringes = [] # array of arrays of cubes
    fringes.append([start_cube])

    k = 1
    while k <= movement_range: #1 < k <= movement_range
        fringes.append([])
        for cube in fringes[k-1]:
            dir = 0
            while dir < 6: #0 <= dir < 6
                neighbour = get_neighbour(cube, dir)
                if neighbour not in visited:
                    # This way we also add obstacles themselves
                    visited.add(neighbour)
                    if not is_blocked(game_world, neighbour):
                        fringes[k].append(neighbour)
                dir += 1
        k += 1
    return visited

# Tests

def complain(name):
    print("FAIL {0}".format(name))

def equal_cube(name, a, b):
    if not (a.q == b.q and a.s == b.s and a.r == b.r):
        complain(name)

def test_cube_round():
    a = Cube(0.0, 0.0, 0.0)
    b = Cube(1.0, -1.0, 0.0)
    c = Cube(0.0, -1.0, 1.0)
    equal_cube("cube_round 1", Cube(5, -10, 5), cube_round(cube_lerp(Cube(0.0, 0.0, 0.0), Cube(10.0, -20.0, 10.0), 0.5)))
    equal_cube("cube_round 2", cube_round(a), cube_round(cube_lerp(a, b, 0.499)))
    equal_cube("cube_round 3", cube_round(b), cube_round(cube_lerp(a, b, 0.501)))
    equal_cube("cube_round 4", cube_round(a), cube_round(Cube(a.q * 0.4 + b.q * 0.3 + c.q * 0.3, a.r * 0.4 + b.r * 0.3 + c.r * 0.3, a.s * 0.4 + b.s * 0.3 + c.s * 0.3)))
    equal_cube("cube_round 5", cube_round(c), cube_round(Cube(a.q * 0.3 + b.q * 0.3 + c.q * 0.4, a.r * 0.3 + b.r * 0.3 + c.r * 0.4, a.s * 0.3 + b.s * 0.3 + c.s * 0.4)))

def test_layout():
    h = Cube(3, 4, -7)
    flat = Layout(layout_flat, Point(10.0, 15.0), Point(35.0, 71.0))
    equal_cube("layout", h, cube_round(pixel_to_cube(flat, cube_to_pixel(flat, h))))
    pointy = Layout(layout_pointy, Point(10.0, 15.0), Point(35.0, 71.0))
    equal_cube("layout", h, cube_round(pixel_to_cube(pointy, cube_to_pixel(pointy, h))))

def test_get_all_neighbours():
    a = Cube(0,0,0)
    b = get_all_neighbours(a, 2)
    print(b)
    print(a in b)
    print(Cube(-1,1,0) in b)

#test_cube_round()
#test_layout()
#test_get_all_neighbours()

# print(cube_round(pixel_to_cube(Layout(layout_flat, Point(20,20), Point(0,0)), Point(200, 200))))