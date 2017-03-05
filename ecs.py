import curses
import logging

from constants import *
from components import *
from events import *
from assemblage import Assemblage
from systems import *

from random import randint

################################################################
#                                                              #
#                            ENGINE                            #
#                                                              #
################################################################


class Engine(object):
    component_classes = [Location, RenderData, AI, Player, NPC, Camera,
                         HP, ATK, DEF, Collideable, Carriable, Inventory,
                         Prop, AdjList, EntityList]
    event_classes = [ActorMoved, ActorPickup, Collision, Damage, Death,
                     Refresh, AbortTurn, Log, Quit]
    stdscr = None
    pads = None

    @staticmethod
    def initialize():
        for cc in Engine.component_classes:
            cc.initialize()

        for ec in Engine.event_classes:
            ec.initialize()

        Engine.render_data = initialize_render()

    @staticmethod
    def main():
        turn_count = 0
        while not Quit.peek():
            logging.info("===TURN %s===", turn_count)
            while ActorMoved.queue or ActorPickup.queue:
                update_physics()
                update_collisions()
                resolve_damage()
                resolve_death()
                resolve_action()  # not sure what order these all happen in 
            update_camera()
            update_render(*Engine.render_data)
            fire_player_action(Engine.render_data[0].getkey())
            while AbortTurn.pop():
                fire_player_action(Engine.stdscr.getkey())
            fire_npc_actions()
            turn_count += 1

    @staticmethod
    def terminate():
        terminate_render(Engine.render_data[0])


if __name__ == "__main__":
    logging.basicConfig(filename="./log", filemode="w", level=logging.INFO)
    Engine.initialize()
    Assemblage.Player(x=10, y=10)
    Assemblage.Camera()
    Assemblage.Orc(x=5, y=2)
    Assemblage.Sword(x=1, y=1)

    generate_map()
    Engine.main()
    Engine.terminate()
