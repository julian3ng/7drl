from components import *
from constants import *
from assemblage import *
from random import randint


def seed(the_map, wall_percentage):
    # First pass: put walls and floors in randomly
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if randint(0, 99) < wall_percentage:
                the_map[x][y] = Assemblage.Wall(x, y)
            else:
                the_map[x][y] = Assemblage.Floor(x, y)


def link(the_map):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            adj_list = AdjList.get_component(the_map[x][y])
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if not (i == x and j == y):
                        if in_bounds(i, j):
                            adj_list.neighbors.append(the_map[i][j])


def smooth(the_map, iters, threshold):
    for i in range(iters):
        transforms = [[None for y in range(MAP_HEIGHT)]
                      for x in range(MAP_WIDTH)]
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                adj_list = AdjList.get_component(the_map[x][y]).neighbors
                wall_count = 1 if Collideable.has_component(the_map[x][y]) else 0
                for neighbor in adj_list:
                    if Collideable.has_component(neighbor):
                        wall_count += 1
                        if wall_count >= threshold:
                            transforms[x][y] = "#"
                        else:
                            transforms[x][y] = "."

        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if transforms[x][y] == "#":
                    Collideable.add_to(the_map[x][y], blocks=True)
                    RenderData.get_component(the_map[x][y]).glyph = "#"
                else:
                    Collideable.rm_from(the_map[x][y])
                    RenderData.get_component(the_map[x][y]).glyph = "."


def cellular_automata(the_map, wall_percentage, smooth_iters, smooth_threshold):

    seed(the_map, wall_percentage)
    link(the_map)
    smooth(the_map, smooth_iters, smooth_threshold)


def random_walk(the_map):
    seed(the_map, 100)
    
