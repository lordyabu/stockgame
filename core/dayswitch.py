from utils.uiux import UIElement
from utils.observering import Observable
import pygame
import os
from core.graph import Graph
import pandas as pd

class DaySwitch(UIElement, Observable):
    """
    DaySwitch provides a UI element to toggle between different days and displays relevant data.

    Attributes
    ----------
    show_date : bool
        Indicates whether the date should be displayed or not.
    max_days : int
        The maximum number of days to be shown.
    current_day : int
        The current day being displayed.
    font : pygame.font.Font
        The font to be used for displaying text.
    arrow_size : int
        The size of the arrows used to toggle days.
    padding : int
        Padding value around the element.
    graphs : list[Graph]
        List of Graph objects associated with this DaySwitch.
    left_arrow_rect : pygame.Rect
        Clickable area of the left arrow.
    right_arrow_rect : pygame.Rect
        Clickable area of the right arrow.
    rect : pygame.Rect
        Bounding rectangle for the entire DaySwitch element.
    strategy_dir : str
        Directory name where strategy data is stored.

    Methods
    -------
    display(screen)
        Renders the DaySwitch UI onto the provided screen.
    clear_graphs()
        Clears the list of associated graphs.
    add_graphs(graphs)
        Extends the list of associated graphs.
    check_click(pos)
        Handles click events on the DaySwitch UI.
    _move_day(direction)
        Changes the current day in the given direction.
    serialize()
        Serializes the DaySwitch instance into a dictionary.
    deserialize(data, graphs=[])
        Deserializes data into a DaySwitch instance.
    update_position(dx, dy)
        Updates the position of DaySwitch and its sub-elements.
    resize(new_width, new_height)
        Resizes the DaySwitch (currently not implemented).
    """
    def __init__(self, x, y, graphs=[], max_days=99, strategy_dir='strategy_zero', show_date=True):
        """
        Initializes a DaySwitch instance.

        Parameters
        ----------
        x : int
            X-coordinate of the top-left corner of the DaySwitch.
        y : int
            Y-coordinate of the top-left corner of the DaySwitch.
        graphs : list[Graph], optional
            List of associated Graph objects.
        max_days : int, optional
            Maximum number of days to be displayed. Default is 99.
        strategy_dir : str, optional
            Name of the directory where strategy data is stored. Default is 'strategy_zero'.
        show_date : bool, optional
            Whether the date should be displayed or not. Default is True.
        """
        super().__init__(x, y)
        self.show_date = show_date
        self.max_days = max_days
        self.current_day = 1
        self.font = pygame.font.SysFont('arial', 16)  # Increased the font size

        self.arrow_size = 20  # Increased from 20 to 80
        self.padding = 40  # Increased from 10 to 40

        self.graphs = graphs

        # Define clickable areas based on new dimensions
        self.left_arrow_rect = pygame.Rect(x, y + self.font.get_height(), self.arrow_size, self.arrow_size)
        self.right_arrow_rect = pygame.Rect(x + 2 * self.padding + self.arrow_size, y + self.font.get_height(), self.arrow_size, self.arrow_size)

        # Define bounding rect for the entire DaySwitch
        total_width = self.arrow_size + 2 * self.padding + self.arrow_size + self.font.size(f"Day {self.max_days}")[0]
        total_height = self.arrow_size + self.font.get_height()
        self.rect = pygame.Rect(self.x, self.y, total_width, total_height)

        self.strategy_dir = strategy_dir
        self.show_date = show_date

    def display(self, screen):
        """
        Renders the DaySwitch UI onto the provided screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the DaySwitch UI is rendered.
        """
        # Create a separate surface for arrows
        arrow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Draw left arrow (shaped like a mouse pointer facing left) using transparent color
        pygame.draw.polygon(arrow_surface, (0, 0, 0, 128),  # RGBA
                            [(self.left_arrow_rect.x + self.arrow_size - self.x, self.left_arrow_rect.y - self.y),
                             (self.left_arrow_rect.x - self.x, self.left_arrow_rect.y + self.arrow_size // 2 - self.y),
                             (self.left_arrow_rect.x + self.arrow_size - self.x,
                              self.left_arrow_rect.y + self.arrow_size - self.y)])

        # Draw right arrow (shaped like a mouse pointer facing right) using transparent color
        pygame.draw.polygon(arrow_surface, (0, 0, 0, 128),  # RGBA
                            [(self.right_arrow_rect.x - self.x, self.right_arrow_rect.y - self.y),
                             (self.right_arrow_rect.x + self.arrow_size - self.x,
                              self.right_arrow_rect.y + self.arrow_size // 2 - self.y),
                             (self.right_arrow_rect.x - self.x, self.right_arrow_rect.y + self.arrow_size - self.y)])

        # Blit arrow surface to main screen
        screen.blit(arrow_surface, (self.x, self.y))

        # Render the text directly onto the main screen (opaque)
        if hasattr(self, 'show_date') and self.show_date and self.graphs:
            df = pd.read_csv(self.graphs[0].df_path)
            day_str = str(df.iloc[0]["DateTime"].split(' ')[0])
        else:
            day_str = f"Day {self.current_day}"

        day_text = self.font.render(day_str, True, (0, 0, 0))  # RGB for opaque black text

        # Calculate the midpoint between the arrows and blit the text
        arrow_midpoint = self.left_arrow_rect.right + (self.right_arrow_rect.left - self.left_arrow_rect.right) / 2
        text_x = arrow_midpoint - day_text.get_width() // 2
        text_y = self.y + self.arrow_size + self.padding  # Below the arrows
        screen.blit(day_text, (text_x, text_y))

    def clear_graphs(self):
        """
        Clears the list of associated graphs.
        """
        self.graphs = []

    def add_graphs(self, graphs):
        """
        Adds multiple graphs to the list of associated graphs.

        Parameters
        ----------
        graphs : list[Graph]
            A list of Graph objects to be added.
        """
        self.graphs.extend(graphs)


    def check_click(self, pos):
        """
        Determines the action based on the position of a click.

        Parameters
        ----------
        pos : tuple[int, int]
            A tuple containing x and y coordinates of the click.
        """
        if self.left_arrow_rect.collidepoint(pos):
            self._move_day(-1)
        elif self.right_arrow_rect.collidepoint(pos):
            self._move_day(1)
        else:
            pass

    def _move_day(self, direction):
        """
        Changes the current day based on the given direction.

        If the data for the new day doesn't exist, it continues moving in the same direction until a valid day is found.

        Parameters
        ----------
        direction : int
            An integer indicating the direction to move. Negative for moving back and positive for moving forward.
        """
        self.current_day += direction
        if self.current_day > self.max_days:
            self.current_day = 1
        elif self.current_day < 1:
            self.current_day = self.max_days

        # Check if directory exists, otherwise wrap around
        while not os.path.exists(f"./data/{self.strategy_dir}/Day{self.current_day}.csv"):
            self.current_day += direction
            if self.current_day > self.max_days:
                self.current_day = 1
            elif self.current_day < 1:
                self.current_day = self.max_days

        for graph in self.graphs:
            graph.set_data_file(self.current_day)

    def serialize(self):
        """
        Serializes the DaySwitch instance into a dictionary for saving state.

        Returns
        -------
        dict
            Dictionary containing the serialized DaySwitch data.
        """
        data = {
            'type': "DaySwitch",
            'x': self.x,
            'y': self.y,
            'current_day': self.current_day,
            'max_days': self.max_days,
            'strategy_dir': self.strategy_dir,
        }
        return data

    @staticmethod
    def deserialize(data, graphs=[]):
        """
        Creates a DaySwitch instance from serialized data.

        Parameters
        ----------
        data : dict
            Dictionary containing serialized DaySwitch data.
        graphs : list[Graph], optional
            A list of associated Graph objects. Default is an empty list.

        Returns
        -------
        DaySwitch
            A DaySwitch instance constructed from the serialized data.
        """
        x = data['x']
        y = data['y']
        current_day = data.get('current_day', 1)
        max_days = data.get('max_days', 99)

        strategy_dir = data['strategy_dir']

        day_switch = DaySwitch(x, y, graphs=graphs, max_days=max_days, strategy_dir=strategy_dir)
        day_switch.current_day = current_day

        # Ensure that the clickable regions are updated based on the loaded position:
        day_switch.left_arrow_rect = pygame.Rect(x, y, day_switch.arrow_size, day_switch.arrow_size)
        day_switch.right_arrow_rect = pygame.Rect(x + 2 * day_switch.padding + day_switch.arrow_size, y,
                                                  day_switch.arrow_size, day_switch.arrow_size)

        return day_switch

    def update_position(self, dx, dy):
        """
        Updates the position of the DaySwitch and its sub-elements.

        Parameters
        ----------
        dx : int
            Change in x-coordinate.
        dy : int
            Change in y-coordinate.
        """
        self.x += dx
        self.y += dy

        self.rect.move_ip(dx, dy)
        self.left_arrow_rect.move_ip(dx, dy)
        self.right_arrow_rect.move_ip(dx, dy)

    def resize(self, new_width, new_height):
        """
        Resizes the DaySwitch. Implementation currently not provided.

        Parameters
        ----------
        new_width : int
            The new width for the DaySwitch.
        new_height : int
            The new height for the DaySwitch.
        """
        pass  # Implement if needed


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
    test_graph1 = Graph(data_file='./data/Day1/PriceDay1.csv', color=(255, 0, 0), title="Graph 1",
                        original_title="Graph 1")
    test_graph2 = Graph(data_file='./data/Day1/PriceDay3.csv', color=(0, 255, 0), title="Graph 2",
                        original_title="Graph 2")

    graphs = [test_graph1, test_graph2]

    # Initialize DaySwitch and provide it with Graph objects to update
    day_switch = DaySwitch(700, 30, graphs=graphs)

    # Rest of your main loop remains largely unchanged...
    dragging = False
    dragged_graph = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handling DaySwitch events
            if event.type == pygame.MOUSEBUTTONDOWN:
                day_switch.check_click(event.pos)

            # ... [rest of your event handling for sliders and graphs]

        screen.fill(WHITE)
        for current_graph in graphs:
            current_graph.display(screen, graphs)

        # Display the DaySwitch
        day_switch.display(screen)

        # ... [rest of your rendering code for sliders and tables]

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
