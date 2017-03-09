# THIS MUST ALWAYS BE ODD
SCREEN_WIDTH = 25
SCREEN_HEIGHT = 25

MAP_WIDTH = 25
MAP_HEIGHT = 25

DUNGEON_DEPTH = 9
DUNGEON_TOP = 0

STAT_LOG_HEIGHT = SCREEN_HEIGHT
STAT_LOG_WIDTH = 11

MSG_LOG_WIDTH = SCREEN_WIDTH + STAT_LOG_WIDTH
MSG_LOG_HEIGHT = 8

INV_MAX = 4

NUM_RENDER_LAYERS = 5
FRONT = 4
MID_FRONT = 3
MID = 2
MID_BACK = 1
BACK = 0
RENDER_LAYERS = [BACK, MID_BACK, MID, MID_FRONT, FRONT]

FOV_RADIUS = 7

HELP_STRING = """hjklyubn: movement
z: ranged attack
x: circular attack



"""


def in_bounds(x, y):
    return 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT


def get_all_children(cls):
    subclasses = []
    if len(cls.__subclasses__()) > 0:
        for subclass in cls.__subclasses__():
            subclasses.append(subclass)
            subclasses += get_all_children(subclass)
    return subclasses
