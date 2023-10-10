import pygame
from core.clock import Clock
from core.graph import Graph
from menu.switch_button import SwitchButton
from menu.main_menu import Menu
from menu.menu_button import MenuButton
from core.presets import save_preset, load_preset
from analysis.slider import Slider
from analysis.table import DataTable
from core.dayswitch import DaySwitch

class Application:

    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Resizable Window with Clock and Graphs")
        self.GLOBAL_LOCK = False
        self.initialize_projections('strategy_zero')


        self.dragging = False
        self.dragged_object = None
        # ... more initialization stuff ...


    def load_saved_state(self):
        # This is a refactor of the loading functionality

        # Load the saved state
        loaded_projections = load_preset()

        # Clear the current projections
        self.projections.clear()

        # Append the loaded projections
        self.projections.extend(loaded_projections)

        # Re-establish the slider's interaction with graphs and data table
        loaded_slider = next((proj for proj in self.projections if isinstance(proj, Slider)), None)
        loaded_graphs = [proj for proj in self.projections if isinstance(proj, Graph)]
        loaded_data_table = next((proj for proj in self.projections if isinstance(proj, DataTable)), None)

        # Re-connect slider to its observers (graphs and data table)
        if loaded_slider:
            for graph in loaded_graphs:
                loaded_slider.add_observer(graph)
            if loaded_data_table:
                loaded_slider.add_observer(loaded_data_table)

        # Reconnect the DaySwitch object to the loaded graphs
        loaded_day_switch = next((proj for proj in self.projections if isinstance(proj, DaySwitch)), None)
        if loaded_day_switch:
            loaded_day_switch.graphs = loaded_graphs
            self.day_switch = loaded_day_switch
    def initialize_projections(self, strategy_dir):
        object_configs = [
            {"class": Clock, "args": (10, 10, 100, 50),
             "kwargs": {"text_color": "black", "border_color": "black", "bg_color": "darkGray"}},
            {"class": Graph,
             "kwargs": {"is_live": False, "data_file": f'./data/{strategy_dir}/Day1.csv', "column": 'Price1',
                        "size_multiplier": 1.5, "color": (255, 0, 0), "title": "Graph 1", "original_title": "Graph 1", "strategy_active": True}},
            {"class": Graph,
             "kwargs": {"is_live": False, "data_file": f'./data/{strategy_dir}/Day1.csv', "column": 'Price2',
                        "size_multiplier": .9, "color": (0, 255, 0), "title": "Graph 2", "original_title": "Graph 2", "strategy_active": True}},
            {"class": Graph,
             "kwargs": {"is_live": False, "data_file": f'./data/{strategy_dir}/Day1.csv', "column": 'Price3',
                        "size_multiplier": .9, "color": (0, 0, 255), "title": "Graph 3", "original_title": "Graph 3", "strategy_active": True}}
        ]

        self.projections = [config["class"](*config.get("args", ()), **config["kwargs"]) for config in object_configs]

        self.graphs = [proj for proj in self.projections if isinstance(proj, Graph)]
        max_length = max([len(graph.df) for graph in self.graphs if graph.df is not None], default=100)

        self.slider = Slider(50, 450, 700, 0, max_length - 1)
        self.projections.append(self.slider)

        font = pygame.font.SysFont(None, 24)
        self.data_table = DataTable(650, 50, self.graphs, font)
        self.projections.append(self.data_table)

        self.slider.add_observer(self.data_table)

        self.menu_button = MenuButton(700, 10, 80, 40, "Menu")
        self.menu = Menu(700, 60)
        self.projections.extend([self.menu_button, self.menu])

        self.day_switch = DaySwitch(650, 10, graphs=self.graphs, strategy_dir=strategy_dir)
        self.projections.append(self.day_switch)

        for graph in self.graphs:
            self.slider.add_observer(graph)

    def handle_mouse_down(self, event):
        dragged_object = None

        # Prioritize handling of the menu and its buttons first
        if event.button == 3 and self.menu_button.rect.collidepoint(event.pos) and not self.GLOBAL_LOCK:
            dragged_object = self.menu_button
        elif self.menu.lock_button.rect.collidepoint(event.pos):
            self.GLOBAL_LOCK = self.menu.lock_button.toggle()
        elif self.menu_button.rect.collidepoint(event.pos):
            self.menu.toggle()
        elif self.menu.save_button.rect.collidepoint(event.pos):
            save_preset(self.projections)
        elif self.menu.load_button.rect.collidepoint(event.pos):
            self.load_saved_state()
        elif not self.GLOBAL_LOCK and not dragged_object:
            dragged_object = next((proj for proj in self.projections if
                                   proj.rect.collidepoint(event.pos) and hasattr(proj, 'update_position')), None)

        # Check DaySwitch clicks last since they should have higher priority than general draggable projections.
        self.day_switch.check_click(event.pos)
        if event.button == 1 and self.day_switch.rect.collidepoint(event.pos):
            dragged_object = self.day_switch


        # Check if right-clicking the slider
        if event.button == 3 and self.slider.rect.collidepoint(event.pos) and not self.GLOBAL_LOCK:
            dragged_object = self.slider
        # Make sure the slider isn't set as dragged_object on left-click
        elif event.button == 1 and self.slider.rect.collidepoint(event.pos):
            dragged_object = None

        # If we found an object to drag, set the dragging flag
        if dragged_object:
            self.dragging = True
            self.dragged_object = dragged_object

    def handle_video_resize(self, event):
        """Handles the window resizing."""
        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    def handle_mouse_up(self):
        """Handles mouse button release."""
        self.dragging = False
        self.dragged_object = None

    def handle_mouse_motion(self, event, is_locked=False):
        """Handles mouse movements."""
        if is_locked and not isinstance(self.dragged_object, Slider):
            return

        if isinstance(self.dragged_object, MenuButton):
            self.dragged_object.update_position(*event.rel)
            self.menu.update_position(self.dragged_object.x, self.dragged_object.y + self.dragged_object.height)
        elif isinstance(self.dragged_object, Graph):
            other_graphs = [graph for graph in self.graphs if graph != self.dragged_object]
            self.dragged_object.update_position(event.rel[0], event.rel[1], other_graphs)
        elif isinstance(self.dragged_object, Slider):
            self.dragged_object.update_position(*event.rel)  # Ensure the slider's position is updated correctly
        else:
            self.dragged_object.update_position(*event.rel)

    def handle_key_down(self, event):
        """Handles key presses."""
        if self.dragged_object:
            funcs = {pygame.K_PLUS: "increase_size", pygame.K_MINUS: "decrease_size"}
            func = getattr(self.dragged_object, funcs.get(event.key, None), None)
            if func:
                func()

    # ... other methods ...

    def run(self):
        running = True
        self.dragging = False
        self.dragged_object = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_video_resize(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up()
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    self.handle_mouse_motion(event, self.GLOBAL_LOCK)
                elif event.type == pygame.KEYDOWN and self.dragged_object:
                    self.handle_key_down(event)

                # Event handling for slider
                for proj in self.projections:
                    if isinstance(proj, Slider):
                        proj.handle_events(event, self.GLOBAL_LOCK)

            # Display logic
            self.screen.fill((255, 255, 255))
            for proj in self.projections:
                if isinstance(proj, Graph):
                    proj.display(self.screen, self.graphs)
                elif not isinstance(proj, (Menu, MenuButton)):
                    proj.display(self.screen)
            self.menu_button.display(self.screen)
            self.menu.display(self.screen)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    app = Application()
    app.run()
