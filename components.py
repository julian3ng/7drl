"""
Components
==========
Components contain pretty much all the game data.
Behavior of a game object is determined by what components it has.
Example: something with a Player component will be affected by the
         player_input system, something with a Collideable component
         is able to collide with other things with Collideable components,
         and something with HP is able to die / be destroyed.
Empty components are used to add behavior without any particular data
attached to it beyond that an entity has that component.
"""
from constants import *
from entity import Entity


class Component(object):
    """
    Component classes are the component managers
    Each holds a dict of entities of their type
    Has functionality to add, remove, get all entities with,
    and get all components of this type
    """
    @classmethod
    def initialize(cls):
        cls.table = {}
        cls.just_removed = []

    @classmethod
    def add_to(cls, entity, *args, **kwargs):
        """
        Add a new instance of the component class with the arguments passed
        through
        """
        cls.table[entity] = cls(*args, **kwargs)

    @classmethod
    def rm_from(cls, entity):
        """
        Remove this component from the given entity
        """
        component_removed = cls.table.pop(entity, None)
        if component_removed is not None:
            cls.just_removed.append((entity, component_removed))

    @classmethod
    def rm_group_from(cls, entity):
        """
        Remove this group of components recursively from the given entity
        """
        if len(cls.__subclasses__()) > 0:
            for subclass in cls.__subclasses__():
                subclass.rm_group_from(entity)
        else:
            cls.rm_from(entity)

    @classmethod
    def get_component(cls, entity):
        """
        Get the component of this class from one entity
        """
        return cls.table.get(entity, None)

    @classmethod
    def has_component(cls, entity):
        """
        See if the entity has this component
        """
        return entity in cls.table

    @classmethod
    def entities(cls):
        """
        Get all entities with this component
        """
        return list(cls.table.keys())

    @classmethod
    def components(cls, entities=None):
        """
        If entities=None: Get all components of this type
        Else: Get components for each entity passed in
        """
        from collections import Iterable
        if entities is None:
            return list(cls.table.values())
        elif isinstance(entities, Iterable):
            return [cls.table.get(e, None) for e in entities]

    @staticmethod
    def entities_with(*component_classes):
        """
        Get all entities with all components given
        """
        valid = set(range(Entity.num_entities))
        for c in component_classes:
            valid = valid.intersection(set(c.table))

        return list(v for v in valid)

    def __str__(self):
        return "{:<20}:".format(self.__class__.__name__) + \
            " ".join("{!s}: {!r} ".format(k, v)
                     for k, v in sorted(vars(self).items()))

    @classmethod
    def table_str(cls):
        return "\n".join("{!s}: {!s}".format(k, v)
                         for k, v in cls.table.items())

    @classmethod
    def cleanup(cls):
        cls.just_removed = []
        if len(cls.__subclasses__()) > 0:
            for subclass in cls.__subclasses__():
                subclass.cleanup()


class Location(Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_x = self.x  # used for undoing movements
        self.last_y = self.y  # used for undoing movements

    @staticmethod
    def intersects(l1, l2):
        """ Return whether or not two Locations intersect """
        return l1.x == l2.x and l1.y == l2.y

    @staticmethod
    def out_of_bounds(l):
        """ Return whether or not a location is out of bounds """
        return not in_bounds(l.x, l.y)

    @staticmethod
    def distance2(l1, l2):
        """ Return the square distance between these two locations """
        return (l1.x - l2.x)**2 + (l1.y - l2.y)**2

    @staticmethod
    def direction(l1, l2):
        """ Return a vector from l1 to l2 """
        from numpy import sign
        return tuple(sign([l2.x - l1.x, l2.y - l1.y]))


class Depth(Component):
    def __init__(self, z):
        self.z = z
        self.last_z = z

    @staticmethod
    def same_level(d1, d2):
        return d1.z == d2.z


class RenderData(Component):
    """
    Layer: there are five layers (defined in constants.py)
    Glyph: what this entity displays as on screen
    """
    def __init__(self, layer, glyph):
        self.layer = layer
        self.last_layer = layer
        self.glyph = glyph


class AI(Component):
    pass


class Player(AI):
    # the player gets to be a little special in this mostly-pure ECS
    active = None


class NPC(AI):
    pass


class Prop(AI):
    pass


class Camera(AI):
    # the camera gets to be a little special too
    active = None


class Collideable(Component):
    """
    Collideables that run into each other will shoot out collision events
    If non-blocking then the owner doesn't force the collider out of its space
    """
    def __init__(self, blocks):
        self.blocks = blocks


class Stat(Component):
    """
    Anything with one value is a stat...?
    """
    def __init__(self, value):
        self.value = value


class Timer(Component):
    def __init__(self, max_time):
        self.time = 0
        self.max_time = max_time


class HP(Stat):
    pass


class ATK(Stat):
    pass


class DEF(Stat):
    pass


class TIME(Stat):
    def __init__(self, value, decay_rate):
        self.value = value
        self.decay_rate = decay_rate


class Faction(Stat):
    pass


class Carriable(Component):
    """
    Things with this component can be picked up
    """
    pass


class Inventory(Component):
    """
    Has slots to hold things with Carriable
    """
    def __init__(self, capacity):
        self.capacity = min(capacity, INV_MAX)
        self.slots = {chr(x): None
                      for x in range(ord('a'), ord('a') + 4)}


class Yendor(Component):
    pass


class OnDeath(Component):
    """
    Define what happens when this thing's HP drops to 0
    """
    def __init__(self, death_function):
        self.death_function = death_function


# Tile components below?
class AdjList(Component):
    """
    Contain adjacency data for a tile
    """
    def __init__(self, neighbors):
        self.neighbors = neighbors


class EntityList(Component):
    """
    Contain whatever entity lives here
    """
    def __init__(self, entities=[]):
        self.entities = entities


class Descender(Component):
    """
    Stairs that go down
    """
    def __init__(self, down):
        self.down = down


class Ascender(Component):
    """
    Stairs that go up
    """
    def __init__(self, up):
        self.up = up
