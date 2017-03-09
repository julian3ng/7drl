from components import *
from constants import *
from assemblage import *
from random import randint, choice


def seed(the_map, wall_percentage):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if randint(0, 99) < wall_percentage:
                the_map[x][y] = "#"
            else:
                the_map[x][y] = "."


def smooth(the_map, iters, threshold):
    """
    Make <iters> passes over the map
    For each tile, check how many adjacent (including itself) tiles are walls
    If > 5, make it a wall too
    Else make it a floor
    This creates nice smooth caves.
    """
    for i in range(iters):
        transforms = [[None for y in range(MAP_HEIGHT)]
                      for x in range(MAP_WIDTH)]
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                adj_list = [the_map[i][j] for i in range(x - 1, x + 2)
                            for j in range(y - 1, y + 2)
                            if in_bounds(i, j)
                            if not (i == 0 and j == 0)]
                wall_count = 1 if the_map[x][y] == "#" else 0
                for neighbor in adj_list:
                    if neighbor == "#":
                        wall_count += 1
                        if wall_count >= threshold:
                            transforms[x][y] = "#"
                        else:
                            transforms[x][y] = "."

        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if transforms[x][y] == "#":
                    the_map[x][y] = "#"
                else:
                    the_map[x][y] = "."


def add_stairs(the_map, depth):
    num_downs = 1
    num_ups = 1
    while num_downs + num_ups > 0:
        if depth == DUNGEON_DEPTH:
            num_downs = 0
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if the_map[x][y] == ".":
                    if randint(0, 99) < 1 and num_downs > 0:
                        the_map[x][y] = ">"
                        num_downs -= 1
                    elif randint(0, 99) < 1 and num_ups > 0:
                        the_map[x][y] = "<"
                        num_ups -= 1


def border(the_map):
    for i in range(0, MAP_WIDTH - 1):
        the_map[i][0] = "#"
        the_map[i][MAP_HEIGHT - 1] = "#"

    for j in range(0, MAP_HEIGHT - 1):
        the_map[0][j] = "#"
        the_map[MAP_WIDTH - 1][j] = "#"


def create_adjacencies(the_map):
    """
    Requires that the map be composed of entities that are in the AdjList table
    """
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            adj_list = AdjList.get_component(the_map[x][y])
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if not (i == x and j == y):
                        if in_bounds(i, j):
                            adj_list.neighbors.append(the_map[i][j])


def create_real_tiles(the_map, depth):
    """
    Convert a map of # and . into Walls and Floors
    """
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if the_map[x][y] == "#":
                the_map[x][y] = Assemblage.Wall(x, y, depth)
            elif the_map[x][y] == ".":
                the_map[x][y] = Assemblage.Floor(x, y, depth)
            elif the_map[x][y] == ">":
                the_map[x][y] = Assemblage.DownStair(x, y, depth)
            elif the_map[x][y] == "<":
                the_map[x][y] = Assemblage.UpStair(x, y, depth)


def cellular_automata(wall_percentage, smooth_iters, smooth_threshold):
    the_map = [[None for y in range(MAP_HEIGHT)]
               for x in range(MAP_WIDTH)]
    seed(the_map, wall_percentage)
    smooth(the_map, smooth_iters, smooth_threshold)

    return the_map


def walk_around(the_map, max_floor):
    x, y = randint(0, MAP_WIDTH - 1), randint(0, MAP_HEIGHT - 1)
    cur_floor = 0
    coordinates = (x, y)
    the_map[coordinates[0]][coordinates[1]] = "."
    cur_floor += 1

    while cur_floor < max_floor:
        neighbors = [(i, j) for i in range(coordinates[0] - 1, coordinates[0] + 2)
                     for j in range(coordinates[1] - 1, coordinates[1] + 2)
                     if in_bounds(i, j)
                     if not (i == coordinates[0] and j == coordinates[1])]
        coordinates = choice(neighbors)
        if the_map[coordinates[0]][coordinates[1]]:
            the_map[coordinates[0]][coordinates[1]] = "."
            cur_floor += 1


def random_walk(max_floor):
    the_map = [[None for y in range(MAP_HEIGHT)]
               for x in range(MAP_WIDTH)]
    seed(the_map, 100)
    walk_around(the_map, max_floor)
    smooth(the_map, 2, 5)
    return the_map


def xor(map1, map2):
    outmap = [[None for y in range(MAP_HEIGHT)]
              for x in range(MAP_WIDTH)]

    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tile1 = map1[x][y]
            tile2 = map2[x][y]
            if (tile1 == "#" and tile2 == "#"):
                outmap[x][y] = "."
            elif (tile1 == "#" and tile2 == "."):
                outmap[x][y] = "#"
            elif (tile1 == "." and tile2 == "#"):
                outmap[x][y] = "."
            elif (tile1 == "." and tile2 == "."):
                outmap[x][y] = "#"

    return outmap


def double_cellular_automata(wall_percentage, smooth_iters, smooth_threshold):
    map1 = cellular_automata(wall_percentage, smooth_iters,
                             smooth_threshold)

    map2 = cellular_automata(wall_percentage, smooth_iters,
                             smooth_threshold)
    return xor(map1, map2)
