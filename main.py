import pygame
from core.clock import Clock
from core.graph import Graph
from menu.switch_button import SwitchButton
from menu.main_menu import Menu
from menu.menu_button import MenuButton
from core.presets import save_preset, load_preset
from analysis.slider import Slider
from analysis.table import DataTable


# Pygame Initialization
pygame.init()
GLOBAL_LOCK = False
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Window with Clock and Graphs")


def initialize_projections():
    object_configs = [
        {"class": Clock, "args": (10, 10, 100, 50), "kwargs": {"text_color": "black", "border_color": "black", "bg_color": "darkGray"}},
        {"class": Graph,
         "kwargs": {"is_live": False, "data_file": './data/PriceDay1.csv', "column": 'Price', "size_multiplier": 1.5}},
        {"class": Graph,
         "kwargs": {"is_live": False, "data_file": './data/PriceDay2.csv', "column": 'Price', "size_multiplier": .9}},
        {"class": Graph,
         "kwargs": {"is_live": False, "data_file": './data/PriceDay3.csv', "column": 'Price', "size_multiplier": .9}}
    ]

    return [config["class"](*config.get("args", ()), **config["kwargs"]) for config in object_configs]


projections = initialize_projections()
graphs = [proj for proj in projections if isinstance(proj, Graph)]
max_length = max([len(graph.df) for graph in graphs if graph.df is not None], default=100)

slider = Slider(50, 450, 700, 0, max_length - 1)
projections.append(slider)  # Add slider to projections

font = pygame.font.SysFont(None, 24)
data_table = DataTable(650, 50, graphs, font)
projections.append(data_table)  # Add data table to projections

for graph in graphs:
    slider.add_observer(graph)
slider.add_observer(data_table)

menu_button = MenuButton(700, 10, 80, 40, "Menu")
menu = Menu(700, 60)
projections.extend([menu_button, menu])

dragging = False
dragged_object = None


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 and menu_button.rect.collidepoint(event.pos) and not GLOBAL_LOCK:
                dragged_object = menu_button
                dragging = True
                continue
            if menu.lock_button.rect.collidepoint(event.pos):
                GLOBAL_LOCK = menu.lock_button.toggle()
            elif menu_button.rect.collidepoint(event.pos):
                menu.toggle()
                dragging = False
            elif not GLOBAL_LOCK:
                dragged_object = next((proj for proj in projections if
                                       proj.rect.collidepoint(event.pos) and hasattr(proj, 'update_position')), None)
                dragging = dragged_object is not None
            if menu.save_button.rect.collidepoint(event.pos):
                save_preset(projections)
            elif menu.load_button.rect.collidepoint(event.pos):
                # Load the saved state
                loaded_projections = load_preset()

                # Clear the current projections
                projections.clear()

                menu_button_proj = next((proj for proj in loaded_projections if isinstance(proj, MenuButton)), None)
                if menu_button_proj:
                    menu_button_position = menu_button_proj.rect.topleft
                else:
                    # Handle this case accordingly, maybe set a default position or raise a more descriptive error.
                    menu_button_position = (0, 0)

                menu_proj = next((proj for proj in loaded_projections if isinstance(proj, Menu)), None)
                if menu_proj:
                    menu_position = menu_proj.rect.topleft
                else:
                    # Handle this case accordingly, maybe set a default position or raise a more descriptive error.
                    menu_position = (0, 0)

                # Ensure only one Menu and MenuButton instance exists and append them to the projections
                menu_button = MenuButton(*menu_button_position, 80, 40, "Menu")
                menu = Menu(*menu_position)
                projections.extend([menu_button, menu])

                # Append the rest of the loaded projections to the projections list
                for proj in loaded_projections:
                    if not isinstance(proj, (Menu, MenuButton)):
                        projections.append(proj)

                # Re-establish the slider's interaction with graphs and data table
                loaded_slider = next((proj for proj in projections if isinstance(proj, Slider)), None)
                loaded_graphs = [proj for proj in projections if isinstance(proj, Graph)]
                # Re-establish the slider's interaction with graphs and data table
                loaded_slider = next((proj for proj in projections if isinstance(proj, Slider)), None)
                loaded_graphs = [proj for proj in projections if isinstance(proj, Graph)]
                loaded_data_table = next((proj for proj in projections if isinstance(proj, DataTable)), None)

                # Re-connect slider to its observers (graphs and data table)
                if loaded_slider:
                    for graph in loaded_graphs:
                        loaded_slider.add_observer(graph)
                    if loaded_data_table:
                        loaded_slider.add_observer(loaded_data_table)

            if not GLOBAL_LOCK:
                dragged_object = next((proj for proj in projections if
                                       proj.rect.collidepoint(event.pos) and hasattr(proj, 'update_position')),
                                      None)
                dragging = dragged_object is not None

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            dragged_object = None  # Clear the dragged object

        elif event.type == pygame.MOUSEMOTION and dragging:
            if isinstance(dragged_object, MenuButton):
                dragged_object.update_position(*event.rel)
                menu.update_position(dragged_object.x, dragged_object.y + dragged_object.height)
            else:
                dragged_object.update_position(*event.rel)

        elif event.type == pygame.KEYDOWN and dragged_object:
            funcs = {pygame.K_PLUS: "increase_size", pygame.K_MINUS: "decrease_size"}
            func = getattr(dragged_object, funcs.get(event.key, None), None)
            if func:
                func()

        for proj in projections:
            if isinstance(proj, Slider):
                proj.handle_events(event)

    screen.fill(WHITE)
    for proj in projections:
        if not isinstance(proj, (Menu, MenuButton)):
            proj.display(screen)
    menu_button.display(screen)
    menu.display(screen)
    pygame.display.flip()

pygame.quit()
