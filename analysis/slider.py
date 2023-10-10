import pygame
from utils.observer_pattern import Observable
from utils.uiux import UIElement
class Slider(UIElement, Observable):

    def __init__(self, x, y, width, min_value, max_value):
        UIElement.__init__(self, x, y)  # Initialize UIElement with position (x and y)
        Observable.__init__(self)

        # Set size directly in the Slider
        self.width = width
        self.height = 20  # Assuming this is the height of your slider.

        # Update the rect to account for the new width and height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


        # Rest of the Slider's attributes initialization
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = self.min_value
        self.handle_width = self.width * 0.05
        self.handle_color = (0, 128, 255)  # Blue
        self.track_color = (200, 200, 200)  # Grey

        # Additional attribute to check if the handle is being dragged
        self.dragging = False
        self.dragging_position = False

    def display(self, screen):
        # Draw the background of the slider
        pygame.draw.rect(screen, self.track_color, self.rect)

        # Calculate the handle position based on the current_value
        handle_x = self.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)

        # Draw the handle
        pygame.draw.rect(screen, self.handle_color, (handle_x, self.y, self.handle_width, self.height))

    def handle_events(self, event, is_locked=False):
        handle_x = self.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)
        handle_rect = pygame.Rect(handle_x, self.y, self.handle_width, self.height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and handle_rect.collidepoint(event.pos):  # Left click on handle
                self.dragging = True
            elif event.button == 3 and self.rect.collidepoint(event.pos):  # Right click on slider
                self.dragging_position = True

                if is_locked:
                    self.dragging_position = False
                    return

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.dragging_position = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:  # If dragging the handle
                self.update_value_from_pos(event.pos[0])
            elif self.dragging_position:  # If dragging the entire slider's position
                self.update_position(*event.rel)

    def update_position(self, dx, dy):
        """Update the position of the slider."""
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.notify_observers(self.current_value)

    def is_clicked(self, x, y):
        return self.rect.collidepoint(x, y)

    def update_value_from_pos(self, x):
        relative_x = x - self.x
        self.current_value = self.min_value + relative_x / (self.width - self.handle_width) * (self.max_value - self.min_value)
        self.current_value = max(self.min_value, min(self.max_value, self.current_value))
        self.notify_observers(self.current_value)

    def update(self, value):
        # print("UPDATING", value)
        """Update the slider based on received values."""
        if isinstance(value, tuple):  # Indicates range values
            self.min_value, self.max_value = value
            self.current_value = max(self.min_value, min(self.max_value, self.current_value))
        else:
            relative_x = (value - self.min_value) / (self.max_value - self.min_value) * (self.width - self.handle_width)
            self.update_value_from_pos(self.x + relative_x)

    def serialize(self):
        data = super().serialize()  # Get base class serialization data.
        data.update({
            "type": "Slider",
            "width": self.width,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "current_value": self.current_value
        })
        return data

    @staticmethod
    def deserialize(data):
        width = data.get("width", 400)  # Default to 400 if width is not present.
        slider = Slider(data["x"], data["y"], width, data["min_value"], data["max_value"])
        slider.current_value = data["current_value"]
        return slider


# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Interactive Data Visualization')

    # Graph instances with colors and titles
    test_graph1 = Graph(data_file='./data/strategy_zero/Day1.csv', column='Price1', color=(255, 0, 0), title="Graph 1", strategy_active=True)
    test_graph2 = Graph(data_file='./data/strategy_zero/Day1.csv', column='Price2', color=(0, 255, 0), title="Graph 2", strategy_active=False)

    graphs = [test_graph1, test_graph2]

    # Slider instances
    test_slider = Slider(x=50, y=500, width=700, min_value=0,
                         max_value=max(len(test_graph1.df), len(test_graph2.df)) - 1)
    test_slider.add_observer(test_graph1)
    test_slider.add_observer(test_graph2)

    value_range_slider = ValueRangeSlider(x=50, y=550, width=700, min_value=0, max_value=len(test_graph1.df) - 1)
    value_range_slider.add_observer(test_graph1)  # Link the range slider to the graph

    # DataTable instance
    font = pygame.font.SysFont(None, 24)
    data_table = DataTable(x=650, y=50, graphs=graphs, font=font)
    test_slider.add_observer(data_table)

    dragging = False
    dragged_graph = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle events for the existing slider
            test_slider.handle_events(event)

            # Handle events for the new value range slider
            value_range_slider.handle_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    for graph in graphs:
                        if graph.rect.collidepoint(event.pos):
                            dragging = True
                            dragged_graph = graph
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                if dragged_graph:
                    is_overlapping = dragged_graph.update_position(0, 0, graphs)
                    if is_overlapping:
                        for graph in graphs:
                            if graph != dragged_graph and dragged_graph.rect.colliderect(graph.rect):
                                overlap_area = dragged_graph.rect.clip(graph.rect).width * dragged_graph.rect.clip(
                                    graph.rect).height
                                if overlap_area > 0.5 * (graph.rect.width * graph.rect.height):
                                    # Adjust dragged_graph's position to perfectly overlap with the graph
                                    dragged_graph.x = graph.x
                                    dragged_graph.y = graph.y
                                    dragged_graph.rect.topleft = (graph.x, graph.y)
                dragged_graph = None  # Clear the dragged graph

            elif event.type == pygame.MOUSEMOTION and dragging:
                other_graphs = [graph for graph in graphs if graph != dragged_graph]
                dragged_graph.update_position(event.rel[0], event.rel[1], other_graphs)

        screen.fill(WHITE)
        for current_graph in graphs:
            current_graph.display(screen, graphs)
        test_slider.display(screen)
        value_range_slider.display(screen)  # Display the value range slider
        data_table.display(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
