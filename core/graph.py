import pygame
import pandas as pd
from core.clock import Clock
from utils.observer_pattern import Observer
from utils.uiux import UIElement
# from analysis.slider import Slider
# from analysis.table import DataTable
# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600


def darken_color(color, factor=0.7):
    """Returns a darker shade of the provided color."""
    return tuple([int(c * factor) for c in color])

class Graph(UIElement, Observer):
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

    def __init__(self, is_live=False, data_file=None, column='Price',
                 size_multiplier=1.0, y_offset_percentage=0.6,
                 x=None, y=None, width=None, height=None, color=(0, 0, 255), title='', original_title=''):
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
        UIElement.__init__(self, x, y)
        Observer.__init__(self)
        self.is_live = is_live
        self.size_multiplier = size_multiplier
        try:
            self.df = pd.read_csv(data_file) if data_file else None
        except FileNotFoundError:
            print(f"Error: Data file {data_file} not found.")
            self.df = None

        self.df_path = data_file
        self.column = column

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

        self.color = color
        self.title_color = darken_color(color)
        self.title = [title, self.title_color]

        self.original_title = original_title

    def set_highlight_index(self, index):
        """
        Set the index to be highlighted.

        Args:
            index (int): The index to be highlighted.
        """
        self.highlight_index = index

    def get_overlapping_graphs(self, other_graphs):
        """Get the overlapping graphs."""
        overlapping_graphs = [graph for graph in other_graphs if self.rect.colliderect(graph.rect)]
        return overlapping_graphs

    def display(self, screen, all_graphs=[]):
        # Draw the rectangle boundary of the graph
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        font = pygame.font.SysFont(None, 24)

        # Plot data if df exists
        if self.df is not None:
            max_val = self.df[self.column].max()
            min_val = self.df[self.column].min()
            values_normalized = [(value - min_val) / (max_val - min_val) for value in self.df[self.column]]
            prev_x_pos = None
            prev_y_pos = None
            for idx, value in enumerate(values_normalized):
                x_pos = self.x + (self.width / len(self.df) * idx)
                y_pos = self.y + self.height - (self.height * value)
                if prev_x_pos is not None:
                    pygame.draw.line(screen, self.color, (int(prev_x_pos), int(prev_y_pos)), (int(x_pos), int(y_pos)),
                                     2)
                prev_x_pos = x_pos
                prev_y_pos = y_pos

            # Display a point for the highlighted index
            if self.highlight_index is not None and 0 <= self.highlight_index < len(self.df):
                x_pos = self.x + (self.width / len(self.df) * self.highlight_index)
                value = self.df[self.column].iloc[self.highlight_index]
                value_normalized = (value - min_val) / (max_val - min_val)
                y_pos = self.y + self.height - (self.height * value_normalized)
                pygame.draw.circle(screen, (255, 0, 0), (int(x_pos), int(y_pos)),
                                   self.point_radius)  # Drawing a red dot

        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)

        # Display the original title for the graph
        title_surf = font.render(self.original_title, True, self.color)
        screen.blit(title_surf, (self.x, self.y - 30))

    def update_position(self, dx, dy, other_graphs=[]):
        """
        Update the position of the graph.

        Args:
            dx (int): The change in x-coordinate.
            dy (int): The change in y-coordinate.
        """
        self.x += dx
        self.y += dy
        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)

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
        data = super().serialize()

        data.update({
            'data_file': self.df_path,
            'size_multiplier': self.size_multiplier,
            'column': self.column,
            'width': self.width,
            'height': self.height,
            'color': self.color,
            'original_title': self.original_title
        })
        return data

    @staticmethod
    def deserialize(data):
        """
        Create a Graph instance from serialized data.
        Args:
            data (dict): The dictionary representation of the graph.
        Returns:
            Graph: An instance of the Graph class.
        """

        return Graph(
            x=data['x'],
            y=data['y'],
            width=data.get('width', None),
            height=data.get('height', None),
            data_file=data['data_file'],
            column=data.get('column', 'Price'),
            size_multiplier=data['size_multiplier'],
            color=data['color'],
            original_title=data['original_title']
        )



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
    test_graph1 = Graph(data_file='./data/PriceDay1.csv', color=(255, 0, 0), title="Graph 1")
    test_graph2 = Graph(data_file='./data/PriceDay2.csv', color=(0, 255, 0), title="Graph 2")

    graphs = [test_graph1, test_graph2]

    # Slider instance
    test_slider = Slider(x=50, y=500, width=700, min_value=0,
                         max_value=max(len(test_graph1.df), len(test_graph2.df)) - 1)
    test_slider.add_observer(test_graph1)
    test_slider.add_observer(test_graph2)

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
            test_slider.handle_events(event)

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
        data_table.display(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
