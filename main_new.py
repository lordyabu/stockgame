import pygame
from core.clock import Clock
from core.graph import Graph
from menu.main_menu import Menu
from menu.menu_button import MenuButton
from core.presets import save_preset, load_preset, load_project_state
from analysis.slider import Slider
from analysis.table import DataTable
from core.dayswitch import DaySwitch

# Pygame Initialization
pygame.init()
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Window with Clock and Graphs")
GLOBAL_LOCK = False


def initialize_projections():
    object_configs = [
        {"class": Clock, "args": (10, 10, 100, 50), "kwargs": {"text_color": "black", "border_color": "black", "bg_color": "darkGray"}},
        {"class": Graph,
         "kwargs": {"is_live": False, "data_file": './data/Day1/PriceDay2.csv', "column": 'Price', "size_multiplier": 1.5, "color": (255, 0, 0), "title": "Graph 1", "original_title": "Graph 1"}},
        {"class": Graph,
         "kwargs": {"is_live": False, "data_file": './data/Day1/PriceDay3.csv', "column": 'Price', "size_multiplier": .9, "color": (0, 255, 0), "title": "Graph 2", "original_title": "Graph 2"}},
        {"class": Graph,
         "kwargs": {"is_live": False, "data_file": './data/Day1/PriceDay1.csv', "column": 'Price', "size_multiplier": .9, "color": (0, 0, 255), "title": "Graph 3", "original_title": "Graph 3"}}
    ]

    return [config["class"](*config.get("args", ()), **config["kwargs"]) for config in object_configs]


def handle_mouse_down(event, projections, dragged_object, menu, menu_button, day_switch):
    global GLOBAL_LOCK

    # If the day_switch is clicked on
    if day_switch.rect.collidepoint(event.pos):
        day_switch.check_click(event.pos)
        return day_switch

    # If right-click on menu_button and not locked
    if event.button == 3 and menu_button.rect.collidepoint(event.pos) and not GLOBAL_LOCK:
        return menu_button

    # If lock_button on the menu is clicked
    if menu.lock_button.rect.collidepoint(event.pos):
        GLOBAL_LOCK = menu.lock_button.toggle()
        return None

    # If menu_button is clicked
    if menu_button.rect.collidepoint(event.pos):
        menu.toggle()
        return None

    # If save_button on the menu is clicked
    if menu.save_button.rect.collidepoint(event.pos):
        save_preset(projections)
        return None

    # If load_button on the menu is clicked
    elif menu.load_button.rect.collidepoint(event.pos):
        slider, menu_button, menu, data_table, day_switch, graphs = load_project_state(projections)
        return None

    # If any other draggable projection is clicked on
    colliding_projection = next(
        (proj for proj in projections if proj.rect.collidepoint(event.pos) and hasattr(proj, 'update_position')), None)
    if colliding_projection:
        return colliding_projection

    return None


def handle_mouse_motion(event, dragged_object, graphs, menu):
    # If the dragged object is a MenuButton
    if isinstance(dragged_object, MenuButton):
        dragged_object.update_position(*event.rel)
        menu.update_position(dragged_object.x, dragged_object.y + dragged_object.height)
    # If the dragged object is a Graph
    elif isinstance(dragged_object, Graph):
        other_graphs = [graph for graph in graphs if graph != dragged_object]
        dragged_object.update_position(event.rel[0], event.rel[1], other_graphs)
    # For other draggable objects
    else:
        dragged_object.update_position(*event.rel)



def handle_key_down(event, dragged_object):
    funcs = {pygame.K_PLUS: "increase_size", pygame.K_MINUS: "decrease_size"}
    func = getattr(dragged_object, funcs.get(event.key, None), None)
    if func:
        func()


def handle_slider_events(event, slider):
    if isinstance(event, Slider):
        slider.handle_events(event)

def handle_display(screen, projections, graphs):
    screen.fill(WHITE)
    for proj in projections:
        if isinstance(proj, Graph):
            proj.display(screen, graphs)
        else:
            proj.display(screen)
    pygame.display.flip()


def main():
    projections = initialize_projections()

    # Extract the graphs from the initialized projections
    graphs = [proj for proj in projections if isinstance(proj, Graph)]
    max_length = max([len(graph.df) for graph in graphs if graph.df is not None], default=100)

    # Initialize and set up the slider component
    slider = Slider(50, 450, 700, 0, max_length - 1)
    projections.append(slider)

    # Initialize and set up the data table component
    font = pygame.font.SysFont(None, 24)
    data_table = DataTable(650, 50, graphs, font)
    projections.append(data_table)

    # Add the data_table as an observer of the slider
    slider.add_observer(data_table)

    for graph in graphs:
        slider.add_observer(graph)

    # Initialize the menu_button and menu components
    menu_button = MenuButton(700, 10, 80, 40, "Menu")
    menu = Menu(700, 60)
    projections.extend([menu_button, menu])

    # Initialize the day_switch component
    day_switch = DaySwitch(650, 10, graphs=graphs)
    projections.append(day_switch)

    # Check if all essential components are initialized
    if not all([menu_button, menu, day_switch, slider]):
        raise Exception("Initialization error: One or more essential components are missing.")

    dragging = False
    dragged_object = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                dragged_object = handle_mouse_down(event, projections, dragged_object, menu, menu_button, day_switch)
                dragging = dragged_object is not None
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                dragged_object = None
            elif event.type == pygame.MOUSEMOTION and dragging:
                handle_mouse_motion(event, dragged_object, graphs, menu)
            elif event.type == pygame.KEYDOWN and dragged_object:
                handle_key_down(event, dragged_object)

            # Handling Slider Events
            handle_slider_events(event, slider)

        # Refreshing and displaying the components
        handle_display(screen, projections, graphs)

    pygame.quit()


if __name__ == "__main__":
    main()
