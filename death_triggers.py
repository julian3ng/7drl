from components import *
from events import *


def player_death(entity):
    RenderData.get_component(entity).glyph = "%"
    RenderData.get_component(entity).layer = MID
    Prop.add_to(entity)
    fire(Quit())


def npc_death(entity):
    HP.rm_from(entity)
    ATK.rm_from(entity)
    DEF.rm_from(entity)
    TIME.rm_from(entity)
    AI.rm_group_from(entity)
    RenderData.get_component(entity).glyph = "%"
    RenderData.get_component(entity).layer = MID
    Prop.add_to(entity)
    if Collideable.get_component(entity) is not None:
        Collideable.get_component(entity).blocks = False
    fire(Refresh(entity))


def wall_death(entity):
    HP.rm_from(entity)
    TIME.rm_from(entity)
    RenderData.get_component(entity).glyph = ","
    Collideable.rm_from(entity)
    fire(Refresh(entity))
