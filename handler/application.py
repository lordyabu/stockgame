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
from analysis.range_slider import RangeSlider
import cProfile
from PIL import Image, ImageDraw
import config
import sys


class Application:

    def __init__(self, num_vals_table):
        pygame.init()

        # Set display to current screen resolution
        self.WIDTH = pygame.display.Info().current_w
        self.HEIGHT = pygame.display.Info().current_h

        # Initialize in full-screen mode
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Resizable Window with Clock and Graphs")

        self.GLOBAL_LOCK = False
        self.initialize_projections('strategy_zero', num_vals_table)

        self.background_color = (10, 25, 50)

        self.dragging = False
        self.dragged_object = None

        self.frames = []  # List to store frames for GIF
        self.mouse_positions = []


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
        loaded_range_slider = next((proj for proj in self.projections if isinstance(proj, RangeSlider)), None)
        loaded_graphs = [proj for proj in self.projections if isinstance(proj, Graph)]
        loaded_data_table = next((proj for proj in self.projections if isinstance(proj, DataTable)), None)

        # Re-connect slider to its observers (graphs and data table)
        if loaded_slider:
            for graph in loaded_graphs:
                loaded_slider.add_observer(graph)
            if loaded_data_table:
                loaded_slider.add_observer(loaded_data_table)

        if loaded_range_slider:
            for graph in loaded_graphs:
                loaded_range_slider.add_observer(graph)

        # Reconnect the DaySwitch object to the loaded graphs
        loaded_day_switch = next((proj for proj in self.projections if isinstance(proj, DaySwitch)), None)
        if loaded_day_switch:
            loaded_day_switch.graphs = loaded_graphs
            self.day_switch = loaded_day_switch

        self.graphs = loaded_graphs

    def initialize_projections(self, strategy_dir, num_vals_table):
        # Using configurations
        font_graph = pygame.font.SysFont(config.font_graph_name, config.font_graph_size)

        for conf in config.object_configs:
            if conf["class_name"] == "Graph":
                conf["kwargs"]["data_file"] = f'./data/{strategy_dir}/Day1.csv'
                conf["kwargs"]["font"] = font_graph

        self.projections = [eval(conf["class_name"])(*conf.get("args", ()), **conf["kwargs"]) for conf in
                            config.object_configs]

        self.graphs = [proj for proj in self.projections if
                       isinstance(proj, eval(conf["class_name"]))]  # Using eval for dynamic class checking
        max_length = max([len(graph.df) for graph in self.graphs if graph.df is not None], default=100)

        self.slider = Slider(*config.slider_position, config.slider_width, 0, max_length - 1)
        self.projections.append(self.slider)

        font = pygame.font.SysFont(config.font_name, config.font_size)
        self.data_table = DataTable(*config.data_table_position, self.graphs, font, visible_rows=num_vals_table)
        self.projections.append(self.data_table)

        self.slider.add_observer(self.data_table)
        self.menu_button = MenuButton(*config.menu_button_position, *config.menu_button_size, "Menu")
        self.menu = Menu(*config.menu_position)
        self.projections.extend([self.menu_button, self.menu])

        self.day_switch = DaySwitch(*config.day_switch_position, graphs=self.graphs, strategy_dir=strategy_dir)
        self.projections.append(self.day_switch)

        self.range_slider = RangeSlider(*config.range_slider_position, config.slider_width, 0, max_length - 1)
        self.projections.append(self.range_slider)

        for graph in self.graphs:
            graph.add_observer(self.slider)
            self.slider.add_observer(graph)
            self.range_slider.add_observer(graph)

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
        elif self.menu.exit_button.rect.collidepoint(event.pos):
            sys.exit()
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

        if event.button == 3 and self.range_slider.rect.collidepoint(event.pos) and not self.GLOBAL_LOCK:
            dragged_object = self.range_slider
        elif event.button == 1 and self.range_slider.rect.collidepoint(event.pos):
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

    def run_for_duration(self, duration):
        """Run the main loop for a specified duration in seconds."""
        end_time = pygame.time.get_ticks() + duration * 1000  # Convert to milliseconds
        while pygame.time.get_ticks() < end_time:
            self._main_loop_iteration()

    def capture_frame(self):
        """Capture the current Pygame screen frame."""

        # Get the current size of the display
        current_size = pygame.display.get_surface().get_size()
        screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)

        # If the sizes don't match (i.e., the screen was resized),
        # temporarily set the display mode to the current screen size to capture the full screen
        if current_size != screen_size:
            temp_surface = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
            self.screen.blit(temp_surface, (0, 0))

        pygame_surface = pygame.display.get_surface()
        image = Image.frombytes('RGB', pygame_surface.get_size(),
                                pygame.image.tostring(pygame_surface, 'RGB'))
        self.frames.append(image)

        # Reset the display mode to the original size if it was changed
        if current_size != screen_size:
            pygame.display.set_mode(current_size)

    def save_gif(self, filename, duration=100):
        """Save the captured frames as a GIF with mouse pointers overlaid."""
        if self.frames and len(self.frames) == len(self.mouse_positions):
            # Modify frames with mouse position overlay
            modified_frames = []
            for frame, position in zip(self.frames, self.mouse_positions):
                frame_copy = frame.copy()  # To ensure we don't modify the original frame
                draw = ImageDraw.Draw(frame_copy)

                draw_mouse_pointer(draw, position)

                modified_frames.append(frame_copy)

            modified_frames[0].save(filename, save_all=True, append_images=modified_frames[1:], optimize=False,
                                    duration=duration, loop=0)


    def record_mouse_position(self):
        """Record the current mouse position."""
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_positions.append(mouse_pos)

    def _main_loop_iteration(self):
        """One iteration of the main loop."""
        for event in pygame.event.get():
            for graph in self.graphs:
                graph.toggle_button_grid.handle_event(event)
                graph.toggle_button_chart.handle_event(event)
                graph.toggle_button_strategy.handle_event(event)
                graph.toggle_button_color.handle_event(event)

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
                if isinstance(proj, RangeSlider):
                    proj.handle_events(event, self.GLOBAL_LOCK)

            self.capture_frame()
            self.record_mouse_position()

            pygame.display.flip()

        self.screen.fill(self.background_color)
        for proj in self.projections:
            if isinstance(proj, Graph):
                proj.display(self.screen, self.graphs)
                proj.toggle_button_grid.display(self.screen)
                proj.toggle_button_chart.display(self.screen)
                proj.toggle_button_strategy.display(self.screen)
                proj.toggle_button_color.display(self.screen)
            elif not isinstance(proj, (Menu, MenuButton)):
                proj.display(self.screen)
        self.menu_button.display(self.screen)
        self.menu.display(self.screen)
        pygame.display.flip()

    # ... [End of your Application class] ...

    def run(self):
        running = True
        self.dragging = False
        self.dragged_object = None
        while running:
            for event in pygame.event.get():
                for graph in self.graphs:
                    graph.toggle_button_grid.handle_event(event)
                    graph.toggle_button_chart.handle_event(event)
                    graph.toggle_button_strategy.handle_event(event)
                    graph.toggle_button_color.handle_event(event)

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
                    if isinstance(proj, RangeSlider):
                        proj.handle_events(event, self.GLOBAL_LOCK)

            self.menu_button.hover()
            # Display logic
            self.screen.fill(self.background_color)
            for proj in self.projections:

                if isinstance(proj, Graph):
                    proj.display(self.screen, self.graphs)
                    # print('aaaaa')
                    proj.toggle_button_grid.display(self.screen)  # Display the button
                    proj.toggle_button_chart.display(self.screen)
                    proj.toggle_button_strategy.display(self.screen)
                    proj.toggle_button_color.display(self.screen)

                elif not isinstance(proj, (Menu, MenuButton)):
                    proj.display(self.screen)

            self.menu_button.display(self.screen)
            self.menu.display(self.screen)
            pygame.display.flip()

        pygame.quit()


def draw_mouse_pointer(draw, position):
    """Draw a simple arrow resembling a mouse pointer."""
    x, y = position
    pointer_color = 'white'

    # Main triangle of the pointer
    draw.polygon([(x, y), (x + 10, y + 15), (x + 15, y + 10)], fill=pointer_color)


if __name__ == "__main__":
    game = Application(49)
    game.run_for_duration(10)  # Run for 5 seconds for example
    game.save_gif('output_preset.gif', duration=50)  # This will save a gif with each frame having a 100ms duration



