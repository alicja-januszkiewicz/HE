import cubic

layout = cubic.Layout(cubic.layout_pointy, cubic.Point(40,40), cubic.Point(800,550))

def pan(direction):
    x = direction.x
    y = direction.y
    x *= layout.size.x
    y *= layout.size.y
    layout.origin.x += x
    layout.origin.y += y

def zoom(sign):
    layout.size.x += sign
    layout.size.y += sign

def get_layout():
    return layout