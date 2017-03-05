from constants import *
from components import *
################################################################
#                                                              #
#                             EVENTS                           #
#                                                              #
################################################################


class Event(object):
    """
    Events are used to pass messages between systems
    """
    @classmethod
    def initialize(cls):
        # deque is optimized!
        from collections import deque
        cls.queue = deque([])

    @classmethod
    def add(cls, event):
        cls.queue.append(event)

    @classmethod
    def pop(cls):
        # when we want to be done with the event
        return cls.queue.popleft() if cls.queue else None

    @classmethod
    def peek(cls):
        # Sometimes we might want to modify the event
        return cls.queue[0] if cls.queue else None


class ActorMoved(Event):
    def __init__(self, x, y, entity):
        self.x = x
        self.y = y
        self.entity = entity

    def execute(self):
        entity_location = Location.get_component(entity=self.entity)
        entity_location.last_x = entity_location.x
        entity_location.last_y = entity_location.y
        entity_location.x = self.x
        entity_location.y = self.y

    def undo(self):
        entity_location = Location.get_component(entity=self.entity)
        entity_location.x = entity_location.last_x
        entity_location.y = entity_location.last_y


class ActorPickup(Event):
    def __init__(self, x, y, entity):
        self.x = x
        self.y = y
        self.entity = entity


class Collision(Event):
    def __init__(self, initiator, receiver, action):
        self.initiator = initiator
        self.receiver = receiver
        self.action = action


class Damage(Event):
    def __init__(self, dmg, target):
        self.dmg = dmg
        self.target = target


class Death(Event):
    def __init__(self, target):
        self.target = target


class Refresh(Event):
    def __init__(self, entity, erase=False):
        self.entity = entity
        self.erase = False


class Log(Event):
    def __init__(self, log_str):
        self.log_str = log_str


class AbortTurn(Event):
    pass


class Quit(Event):
    pass


def fire(event):
    """
    Add an event to its class's queue for later processing
    """
    event.__class__.add(event)
