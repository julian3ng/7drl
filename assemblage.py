import logging
from entity import Entity
from components import *
from events import *
from death_triggers import *

################################################################
#                                                              #
#                          ASSEMBLAGE                          #
#                                                              #
################################################################


class Assemblage(object):
    """
    Define 'classes' of objects
    It would be nice to define these in a json file or something somewhere
    else so it's easier to add objects but this is ok for now
    """
    @staticmethod
    def Player(x, y, z):
        e = Entity.create()
        Player.add_to(entity=e)
        Player.active = e
        HP.add_to(entity=e, value=10)
        ATK.add_to(entity=e, value=2)
        DEF.add_to(entity=e, value=1)
        TIME.add_to(entity=e, value=1000, decay_rate=1)
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=FRONT, glyph="@")
        Collideable.add_to(entity=e, blocks=True)
        Inventory.add_to(entity=e, capacity=10)
        Faction.add_to(entity=e, value=0)
        OnDeath.add_to(entity=e, death_function=player_death)
        fire(Refresh(e))
        return e

    @staticmethod
    def Camera():
        e = Entity.create()
        Camera.add_to(entity=e)
        Camera.active = e
        Location.add_to(entity=e, x=4, y=4)
#        RenderData.add_to(entity=e, layer=MID_FRONT, glyph="*")

        return e

    @staticmethod
    def Zombie(x, y, z):
        e = Entity.create()
        NPC.add_to(entity=e)
        HP.add_to(entity=e, value=4)
        ATK.add_to(entity=e, value=1)
        TIME.add_to(entity=e, value=50, decay_rate=1)
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=FRONT, glyph="z")
        Collideable.add_to(entity=e, blocks=True)
        OnDeath.add_to(entity=e, death_function=npc_death)
        Faction.add_to(entity=e, value=1)
        fire(Refresh(e))
        return e

    @staticmethod
    def Wight(x, y, z):
        e = Entity.create()
        NPC.add_to(entity=e)
        HP.add_to(entity=e, value=10)
        ATK.add_to(entity=e, value=2)
        TIME.add_to(entity=e, value=1, decay_rate=0)
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=FRONT, glyph='w')
        OnDeath.add_to(entity=e, death_function=npc_death)
        Faction.add_to(entity=e, value=2)
        fire(Refresh(e))
        return e

    @staticmethod
    def Floor(x, y, z):
        e = Entity.create()
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=BACK, glyph='.')
        fire(Refresh(e))
        AdjList.add_to(entity=e, neighbors=[])
        EntityList.add_to(entity=e, entities=[])
        return e

    @staticmethod
    def Wall(x, y, z):
        e = Entity.create()
        HP.add_to(entity=e, value=1)
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=BACK, glyph='#')
        Collideable.add_to(entity=e, blocks=True)
        AdjList.add_to(entity=e, neighbors=[])
        EntityList.add_to(entity=e, entities=[])
        OnDeath.add_to(entity=e, death_function=wall_death)
        fire(Refresh(e))
        return e

    @staticmethod
    def DownStair(x, y, z):
        e = Entity.create()
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=BACK, glyph='>')
        AdjList.add_to(entity=e, neighbors=[])
        EntityList.add_to(entity=e, entities=[])
        Descender.add_to(entity=e, down=None)
        fire(Refresh(e))
        return e

    @staticmethod
    def UpStair(x, y, z):
        e = Entity.create()
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=BACK, glyph='<')
        AdjList.add_to(entity=e, neighbors=[])
        EntityList.add_to(entity=e, entities=[])
        Ascender.add_to(entity=e, up=None)
        fire(Refresh(e))
        return e

    @staticmethod
    def Objective(x, y, z):
        e = Entity.create()
        Prop.add_to(entity=e)
        Location.add_to(entity=e, x=x, y=y)
        Depth.add_to(entity=e, z=z)
        RenderData.add_to(entity=e, layer=MID, glyph="*")
        Carriable.add_to(entity=e)
        Yendor.add_to(entity=e)
        return e
