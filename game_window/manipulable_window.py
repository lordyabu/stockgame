import pygame
from clock import Clock
from stock_graph import Graph
from menuObjects.switch_button import SwitchButton
from menuObjects.menu import Menu
from menuObjects.menu_button import MenuButton

# Pygame Initialization
pygame.init()
GLOBAL_LOCK = False
WHITE = (255, 255, 255)

# Initial window dimensions
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Window with Clock and Graphs")

# Object configurations: You can easily add more objects by adding to this list
object_configs = [
    {"class": Clock, "args": (10, 10, 100, 50), "kwargs": {"text_color": "black", "border_color": "black", "bg_color": "darkGray"}},
    {"class": Graph, "kwargs": {"is_live": False, "data_file": './data/PriceDay.csv', "size_multiplier": 1.5}},
    {"class": Graph, "kwargs": {"is_live": False, "data_file": './data/PriceDay2.csv', "size_multiplier": .9}},
    {"class": Graph, "kwargs": {"is_live": False, "data_file": './data/PriceDay3.csv', "size_multiplier": .9}}
]

# Creating objects dynamically based on the configurations
projections = [config["class"](*config.get("args", ()), **config["kwargs"]) for config in object_configs]

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
            if menu.lock_button.rect.collidepoint(event.pos):
                menu.lock_button.toggle()
                GLOBAL_LOCK = menu.lock_button.is_on

            if not GLOBAL_LOCK:
                dragged_object = next((proj for proj in projections if
                                       proj.rect.collidepoint(event.pos) and hasattr(proj, 'update_position')), None)
                if isinstance(dragged_object, MenuButton):
                    menu.toggle()
                dragging = dragged_object is not None
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            dragged_object.update_position(*event.rel)
        elif event.type == pygame.KEYDOWN and dragged_object:
            funcs = {pygame.K_PLUS: "increase_size", pygame.K_MINUS: "decrease_size"}
            func = getattr(dragged_object, funcs.get(event.key, None), None)
            if func:
                func()

    screen.fill(WHITE)
    for proj in projections:
        proj.display(screen)
    pygame.display.flip()

pygame.quit()
