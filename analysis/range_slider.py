import pygame
from core.graph import Graph
from analysis.slider import Slider
from analysis.table import DataTable
from utils.observering import Observable
from utils.uiux import UIElement

class RangeSlider(UIElement, Observable):
    """
    A slider allowing selection of a range of values.

    Methods
    -------
    display(screen)
        Render the slider on the given screen.
    handle_events(event, is_locked=False)
        Handle mouse events for interactions with the slider.
    update_position(dx, dy)
        Update the slider's position based on x and y deltas.
    update_value_from_pos(x, handle_type)
        Update the slider values based on the given x-coordinate and handle type.
    update_slider_positions()
        Adjust the slider positions if they are too close or overlapping.
    serialize()
        Convert the slider's state to a dictionary.
    deserialize(data)
        Create a RangeSlider instance from a dictionary.
    """
    def __init__(self, x, y, width, min_value, max_value):
        """
        Initialize a RangeSlider instance.

        Parameters
        ----------
        x : int
            x-coordinate of the top-left corner of the slider.
        y : int
            y-coordinate of the top-left corner of the slider.
        width : int
            Width of the slider.
        min_value : int, float
            Minimum value of the slider range.
        max_value : int, float
            Maximum value of the slider range.
        """
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
        self.radius = 10  # Radius for the circle handles

        self.font = pygame.font.SysFont('Arial', 16)

    def display(self, screen):
        """
        Render the slider on the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The Pygame screen to render the slider on.
        """

        WHITE = (255, 255, 255)
        start_handle_x = self.rect.x + (self.start_value - self.min_value) / (
                    self.max_value - self.min_value) * self.width
        end_handle_x = self.rect.x + (self.end_value - self.min_value) / (self.max_value - self.min_value) * self.width
        line_thickness = 3  # Making the line thicker
        line_alpha = 100  # 78% transparency (adjust this as needed)

        # Drawing the line segments
        # Leftmost to left handle
        pygame.draw.line(screen, self.handle_color + (line_alpha,),
                         (self.x, self.y), (start_handle_x - self.radius, self.y),
                         line_thickness)
        # Left handle to right handle
        pygame.draw.line(screen, self.track_color + (line_alpha,),
                         (start_handle_x + self.radius, self.y), (end_handle_x - self.radius, self.y),
                         line_thickness)
        # Right handle to rightmost
        pygame.draw.line(screen, self.handle_color + (line_alpha,),
                         (end_handle_x + self.radius, self.y), (self.x + self.width, self.y),
                         line_thickness)

        # Draw the handles
        pygame.draw.circle(screen, self.handle_color, (int(start_handle_x), self.y), self.radius)
        pygame.draw.circle(screen, self.handle_color, (int(end_handle_x), self.y), self.radius)

        # Draw the semi-transparent text label
        text = self.font.render('Interval Slider', True, WHITE)
        text_surface = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
        text_surface.blit(text, (0, 0))
        text_surface.set_alpha(100)
        screen.blit(text_surface,
                    (self.x + self.width - text.get_width(), self.y - self.radius * 2 - text.get_height()))

    def handle_events(self, event, is_locked=False):
        """
        Handle mouse events for interactions with the slider.

        Parameters
        ----------
        event : pygame.Event
            The Pygame event to be handled.
        is_locked : bool, optional
            If True, disables dragging the entire slider's position, default is False.
        """
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

            BUFFER = 10  # Adjust this value based on how much bigger you want the click area to be
            enlarged_rect = pygame.Rect(self.rect.x - BUFFER, self.rect.y - BUFFER, self.rect.width + 2 * BUFFER,
                                        self.rect.height + 2 * BUFFER)

            # Check if the click is inside the enlarged rectangle
            if enlarged_rect.collidepoint(event.pos) and (event.button == 3 or event.button == 1):
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
        """
        Update the slider's position based on x and y deltas.

        Parameters
        ----------
        dx : int
            Change in the x-coordinate.
        dy : int
            Change in the y-coordinate.
        """
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.notify_observers((self.start_value, self.end_value))

    def update_value_from_pos(self, x, handle_type):
        """
        Update the slider values based on the given x-coordinate and handle type.

        Parameters
        ----------
        x : int
            x-coordinate where the change happened.
        handle_type : str
            Type of handle being moved ("start" or "end").
        """
        relative_x = x - self.rect.x
        value = int(self.min_value + relative_x / (self.width - self.handle_width) * (self.max_value - self.min_value))
        value = max(self.min_value, min(self.max_value, value))

        MIN_GAP = 5  # Ensure at least one data point between the two sliders

        if handle_type == "start":
            self.start_value = min(value, self.end_value - MIN_GAP)
        elif handle_type == "end":
            self.end_value = max(value, self.start_value + MIN_GAP)

        self.notify_observers((self.start_value, self.end_value))

    def update_slider_positions(self):
        """
        Adjust the slider positions if they are too close or overlapping.
        """
        MIN_GAP = 1  # Ensure at least one data point between the two sliders

        if self.end_value - self.start_value < MIN_GAP:
            if self.dragging_start:
                self.start_value = self.end_value - MIN_GAP
            elif self.dragging_end:
                self.end_value = self.start_value + MIN_GAP


    def serialize(self):
        """
        Convert the slider's state to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the slider's state.
        """
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
        """
        Create a RangeSlider instance from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing slider data.

        Returns
        -------
        RangeSlider
            A new RangeSlider instance.
        """
        width = data.get("width", 700)  # Default to 700 if width is not present.
        range_slider = RangeSlider(data["x"], data["y"], width, data["min_value"], data["max_value"])
        range_slider.start_value = data.get("start_value", data["min_value"])  # Default to min_value if start_value is not present.
        range_slider.end_value = data.get("end_value", data["max_value"])    # Default to max_value if end_value is not present.
        return range_slider



if __name__ == "__main__":
    # Colors
    WHITE = (255, 255, 255)

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
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