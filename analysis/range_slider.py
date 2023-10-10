import pygame
from core.graph import Graph
from analysis.slider import Slider
from analysis.table import DataTable
from utils.observer_pattern import Observable
from utils.uiux import UIElement

class RangeSlider(UIElement, Observable):
    def __init__(self, x, y, width, min_value, max_value):
        super().__init__(x, y)
        Observable.__init__(self)

        self.width = width
        self.height = 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.min_value = min_value
        self.max_value = max_value
        self.start_value = self.min_value
        self.end_value = self.max_value

        self.handle_width = self.width * 0.05
        self.handle_color = (0, 128, 255)  # Blue
        self.track_color = (200, 200, 200)  # Grey

        # Flags for dragging
        self.dragging_start = False
        self.dragging_end = False

    def display(self, screen):
        # Draw the background of the slider
        pygame.draw.rect(screen, self.track_color, self.rect)

        # Calculate handle positions
        start_handle_x = self.x + (self.start_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)
        end_handle_x = self.x + (self.end_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)

        # Draw the handles
        pygame.draw.rect(screen, self.handle_color, (start_handle_x, self.y, self.handle_width, self.height))
        pygame.draw.rect(screen, self.handle_color, (end_handle_x, self.y, self.handle_width, self.height))

    def handle_events(self, event):
        start_handle_x = self.x + (self.start_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)
        end_handle_x = self.x + (self.end_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)

        start_handle_rect = pygame.Rect(start_handle_x, self.y, self.handle_width, self.height)
        end_handle_rect = pygame.Rect(end_handle_x, self.y, self.handle_width, self.height)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if start_handle_rect.collidepoint(event.pos):
                self.dragging_start = True
            elif end_handle_rect.collidepoint(event.pos):
                self.dragging_end = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_start = False
            self.dragging_end = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_start:
                self.update_value_from_pos(event.pos[0], "start")
            elif self.dragging_end:
                self.update_value_from_pos(event.pos[0], "end")

            self.update_slider_positions()  # Ensure the minimum gap after updating slider values

    def update_value_from_pos(self, x, handle_type):
        relative_x = x - self.x
        value = int(self.min_value + relative_x / (self.width - self.handle_width) * (self.max_value - self.min_value))
        value = max(self.min_value, min(self.max_value, value))
        if handle_type == "start":
            self.start_value = value
            # Ensure start_value doesn't surpass end_value
            self.start_value = min(self.start_value, self.end_value)
        elif handle_type == "end":
            self.end_value = value
            # Ensure end_value doesn't go below start_value
            self.end_value = max(self.end_value, self.start_value)
        self.notify_observers((self.start_value, self.end_value))

    def update_slider_positions(self):
        MIN_GAP = 1  # Ensure at least one data point between the two sliders

        if self.end_value - self.start_value < MIN_GAP:
            if self.dragging_start:
                self.start_value = self.end_value - MIN_GAP
            elif self.dragging_end:
                self.end_value = self.start_value + MIN_GAP


# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Interactive Data Visualization')

    # Create graph instances with colors and titles
    test_graph1 = Graph(data_file='./data/strategy_zero/Day1.csv', column='Price1', color=(255, 0, 0), title="Graph 1",
                        strategy_active=True)
    test_graph2 = Graph(data_file='./data/strategy_zero/Day1.csv', column='Price2', color=(0, 255, 0), title="Graph 2",
                        strategy_active=False)

    graphs = [test_graph1, test_graph2]

    # Create Slider instance
    # test_slider = Slider(x=50, y=500, width=700, min_value=0,
    #                      max_value=max(len(test_graph1.df), len(test_graph2.df)) - 1)
    # for graph in graphs:
    #     test_slider.add_observer(graph)

    # Create RangeSlider instance
    value_range_slider = RangeSlider(x=50, y=550, width=700, min_value=0, max_value=len(test_graph1.df) - 1)
    value_range_slider.add_observer(test_graph1)
    value_range_slider.add_observer(test_graph2)

    # Create DataTable instance
    font = pygame.font.SysFont(None, 24)
    data_table = DataTable(x=650, y=50, graphs=graphs, font=font)
    # test_slider.add_observer(data_table)

    running = True
    dragging = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # test_slider.handle_events(event)
            value_range_slider.handle_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                for graph in graphs:
                    if graph.rect.collidepoint(event.pos):
                        dragging = True
                        dragged_graph = graph
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                dragged_graph = None  # Reset the dragged object

        screen.fill(WHITE)
        for graph in graphs:
            graph.display(screen)
        # test_slider.display(screen)
        value_range_slider.display(screen)
        data_table.display(screen)
        pygame.display.flip()

    pygame.quit()