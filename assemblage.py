import logging
from entity import Entity
from components import *
from events import *

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
    def Player(x, y):
        e = Entity.create()
        Player.add_to(entity=e)
        Player.active = e
        HP.add_to(entity=e, value=10)
        ATK.add_to(entity=e, value=1)
        DEF.add_to(entity=e, value=1)
        Location.add_to(entity=e, x=x, y=y)
        RenderData.add_to(entity=e, layer=FRONT, glyph="@")
        Collideable.add_to(entity=e, blocks=True)
        Inventory.add_to(entity=e, capacity=10)
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
    def Orc(x, y):
        e = Entity.create()
        NPC.add_to(entity=e)
        HP.add_to(entity=e, value=4)
        ATK.add_to(entity=e, value=1)
        Location.add_to(entity=e, x=x, y=y)
        RenderData.add_to(entity=e, layer=FRONT, glyph="o")
        Collideable.add_to(entity=e, blocks=True)
        fire(Refresh(e))
        return e

    @staticmethod
    def Floor(x, y):
        e = Entity.create()
        Location.add_to(entity=e, x=x, y=y)
        RenderData.add_to(entity=e, layer=BACK, glyph='.')
        fire(Refresh(e))
        AdjList.add_to(entity=e, neighbors=[])
        EntityList.add_to(entity=e, entities=[])
        return e

    @staticmethod
    def Wall(x, y):
        e = Entity.create()
        Location.add_to(entity=e, x=x, y=y)
        RenderData.add_to(entity=e, layer=BACK, glyph='#')
        Collideable.add_to(entity=e, blocks=True)
        AdjList.add_to(entity=e, neighbors=[])
        EntityList.add_to(entity=e, entities=[])
        fire(Refresh(e))
        return e

    @staticmethod
    def Sword(x, y):
        e = Entity.create()
        Prop.add_to(entity=e)
        Location.add_to(entity=e, x=x, y=y)
        RenderData.add_to(entity=e, layer=MID, glyph=")")
        Carriable.add_to(entity=e)
        return e
