"""
Systems
=======
Systems determine all behavior and handle the actual processing of data
contained in the components.  Systems pass data to each other through events.
Example: when a thing with Collideable overlaps something else with
         Collideable, update_physics will detect that, undo the movement that caused it,
         and fire off a Damage event
"""
import curses
import logging
from assemblage import *
from constants import *
from components import *
from events import *
from mapgen import *



def my_log(log_str):
    fire(Log(log_str))
    logging.info(log_str)


def generate_map():
    the_map = [[None for y in range(MAP_HEIGHT)]
               for x in range(MAP_WIDTH)]

    cellular_automata(the_map, wall_percentage=45,
                      smooth_iters=2, smooth_threshold=5)


def fire_player_action(ipt):
    # There should be only one thing with a player component
    player = Player.active
    player_location = Location.get_component(entity=player)
    if player_location:
        x, y = player_location.x, player_location.y
        if ipt == 'h':
            x -= 1
        if ipt == 'l':
            x += 1
        if ipt == 'j':
            y += 1
        if ipt == 'k':
            y -= 1
        if ipt == 'y':
            x -= 1
            y -= 1
        if ipt == 'u':
            x += 1
            y -= 1
        if ipt == 'b':
            x -= 1
            y += 1
        if ipt == 'n':
            x += 1
            y += 1
        if ipt == 'g':
            fire(ActorPickup(x, y, player))
        # Fire an event saying we want to move the player
        # When physics is updated the actual movement will happen
        # We could just move the player and collapse physics resolution
        # into collision resolution?
        fire(ActorMoved(x, y, player))

    if ipt == '#':
        logging.info("%s", player)
        fire(AbortTurn())
    if ipt == 'q':
        fire(Quit())


def fire_npc_actions():
    npcs = Component.entities_with(NPC, Location)
    npc_locs = Location.components(entities=npcs)

    for npc, loc in zip(npcs, npc_locs):
        x, y = loc.x, loc.y
        fire(ActorMoved(x, y, npc))


def update_camera():
    # consider doing this by making the player_input fire an actor_moved event
    # for the camera as well
    # should pick one or the other for consistency's sake
    # on the other hand, this'll never(?) collide with anything
    camera_entity = Camera.active
    camera_loc = Location.get_component(camera_entity)

    player_entity = Player.active
    player_loc = Location.get_component(entity=player_entity)

    camera_loc.x, camera_loc.y = player_loc.x, player_loc.y

    # this is where all the off-by-ones are going to be
    # I think the math is right now though
    if player_loc.x < SCREEN_WIDTH // 2:
        camera_loc.x = SCREEN_WIDTH // 2
    if player_loc.y < SCREEN_HEIGHT // 2:
        camera_loc.y = SCREEN_HEIGHT // 2
    if player_loc.x > MAP_WIDTH - 1 - SCREEN_WIDTH // 2:
        camera_loc.x = MAP_WIDTH - 1 - SCREEN_WIDTH // 2
    if player_loc.y > MAP_HEIGHT - 1 - SCREEN_HEIGHT // 2:
        camera_loc.y = MAP_HEIGHT - 1 - SCREEN_HEIGHT // 2


def update_physics():
    action = ActorMoved.pop()

    if action is None:
        return

    # Execute the move.
    # This event has execute() and undo()
    # just in case the actor bumps something
    action.execute()

    actor = action.entity
    actor_location = Location.get_component(entity=actor)

    # like here
    if Location.out_of_bounds(actor_location):
        action.undo()

    fire(Refresh(actor))
    # Get the next entity that collides with the entity that just moved;
    # We may need to undo our move
    # next(..., None) makes it return None if we hit StopIteration
    collider = next((e for e in Component.entities_with(Location, Collideable)
                     if e != actor
                     if Location.intersects(actor_location,
                                            Location.get_component(entity=e))),
                    None)

    if collider is not None:
        fire(Collision(actor, collider, action))


def resolve_action():
    pickup_event = ActorPickup.pop()

    if pickup_event is None:
        return

    actor = pickup_event.entity

    all_here = (e for e in Component.entities_with(Carriable, Location)
                if Location.get_component(e).x == pickup_event.x
                if Location.get_component(e).y == pickup_event.y)

    inv_slots = Inventory.get_component(actor).slots

    for item in all_here:
        next_slot = next(k for k, v in sorted(inv_slots.items())
                         if v is None)

        inv_slots[next_slot] = item
        Location.rm_from(item)
        logging.info("%s has %s now: %s", actor, item,
                     sorted((k, v) for k, v in inv_slots.items()))


def update_collisions():
    c = Collision.pop()

    if c is None:
        return

    if Collideable.get_component(c.receiver).blocks:
        c.action.undo()

    atk = ATK.get_component(c.initiator)
    if atk is not None:
        fire(Damage(atk, c.receiver))


def resolve_damage():
    d = Damage.pop()

    if d is None:
        return

    target_hp = HP.get_component(d.target)
    if target_hp is not None:
        target_hp.value -= d.dmg.value
        if target_hp.value <= 0:
            fire(Death(d.target))


def resolve_death():
    d = Death.pop()

    if d is None:
        return

    if d.target == Player.active:
        fire(Quit())

    # Dead things have no stats
    # Pretty much making it into a background prop
    HP.rm_from(d.target)
    ATK.rm_from(d.target)
    DEF.rm_from(d.target)

    AI.rm_group_from(d.target)
    RenderData.get_component(d.target).glyph = "%"
    RenderData.get_component(d.target).layer = MID
    Prop.add_to(d.target)
    Collideable.get_component(d.target).blocks = False
    fire(Refresh(d.target))



def initialize_render():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)

    pads = [curses.newpad(MAP_HEIGHT + 1, MAP_WIDTH + 1)
            for _ in range(NUM_RENDER_LAYERS)]

    message_log = curses.newwin(MSG_LOG_HEIGHT, MSG_LOG_WIDTH,
                                SCREEN_HEIGHT + 1, 1)
    status_log = curses.newwin(STAT_LOG_HEIGHT, STAT_LOG_WIDTH,
                               1, SCREEN_WIDTH + 1)

    message_log.idlok(True)
    message_log.scrollok(True)

    return stdscr, pads, message_log, status_log


def update_render(stdscr, pads, msg_log, stat_log):
    # render props
    props = Component.entities_with(Prop, Location, RenderData)
    for p in props:
        render = RenderData.get_component(entity=p)
        location = Location.get_component(entity=p)
        pads[render.last_layer].delch(location.y, location.x)
        pads[render.last_layer].insch(location.y, location.x, ' ')
        pads[render.layer].addch(location.y, location.x, render.glyph)

    # render anything that changed
    refreshee = Refresh.pop()

    if refreshee is None:
        return

    while refreshee is not None:

        render = RenderData.get_component(entity=refreshee.entity)
        location = Location.get_component(entity=refreshee.entity)

        pads[render.last_layer].delch(location.last_y, location.last_x)
        pads[render.last_layer].insch(location.last_y, location.last_x, ' ')
        pads[render.layer].addch(location.y, location.x,
                                 render.glyph)

        render.last_layer = render.layer
        refreshee = Refresh.pop()

    camera_entity = Camera.active
    camera_loc = Location.get_component(entity=camera_entity)

    # delete anything whose location was removed
    while Location.just_removed:
        entity, location = Location.just_removed.pop(0)
        render = RenderData.get_component(entity)
        pads[render.last_layer].delch(location.last_y, location.last_x)
        pads[render.last_layer].insch(location.last_y, location.last_x, ' ')

    # I've fixed all the off-by-ones so this should be correct
    for layer in range(NUM_RENDER_LAYERS):
        pads[layer].overlay(stdscr, camera_loc.y - SCREEN_HEIGHT // 2,
                            camera_loc.x - SCREEN_HEIGHT // 2,
                            1, 1, SCREEN_HEIGHT, SCREEN_WIDTH)

    # log player health
    # TODO: get FOV working so we can see enemies in view
    stat_log.addstr(1, 1,
                    "HP: {!s}".format(HP.get_component(Player.active).value))
    stat_log.addstr(2, 1,
                    "ATK: {!s}".format(ATK.get_component(Player.active).value))
    stat_log.addstr(3, 1,
                    "DEF: {!s}".format(DEF.get_component(Player.active).value))

    # log whatever happened this turn
    log_event = Log.pop()
    while log_event:
        msg_log.addstr("{!s}\n".format(log_event.log_str))
        log_event = Log.pop()

    stdscr.refresh()
    msg_log.refresh()
    stat_log.refresh()


def terminate_render(stdscr):
    stdscr.keypad(False)
    curses.curs_set(1)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
