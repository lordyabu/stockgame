import pygame
from utils.observering import Observable
from utils.uiux import UIElement
class Slider(UIElement, Observable):
    """
    A class used to represent an interactive slider UI element.

    Methods
    -------
    display(screen)
        Displays the slider on the given Pygame screen.
    handle_events(event, is_locked=False)
        Handles Pygame events like mouse clicks and movements.
    update_position(dx, dy)
        Updates the position of the slider.
    is_clicked(x, y)
        Returns True if the given x, y coordinates intersect the slider.
    update_value_from_pos(x)
        Updates the current value based on the handle's x-coordinate.
    update(value)
        Updates the slider based on the provided value or range.
    serialize()
        Returns a dictionary containing slider's data.
    deserialize(data)
        Returns a new Slider instance from the provided serialized data.
    """


    def __init__(self, x, y, width, min_value, max_value):
        """
        Constructs all the necessary attributes for the Slider object.

        Parameters
        ----------
        x : int
            The x-coordinate of the slider.
        y : int
            The y-coordinate of the slider.
        width : int
            The width of the slider.
        min_value : int or float
            The minimum value of the slider.
        max_value : int or float
            The maximum value of the slider.
        """
        UIElement.__init__(self, x, y)  # Initialize UIElement with position (x and y)
        Observable.__init__(self)

        self.width = width
        self.height = 20  # Assuming this is the height of your slider.
        self.radius = 10  # Radius of the slider handle

        self.rect = pygame.Rect(self.x, self.y - self.radius // 2, self.width, self.height + self.radius)

        self.min_value = min_value
        self.max_value = max_value
        self.current_value = self.min_value

        self.handle_color = (50, 50, 50)  # Black
        self.track_color = (200, 200, 200)  # Grey

        self.dragging = False
        self.dragging_position = False

        self.handle_width = self.radius * 2

        self.font = pygame.font.SysFont('Arial', 16)  # Use Arial font with a size of 24 pixels.

    def display(self, screen):
        """
        Displays the slider on the given Pygame screen.

        Parameters
        ----------
        screen : pygame.Surface
            The Pygame screen where the slider should be displayed.
        """
        # Calculate the handle position based on the current_value
        proportion = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.x + proportion * (self.width - self.handle_width) + self.radius

        line_thickness = 3  # Adjust for desired thickness
        line_alpha = 100  # 78% transparency (adjust this as needed)

        # Drawing the left segment of the line with the same color as the handle
        pygame.draw.line(screen, self.handle_color + (line_alpha,),
                         (self.x, self.y), (handle_x - self.radius, self.y),
                         line_thickness)
        # Drawing the right segment of the line with the original color
        pygame.draw.line(screen, self.track_color + (line_alpha,),
                         (handle_x + self.radius, self.y), (self.x + self.width, self.y),
                         line_thickness)

        # Create the transparent handle
        circle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, self.handle_color + (100,),
                           (self.radius, self.radius), self.radius)
        screen.blit(circle_surface, (int(handle_x) - self.radius, self.y - self.radius))

        # Draw the semi-transparent text
        text = self.font.render('Time Slider', True, WHITE)
        text_surface = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
        text_surface.blit(text, (0, 0))
        text_surface.set_alpha(100)
        screen.blit(text_surface, (self.x + self.width - text.get_width(),
                                   self.y - self.radius * 2 - text.get_height()))

    def handle_events(self, event, is_locked=False):
        """
        Handle mouse events for the slider, such as dragging the handle or the entire slider.

        Parameters
        ----------
        event : pygame.Event
            The Pygame event to be handled.
        is_locked : bool, optional
            If True, disables dragging the entire slider's position, default is False.
        """
        proportion = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.x + proportion * (self.width - self.handle_width) + self.radius
        padding = 10
        handle_rect = pygame.Rect(handle_x - self.radius - padding, self.y - self.radius - padding,
                                  self.handle_width + 2 * padding, self.handle_width + 2 * padding)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if (event.button == 1 or event.button == 3) and handle_rect.collidepoint(
                    event.pos):  # Left or right click on handle

                self.dragging = True
            elif (event.button == 1 or event.button == 3) and self.rect.collidepoint(
                    event.pos):  # Left or right click on slider
                # Right click on slider
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
        """
        Update the position of the slider based on the given deltas.

        Parameters
        ----------
        dx : int
            The change in the x-coordinate.
        dy : int
            The change in the y-coordinate.
        """
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.notify_observers(self.current_value)

    def is_clicked(self, x, y):
        """
        Check if the slider is clicked based on given coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the click.
        y : int
            The y-coordinate of the click.

        Returns
        -------
        bool
            True if the slider was clicked, otherwise False.
        """
        return self.rect.collidepoint(x, y)

    def update_value_from_pos(self, x):
        """
        Update the slider's current value based on the handle's x-coordinate.

        Parameters
        ----------
        x : int
            The x-coordinate of the handle.
        """
        # Clamp the x-position within the bounds of the slider.
        x = max(self.x + self.radius, min(self.x + self.width - self.radius, x))

        # Calculate the relative position
        relative_x = x - self.x - self.radius
        proportion = relative_x / (self.width - self.handle_width)

        # Update the current value
        self.current_value = self.min_value + proportion * (self.max_value - self.min_value)
        self.current_value = max(self.min_value, min(self.max_value, self.current_value))
        self.notify_observers(self.current_value)

    def update(self, value):
        """
        Update the slider based on received values or range.

        Parameters
        ----------
        value : int, float, or tuple
            If tuple, indicates a range with (min_value, max_value). Otherwise, indicates a single value.
        """
        if isinstance(value, tuple):  # Indicates range values
            self.min_value, self.max_value = value
            self.current_value = max(self.min_value, min(self.max_value, self.current_value))
            self.notify_observers(self.current_value)
        else:
            relative_x = (value - self.min_value) / (self.max_value - self.min_value) * (self.width - self.handle_width)
            self.update_value_from_pos(self.x + relative_x)

    def serialize(self):
        """
        Serialize the slider's data into a dictionary.

        Returns
        -------
        dict
            Dictionary containing slider's serialized data.
        """
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
        """
        Create a new Slider instance from the provided serialized data.

        Parameters
        ----------
        data : dict
            The serialized slider data.

        Returns
        -------
        Slider
            A new Slider instance.
        """
        width = data.get("width", 400)  # Default to 400 if width is not present.
        slider = Slider(data["x"], data["y"], width, data["min_value"], data["max_value"])
        slider.current_value = data["current_value"]
        return slider


def main():
    # Colors
    WHITE = (255, 255, 255)

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
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
