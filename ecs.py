import curses
import logging

from constants import *
from components import *
from events import *
from assemblage import Assemblage
from systems import *

################################################################
#                                                              #
#                            ENGINE                            #
#                                                              #
################################################################


class Engine(object):
    component_classes = get_all_children(Component)
    event_classes = get_all_children(Event)
    stdscr = None
    pads = None

    @staticmethod
    def initialize():
        for cc in Engine.component_classes:
            cc.initialize()

        for ec in Engine.event_classes:
            ec.initialize()

        Engine.render_data = initialize_render()

        Assemblage.Camera()

        dungeon = [generate_map(l) for l in range(10)]

        for i in range(10):
            actualize_map(dungeon[i], depth=i)

        link_stairs()

        populate_dungeon(dungeon, DUNGEON_DEPTH)

    @staticmethod
    def main():
        turn_count = 0
        while not (Quit.peek() or Win.peek()):
            logging.info("===TURN %s===", turn_count)
            update_timers()
            while (ActorMoved.queue or ActorPickup.queue or
                   Descent.queue or Ascent.queue):
                update_depth()
                update_physics()
                update_collisions()
                resolve_level_change()
                resolve_special()
                resolve_action()  # not sure what order these all happen in
            resolve_heals()
            resolve_damage()
            resolve_time_siphon()
            update_TIME()
            resolve_death()
            update_camera()
            update_render(*Engine.render_data)
            fire_player_action(Engine.render_data[0].getkey())
            while AbortTurn.pop():
                fire_player_action(Engine.stdscr.getkey())
            fire_npc_actions()
            cleanup_removed_components()
            turn_count += 1

    @staticmethod
    def terminate():
        terminate_render(Engine.render_data[0])
        if Win.pop() is not None:
            print("Yon win!")
        else:
            print("You lose!")

if __name__ == "__main__":
    logging.basicConfig(filename="./log", filemode="w", level=logging.INFO)
    Engine.initialize()
    Engine.main()
    Engine.terminate()


# TODO
# Get basic enemy ai working
# Get deeper-level enemies to suck your time away
# Experience levels?
# THink of more skills!
