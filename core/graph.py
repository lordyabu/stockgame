import pygame
import pandas as pd
from core.clock import Clock
from utils.observer_pattern import Observer
# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600


class Graph(Observer):
    """
    A class for plotting and displaying graphs on a Pygame screen.

    Attributes:
        is_live (bool): Flag indicating if the graph is live or static.
        size_multiplier (float): Multiplier to adjust the graph's display size.
        df (pd.DataFrame): The data for the graph, stored as a Pandas DataFrame.
        df_path (str): Path to the data file from which the DataFrame was loaded.
        x (int): The x-coordinate of the top-left corner of the graph.
        y (int): The y-coordinate of the top-left corner of the graph.
        width (int): Width of the graph.
        height (int): Height of the graph.
        rect (pygame.Rect): The rectangle object representing the graph's position and size.

    Methods:
        display(screen): Display the graph on the Pygame screen.
        update_position(dx, dy): Update the position of the graph by dx and dy.
        serialize(): Convert the graph object into a serializable dictionary.
    """
    current_x_offset = 0  # Class variable to track x-offset for new graphs
    spacing = 20  # Space between each graph
    MARGIN = 10  # Margin for all sides

    def __init__(self, is_live=False, data_file=None, size_multiplier=1.0, y_offset_percentage=0.6,
                 x=None, y=None, width=None, height=None):
        """
        Initialize a Graph instance.

        Args:
            is_live (bool): Flag indicating if the graph is live or static. Default is False.
            data_file (str, optional): Path to the CSV data file. Default is None.
            size_multiplier (float, optional): Multiplier to adjust the graph's display size. Default is 1.0.
            y_offset_percentage (float, optional): Y-offset percentage from the top of the screen. Default is 0.6.
            x (int, optional): The x-coordinate of the top-left corner. Default is None.
            y (int, optional): The y-coordinate of the top-left corner. Default is None.
            width (int, optional): The width of the graph. Default is None.
            height (int, optional): The height of the graph. Default is None.
        """
        self.is_live = is_live
        self.size_multiplier = size_multiplier
        try:
            self.df = pd.read_csv(data_file) if data_file else None
        except FileNotFoundError:
            print(f"Error: Data file {data_file} not found.")
            self.df = None

        self.df_path = data_file

        if x is None or y is None or width is None or height is None:
            # Define size only if not provided
            self.width = (WIDTH - 2 * Graph.MARGIN) * 0.5 * size_multiplier
            self.height = (HEIGHT - 2 * Graph.MARGIN) * 0.5 * size_multiplier

            # x and y position adjusted for margin and spacing
            self.x = Graph.current_x_offset + Graph.MARGIN
            self.y = HEIGHT * y_offset_percentage - self.height * 0.5

            # Increase the offset for next graphs by width + spacing
            Graph.current_x_offset += self.width + Graph.spacing
        else:
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)



        self.current_time_highlight = None  # New attribute to hold the current time from the slider.
        self.point_radius = 5  # Size of the point to display on the graph for the current time.

        self.highlight_index = None

    def set_highlight_index(self, index):
        """
        Set the index to be highlighted.

        Args:
            index (int): The index to be highlighted.
        """
        self.highlight_index = index

    def display(self, screen):
        # Draw the rectangle boundary of the graph
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

        # Plot data if df exists
        if self.df is not None:
            max_price = self.df['Price'].max()
            min_price = self.df['Price'].min()

            prices_normalized = [(price - min_price) / (max_price - min_price) for price in self.df['Price']]

            prev_x_pos = None
            prev_y_pos = None
            for idx, price in enumerate(prices_normalized):
                x_pos = self.x + (self.width / len(self.df) * idx)
                y_pos = self.y + self.height - (self.height * price)

                if prev_x_pos is not None:
                    pygame.draw.line(screen, (0, 0, 255), (int(prev_x_pos), int(prev_y_pos)), (int(x_pos), int(y_pos)),
                                     2)

                prev_x_pos = x_pos
                prev_y_pos = y_pos

            # Add the code to display a point for the highlighted index
            if self.highlight_index is not None and 0 <= self.highlight_index < len(self.df):
                x_pos = self.x + (self.width / len(self.df) * self.highlight_index)
                price = self.df['Price'].iloc[self.highlight_index]
                price_normalized = (price - min_price) / (max_price - min_price)
                y_pos = self.y + self.height - (self.height * price_normalized)

                pygame.draw.circle(screen, (255, 0, 0), (int(x_pos), int(y_pos)),
                                   self.point_radius)  # Drawing a red dot

        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)

    def update_position(self, dx, dy):
        """
        Update the position of the graph.

        Args:
            dx (int): The change in x-coordinate.
            dy (int): The change in y-coordinate.
        """
        self.x += dx
        self.y += dy

    def update(self, value):
        """Called when the slider's value changes."""
        # Update the highlight index based on the received value.
        if self.df is not None:
            self.highlight_index = int(value)
            # Ensure the value is within the dataframe's bounds.
            self.highlight_index = max(0, min(len(self.df) - 1, self.highlight_index))

    def serialize(self):
        """
        Convert the graph object into a serializable dictionary.

        Returns:
            dict: The dictionary representation of the graph.
        """
        return {
            'type': 'Graph',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'data_file': self.df_path,
            'size_multiplier': self.size_multiplier
        }


# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# ... [Your Graph class goes here] ...

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Graph Test')

    # Try with an absolute path to the CSV if the relative path doesn't work.
    test_graph = Graph(data_file='./data/PriceDay.csv')  # Replace with the correct path if needed

    test_graph.set_highlight_index(2)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        test_graph.display(screen)
        pygame.display.flip()

    pygame.quit()