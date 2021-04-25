"""
randrmenu

A little script using rofi/dmenu to configure x server screens.
"""
from dynmen.rofi import Rofi

import pyrandr as randr

ROTATIONS = {1: "rot. normal", 2: "rot. left", 3: "rot. inverse", 4: "rot. right"}
finished = bool()


def change_resolution(screen):
    available_resolutions = {
        f"{res[0]}x{res[1]}": res for res in screen.available_resolutions()
    }
    menu = Rofi()
    menu.prompt = "Choose resolution"
    selected_resolution = menu(available_resolutions).value
    screen.set_resolution(selected_resolution)

def change_rotation(screen):
    available_rotations = dict(map(reversed, ROTATIONS.items()))
    menu = Rofi()
    menu.prompt = "Choose rotation"
    rotation = menu(available_rotations).value
    screen.rotate(rotation)


def change_position(screen):
    available_positions = {
        "LeftOf": 1,
        "RightOf": 2,
        "Above": 3,
        "Below": 4,
        "SameAs": 5,
    }
    menu = Rofi()
    menu.prompt = "Choose position"
    position = menu(available_positions).value

    available_relatives = {
        peer.name: peer for peer in randr.enabled_screens() if peer.name != screen.name
    }
    if not available_relatives:
        print("No other screen to relate to")
        return
    menu = Rofi()
    menu.prompt = "In regard to which screen ?"
    relative = menu(available_relatives).value
    print(relative.name)

    screen.set_position(position, relative.name)


def enable_screen(screen):
    screen.set_enabled(True)


def disable_screen(screen):
    if len(randr.enabled_screens()) == 1:
        print("Too risky to shut down last screen, refusing")
        return
    screen.set_enabled(False)


def save_and_exit(screen):
    global finished
    screen.apply_settings()
    finished = True


def craft_actions(screen):
    """
    Returns a dict of all the available actions on a screen.
    If the screen is disabled you wwon't be able to change irs resolution.
    """
    actions = {"save and exit": save_and_exit}
    if screen.set.is_enabled:
        actions["disable"] = disable_screen
        actions["change resolution"] = change_resolution
        actions["change position"] = change_position
        actions["change rotation"] = change_rotation
    else:
        actions["enable"] = enable_screen
    return actions


def craft_screen_name(screen):
    """
    Creates a string from a screen which describes it :
    name (enabled, primary, ...)
    """
    name = screen.name
    properties = []
    if screen.is_enabled():
        properties.append("enabled")
        if screen.rotation != 1:
            properties.append(ROTATIONS[screen.rotation])

    if screen.primary:
        properties.append("primary")

    return "{name} ({properties})".format(name=name, properties=", ".join(properties))


def select_screen():
    """
    Gets all connected screens, asks the user which one to edit and then return
    the screen.
    """
    menu = Rofi()
    connected_screens = {
        craft_screen_name(screen): screen for screen in randr.connected_screens()
    }

    menu.prompt = "Connected screens"

    return menu(connected_screens).value


def select_action(screen):
    """
    Takes a screen, prompt the user for wwhich action to do.
    Returns a function that does the selected action.
    """
    actions = craft_actions(screen)
    menu = Rofi()
    menu.prompt = f"What to do on screen {screen.name} ?"
    action = menu(actions).value
    return action


def main():
    """
    Main function, contains main loop
    """
    global finished  # TODO(shaka): get rid of global, maybe with a context object or with kwargs
    finished = False
    screen = select_screen()
    print(screen, "selected")
    while not finished:
        action = select_action(screen)
        print(action)
        action(screen)


if __name__ == "__main__":
    main()
