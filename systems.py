"""
Systems
=======
Systems determine all behavior and handle the actual processing of data
contained in the components.  Systems pass data to each other through events.
Example: when a thing with Collideable overlaps something else with
         Collideable, update_physics will detect that, undo the movement that
         caused it,
         and fire off a Damage event
"""
import curses
import logging
from assemblage import *
from constants import *
from components import *
from events import *
from mapgen import *
from random import randint


def my_log(log_str):
    fire(Log(log_str))
    logging.info(log_str)


def generate_map(depth):
    the_map = double_cellular_automata(wall_percentage=45,
                                       smooth_iters=2, smooth_threshold=5)
    add_stairs(the_map, depth)
    return the_map


def actualize_map(the_map, depth):
    create_real_tiles(the_map, depth)
    create_adjacencies(the_map)
    return the_map


def spawn(dungeon, depth, assemblage_with_location):
    initial_x = randint(0, MAP_WIDTH - 1)
    initial_y = randint(0, MAP_HEIGHT - 1)
    while Collideable.has_component(dungeon[depth][initial_x][initial_y]):
        initial_x = randint(0, MAP_WIDTH - 1)
        initial_y = randint(0, MAP_HEIGHT - 1)

    assemblage_with_location(x=initial_x, y=initial_y, z=depth)


def all_in_radius(entity, radius):
    entity_location = Location.get_component(entity)
    entity_depth = Depth.get_component(entity)

    if entity_location is None or entity_depth is None:
        return

    in_radius = []
    for maybe_entity in Component.entities_with(Location, Depth):
        if entity == maybe_entity:
            continue
        if Depth.same_level(Depth.get_component(maybe_entity), entity_depth):
            if Location.distance2(Location.get_component(maybe_entity), entity_location) < radius **2:
                in_radius.append(maybe_entity)
    return in_radius


def get_nearest_entity(entity):
    from math import inf
    entity_location = Location.get_component(entity)
    entity_depth = Depth.get_component(entity)
    if entity_location is None or entity_depth is None:
        return None

    entities = Component.entities_with(Location, NPC) + Component.entities_with(Location, Player)
    locations = Location.components(entities)
    depths = Depth.components(entities)
    min_ent = None
    min_dist = inf
    for cur_entity, location, depth in zip(entities, locations, depths):
        if cur_entity == entity:
            continue
        if not Depth.same_level(entity_depth, depth):
            continue
        dist2 = Location.distance2(entity_location, location)
        if dist2 < min_dist:
            min_dist = dist2
            min_ent = cur_entity

    return min_ent, min_dist


def get_nearest_enemy(entity):
    from math import inf
    entity_location = Location.get_component(entity)
    entity_depth = Depth.get_component(entity)
    entity_faction = Faction.get_component(entity)
    if entity_location is None or entity_depth is None:

        return None

    entities = Component.entities_with(Location, NPC) + Component.entities_with(Location, Player)
    min_ent = None
    min_dist = inf
    for cur_entity in entities:
        location = Location.get_component(cur_entity)
        depth = Depth.get_component(cur_entity)
        faction = Faction.get_component(cur_entity)

        if faction.value == entity_faction.value:
            continue
        if cur_entity == entity:
            continue
        if not Depth.same_level(entity_depth, depth):
            continue

        dist2 = Location.distance2(entity_location, location)
        if dist2 < min_dist:
            min_dist = dist2
            min_ent = cur_entity

    return min_ent, min_dist


def populate_dungeon(dungeon, depth):
    for floor in range(depth + 1):
        if floor == DUNGEON_TOP:
            spawn(dungeon, floor, Assemblage.Player)
        for _ in range(5):
            spawn(dungeon, floor, Assemblage.Zombie)
        if randint(0, 99) < 10:
            spawn(dungeon, floor, Assemblage.Wight)

        if floor == DUNGEON_DEPTH:
            spawn(dungeon, floor, Assemblage.Objective)


def link_stairs():
    up_stairs = Component.entities_with(Ascender, Location, Depth)
    down_stairs = Component.entities_with(Descender, Location, Depth)

    all_pairs = [(up, down) for up in up_stairs for down in down_stairs]

    for stair_pair in all_pairs:
        up_depth = Depth.get_component(stair_pair[0])
        down_depth = Depth.get_component(stair_pair[1])

        if down_depth.z > up_depth.z:
            continue
        if up_depth.z - down_depth.z != 1:
            continue
        up_ascender = Ascender.get_component(stair_pair[0])
        down_descender = Descender.get_component(stair_pair[1])

        if (up_ascender.up is not None or
                down_descender.down is not None):
            continue
        up_ascender.up = stair_pair[1]
        down_descender.down = stair_pair[0]


def fire_player_action(ipt):
    # There should be only one thing with a player component
    player = Player.active
    player_location = Location.get_component(entity=player)
    player_depth = Depth.get_component(entity=player)
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
        if ipt == '>':
            logging.info("COMMAND: >")
            fire(ActorChangeLevel(player_depth.z + 1, player))

        if ipt == '<':
            logging.info("COMMAND: <")
            fire(ActorChangeLevel(player_depth.z - 1, player))

        if ipt == 'x':
            for entity in all_in_radius(player, FOV_RADIUS):
                fire(TIMEPulse(player, entity))

        if ipt == 'z':
            fire(TIMESiphon(player, get_nearest_enemy(player)[0]))

        if ipt == 'g':
            fire(ActorPickup(x, y, player))

        if ipt == '?':
            fire(Log(HELP_STRING))

        # Fire an event saying we want to move the player
        # When physics is updated the actual movement will happen
        # We could just move the player and collapse physics resolution
        # into collision resolution?
        fire(ActorMoved(x, y, player))

    if ipt == '#':
        my_log("{!s}".format(player_location.x))

    if ipt == 'q':
        fire(Quit())


def fire_npc_actions():
    npcs = Component.entities_with(NPC, Location)

    for npc in npcs:
        loc = Location.get_component(npc)
        depth = Depth.get_component(npc)
        if abs(depth.z - Depth.get_component(Player.active).z) == 0:
            near = all_in_radius(npc, FOV_RADIUS)
            nearest = get_nearest_enemy(npc)
            nloc = Location.get_component(nearest[0])
            if (nearest[0] in near and
                nearest != npc and
                    nloc is not None):
                dir = Location.direction(loc, nloc)
                x, y = loc.x + dir[0], loc.y + dir[1]
                fire(ActorMoved(x, y, npc))
            else:
                x, y = loc.x + randint(-1, 1), loc.y + randint(-1, 1)
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

    actor_depth = Depth.get_component(entity=actor)

    fire(Refresh(actor))
    # Get the next entity that collides with the entity that just moved;
    # We may need to undo our move
    # next(..., None) makes it return None if we hit StopIteration
    collider = next((e for e in Component.entities_with(Location, Collideable)
                     if e != actor
                     if Location.intersects(actor_location,
                                            Location.get_component(entity=e))
                    if Depth.same_level(actor_depth,
                                        Depth.get_component(entity=e))),
                    None)

    if collider is not None:
        fire(Collision(actor, collider, action))


def update_depth():
    depth_change = ActorChangeLevel.pop()

    if depth_change is None:
        return
    
    actor = depth_change.entity
    actor_depth = Depth.get_component(entity=actor)

    direction = depth_change.z - actor_depth.z
    up_stairs = Component.entities_with(Ascender, Location)
    down_stairs = Component.entities_with(Descender, Location)

    if direction < 0:
        for up_stair in up_stairs:
            if (Location.intersects(Location.get_component(up_stair),
                                    Location.get_component(actor)) and
                    (Depth.same_level(actor_depth, Depth.get_component(up_stair)))):
                # We're on the top floor?
                if actor == Player.active and actor_depth.z == DUNGEON_TOP:
                    for entity in Inventory.get_component(actor).slots.values():
                        if Yendor.get_component(entity) is not None:
                            fire(Win())
                    fire(Log("Press any key to continue..."))
                    fire(Quit())
                    break

                up_stair_connector = Ascender.get_component(up_stair).up
                up_stair_connector_loc = Location.get_component(up_stair_connector)
                depth_change.execute()
                fire(Ascent())
                fire(ActorMoved(up_stair_connector_loc.x,
                                up_stair_connector_loc.y,
                                actor))

    if direction > 0:
        for down_stair in down_stairs:
            if (Location.intersects(Location.get_component(down_stair),
                                    Location.get_component(actor)) and
                    (Depth.same_level(actor_depth, Depth.get_component(down_stair)))) :
                down_stair_connector = Descender.get_component(down_stair).down
                down_stair_connector_loc = Location.get_component(down_stair_connector)
                depth_change.execute()
                fire(Descent())
                fire(ActorMoved(down_stair_connector_loc.x,
                                down_stair_connector_loc.y,
                                actor))


def update_TIME():
    timed = Component.entities_with(TIME)
    for entity in timed:
        time = TIME.get_component(entity)
        depth = Depth.get_component(entity)
        if abs(depth.z - Depth.get_component(Player.active).z) <= 1:
            time.value -= time.decay_rate
            if time.value <= 0:
                fire(Death(entity))


def update_timers():
    timed = Component.entities_with(Timer)

    for timed_one in timed:
        timer = Timer.get_component(timed_one)
        timer.time += 1
        if timer.time == timer.max_time:
            timer.time = 0
            fire(Heal(timed_one))

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


def resolve_special():
    time_pulse_event = TIMEPulse.pop()

    while time_pulse_event is not None:
        actor_time = TIME.get_component(time_pulse_event.actor)
        actor_atk = ATK.get_component(time_pulse_event.actor)
        target_health = HP.get_component(time_pulse_event.target)

        if target_health is None:
            time_pulse_event = TIMEPulse.pop()
            continue

        fire(TimeDamage(actor_atk.value, time_pulse_event.actor))
        fire(Damage(actor_atk.value, time_pulse_event.target))
        time_pulse_event = TIMEPulse.pop()


def update_collisions():
    c = Collision.pop()

    if c is None:
        return

    if Collideable.get_component(c.receiver).blocks:
        c.action.undo()

    atk = ATK.get_component(c.initiator)
    if atk is not None:
        fire(Damage(atk.value, c.receiver))
        fire(TIMESiphon(c.initiator, c.receiver))


def resolve_heals():
    h = Heal.pop()

    while h is not None:
        target_hp = HP.get_component(h.actor)
        if target_hp is not None and target_hp.value < 10:
            target_hp.value += 1
        h = Heal.pop()


def resolve_damage():
    d = Damage.pop()

    while d is not None:
        target_hp = HP.get_component(d.target)
        if target_hp is not None:
            target_hp.value -= d.dmg
            if target_hp.value <= 0:
                fire(Death(d.target))
        d = Damage.pop()

    t = TimeDamage.pop()
    while t is not None:
        target_time = TIME.get_component(t.target)
        if target_time is not None:
            target_time.value -= t.dmg
            if target_time.value <= 0:
                fire(Death(t.target))
        t = TimeDamage.pop()


def resolve_time_siphon():
    siphon_event = TIMESiphon.pop()

    while siphon_event is not None:
        actor_atk = ATK.get_component(siphon_event.actor)
        actor_time = TIME.get_component(siphon_event.actor)
        target_time = TIME.get_component(siphon_event.target)
        if target_time is not None and actor_atk is not None:
            fire(TimeDamage(actor_atk.value, siphon_event.target))
            fire(Damage(actor_atk.value - 1, siphon_event.actor))

            actor_time.value += actor_atk.value
        siphon_event = TIMESiphon.pop()


def resolve_death():
    d = Death.pop()

    while d is not None:
        death_trigger = OnDeath.get_component(d.target)
        if death_trigger is not None:
            death_trigger.death_function(d.target)
        d = Death.pop()


def resolve_level_change():
    ascent_event = Ascent.pop()
    descent_event = Descent.pop()

    if not any([ascent_event, descent_event]):
        return

    player_depth = Depth.get_component(Player.active)
    depth_entities = Component.entities_with(Depth, RenderData, Location)
    depth_components = Depth.components(depth_entities)

    for e, c in zip(depth_entities, depth_components):
        if c.z == player_depth:
            fire(Refresh(e))
        else:
            fire(Refresh(e, erase=True))

    fire(ClearScreen())


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
    clear_event = ClearScreen.pop()

    if clear_event is not None:
        for pad in pads:
            pad.clear()


    # render props
    player_depth = Depth.get_component(entity=Player.active)
    props = Component.entities_with(Prop, Location, RenderData)
    for p in props:
        render = RenderData.get_component(entity=p)
        location = Location.get_component(entity=p)
        depth = Depth.get_component(entity=p)
        if Depth.same_level(player_depth, depth):
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
        depth = Depth.get_component(entity=refreshee.entity)
        if Depth.same_level(player_depth, depth):
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

    # hook up stats to stat bar 
    stat_log.addstr(1, 1,
                    "HP: {!s}".format(HP.get_component(Player.active).value))
    stat_log.addstr(2, 1,
                    "ATK: {!s}".format(ATK.get_component(Player.active).value))
    stat_log.addstr(3, 1,
                    "DEF: {!s}".format(DEF.get_component(Player.active).value))
    stat_log.addstr(4, 1,
                    "TIME: {!s}".format(TIME.get_component(Player.active).value))

    stat_log.addstr(10, 1,
                    "DEPTH: {!s}".format(player_depth.z))
    # log whatever happened this turn (from my_log)
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


def cleanup_removed_components():
    Component.cleanup()
