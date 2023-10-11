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
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.min_value = min_value
        self.max_value = max_value
        self.start_value = self.min_value
        self.end_value = self.max_value

        self.handle_width = self.width * 0.05

        self.track_color = (200, 200, 200)  # Grey

        # Flags for dragging
        self.dragging_start = False
        self.dragging_end = False

        self.dragging_position = False

        self.handle_color = (50, 50, 50)  # Grey for both start and end handles
        self.radius = 15  # Radius for the circle handles



    def display(self, screen):
        # Draw the background of the slider as a thin line
        pygame.draw.line(screen, self.track_color, (self.x, self.y), (self.x + self.width, self.y), 2)

        # Calculate handle positions
        start_handle_x = self.rect.x + (self.start_value - self.min_value) / (self.max_value - self.min_value) * self.width
        end_handle_x = self.rect.x + (self.end_value - self.min_value) / (self.max_value - self.min_value) * self.width

        pygame.draw.circle(screen, self.handle_color, (int(start_handle_x), self.y), self.radius)
        pygame.draw.circle(screen, self.handle_color, (int(end_handle_x), self.y), self.radius)

        font = pygame.font.SysFont('Arial', 16)
        text = font.render('Interval Slider', True, WHITE)
        screen.blit(text, (self.x + self.width - text.get_width(), self.y - self.radius * 2 - text.get_height()))

    def handle_events(self, event, is_locked=False):
        start_handle_x = self.rect.x + (self.start_value - self.min_value) / (
                    self.max_value - self.min_value) * self.width
        end_handle_x = self.rect.x + (self.end_value - self.min_value) / (self.max_value - self.min_value) * self.width

        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_x, clicked_y = event.pos

            # Check if the start handle was clicked
            if event.button == 1 and (start_handle_x - clicked_x) ** 2 + (self.y - clicked_y) ** 2 <= self.radius ** 2:
                self.dragging_start = True

            # Check if the end handle was clicked
            elif event.button == 1 and (end_handle_x - clicked_x) ** 2 + (self.y - clicked_y) ** 2 <= self.radius ** 2:
                self.dragging_end = True

            # Right-click to move the entire slider
            elif self.rect.collidepoint(event.pos) and event.button == 3:
                if is_locked:
                    self.dragging_position = False
                    return
                self.dragging_position = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_start = False
            self.dragging_end = False
            self.dragging_position = False

        elif event.type == pygame.MOUSEMOTION:
            prev_start_value = self.start_value  # Store previous values before updating
            prev_end_value = self.end_value

            if self.dragging_start:
                self.update_value_from_pos(event.pos[0], "start")
            elif self.dragging_end:
                self.update_value_from_pos(event.pos[0], "end")

            if self.start_value > self.end_value:  # Check if values have crossed over
                self.start_value, self.end_value = prev_start_value, prev_end_value  # Revert to previous values

            if self.dragging_position:  # If dragging the entire slider's position
                self.update_position(*event.rel)

            self.update_slider_positions()

    def update_position(self, dx, dy):
        """Update the position of the slider."""
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.notify_observers((self.start_value, self.end_value))


    def update_value_from_pos(self, x, handle_type):
        relative_x = x - self.rect.x

        value = int(self.min_value + relative_x / (self.width - self.handle_width) * (self.max_value - self.min_value))
        value = max(self.min_value, min(self.max_value, value))

        if handle_type == "start":
            # Ensure start_value doesn't surpass end_value
            self.start_value = min(value, self.end_value - 1)
        elif handle_type == "end":
            # Ensure end_value doesn't go below start_value
            self.end_value = max(value, self.start_value + 1)

        self.notify_observers((self.start_value, self.end_value))

    def update_slider_positions(self):
        MIN_GAP = 1  # Ensure at least one data point between the two sliders

        if self.end_value - self.start_value < MIN_GAP:
            if self.dragging_start:
                self.start_value = self.end_value - MIN_GAP
            elif self.dragging_end:
                self.end_value = self.start_value + MIN_GAP


    def serialize(self):
        data = super().serialize()  # Get base class serialization data.
        data.update({
            "type": "RangeSlider",
            "width": self.width,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "start_value": self.start_value,
            "end_value": self.end_value
        })
        return data

    @staticmethod
    def deserialize(data):
        width = data.get("width", 700)  # Default to 700 if width is not present.
        range_slider = RangeSlider(data["x"], data["y"], width, data["min_value"], data["max_value"])
        range_slider.start_value = data.get("start_value", data["min_value"])  # Default to min_value if start_value is not present.
        range_slider.end_value = data.get("end_value", data["max_value"])    # Default to max_value if end_value is not present.
        return range_slider


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