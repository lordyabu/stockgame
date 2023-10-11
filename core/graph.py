import time
from utils.strategy_rules import Strategy
import pygame
import pandas as pd
from core.clock import Clock
from utils.observer_pattern import Observer, Observable
from utils.uiux import UIElement
# from analysis.slider import Slider
from utils.mini_button import TextButton
# from analysis.table import DataTable
import os
# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600


def darken_color(color, factor=0.7):
    """Returns a darker shade of the provided color."""
    return tuple([int(c * factor) for c in color])

class Graph(UIElement, Observer, Observable):
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
                 x=None, y=None, width=None, height=None, color=(0, 0, 255),
                 title='', original_title='', strategy_active=False, strategy_name='Strategy', prof_coloring=False, bar_chart=False, grid=True):
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
        Observable.__init__(self)
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

        # Extract the filename from the data_file path
        self.data_filename = os.path.basename(data_file) if data_file else None

        self.strategy_name = strategy_name  # or any default name for your strategy column
        self.strategy_active = False

        self.strategy_dir = data_file.split("/")[2]

        # Initialize the strategy
        self.strategy = Strategy()

        # Set the strategy_active attribute
        self.strategy_active = strategy_active

        self.display_range = (0, len(self.df) - 1) if self.df is not None else (0, 0)

        self.prof_coloring = prof_coloring




        self.colors = self.calculate_colors()

        self.bar_chart = bar_chart

        self.df['DateTime'] = pd.to_datetime(self.df['DateTime'], format='%m/%d/%Y %H:%M')



        # Assuming 'DateTime' column is of type datetime64
        self.df.set_index('DateTime', inplace=True)

        # Resample in 5-minute intervals and compute OHLC
        self.ohlc_data = self.df.resample('5T').agg({
            'Price': ['first', 'max', 'min', 'last']
        })

        self.ohlc_data.columns = ['Open', 'High', 'Low', 'Close']
        self.ohlc_data.dropna(inplace=True)  # drop any empty intervals

        self.label_color = (192, 192, 192)

        self.setup_grid(grid)


    def setup_grid(self, grid):
        self.grid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.grid = grid

        if self.grid:
            self._draw_grid_on_surface()
            self.create_toggle_buttons()


    def create_toggle_buttons(self):
        """Create interactive toggle buttons for the graph."""
        self.toggle_button_grid = self._create_button(self.x + 75, "Grid On", self.toggle_grid)
        self.toggle_button_chart = self._create_button(self.x + 150, "Candle", self.toggle_bar)
        self.toggle_button_strategy = self._create_button(self.x + 225, "Indicators On", self.toggle_strategy)
        self.toggle_button_color = self._create_button(self.x + 350, "RG Color", self.toggle_color)


    def _create_button(self, x_pos, label, action):
        """Helper function to create a button."""
        return TextButton(x_pos, self.y - 29, label, pygame.font.SysFont(None, 24), (255, 255, 255), action, alpha=100)

    def _draw_grid_on_surface(self):
        """Draws the transparent grid onto self.grid_surface."""
        alpha_value = 64  # Adjust this value for desired transparency; lower value means more transparent

        interval_step = max(len(self.df) // 7, 1)  # Ensure it's at least 1

        # Vertical lines
        for idx in range(0, len(self.df), interval_step):
            x_pos = (self.width / (len(self.df) - 1) * idx)
            pygame.draw.line(self.grid_surface, self.label_color + (alpha_value,), (int(x_pos), 0),
                             (int(x_pos), self.height), 1)

        # Horizontal lines
        y_spacing = self.height / 4
        for i in range(5):  # Five lines in total
            y_pos = i * y_spacing
            pygame.draw.line(self.grid_surface, self.label_color + (alpha_value,), (0, int(y_pos)),
                             (self.width, int(y_pos)), 1)

    def toggle_grid(self):
        self.grid = not self.grid
        if self.grid:
            self.toggle_button_grid.text = "Grid On"
        else:
            self.toggle_button_grid.text = "Grid Off"
        self.toggle_button_grid.image = self.toggle_button_grid.font.render(self.toggle_button_grid.text, True,
                                                                  self.toggle_button_grid.color)

    def toggle_bar(self):
        self.bar_chart = not self.bar_chart
        if self.bar_chart:
            self.toggle_button_chart.text = "Candle"
        else:
            self.toggle_button_chart.text = "Line"
        self.toggle_button_chart.image = self.toggle_button_chart.font.render(self.toggle_button_chart.text, True,
                                                                  self.toggle_button_chart.color)

    def toggle_strategy(self):
        self.strategy_active = not self.strategy_active
        if self.strategy_active:
            self.toggle_button_strategy.text = "Indicator On"
        else:
            self.toggle_button_strategy.text = "Indicator Off"
        self.toggle_button_strategy.image = self.toggle_button_strategy.font.render(self.toggle_button_strategy.text, True,
                                                                  self.toggle_button_strategy.color)

    def toggle_color(self):
        self.prof_coloring = not self.prof_coloring
        if self.prof_coloring:
            self.toggle_button_color.text = "RG Color"
        else:
            self.toggle_button_color.text = "B Color"
        self.toggle_button_color.image = self.toggle_button_color.font.render(self.toggle_button_color.text, True,
                                                                  self.toggle_button_color.color)

    def calculate_colors(self):
        """Calculate colors for data points based on the previous average."""
        if self.df is None or 'Price' not in self.df:
            return []

        prices = self.df['Price'].tolist()
        colors = []

        # Compute the lookback for coloring
        cum_sum = 0
        for i, price in enumerate(prices):
            cum_avg = cum_sum / (i+1) if i != 0 else price
            color = (0, 255, 0) if price >= cum_avg else (255, 0, 0)
            colors.append(color)
            cum_sum += price
        return colors

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
        def render_transparent_text(surface, text, font, color, position, alpha):
            text_surf = font.render(text, True, color).convert_alpha()
            text_surf.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            surface.blit(text_surf, position)



        alpha_value = 128
        # print(self.highlight_index)

        # print(self.display_range)
        # print(id(self), 'DISPLAYING')
        # Draw the rectangle boundary of the graph
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        font = pygame.font.SysFont(None, 24)

        # Plot data if df exists
        if self.df is not None:
            start_idx, end_idx = self.display_range
            # print(start_idx, end_idx)
            displayed_data = self.df.iloc[start_idx:end_idx + 1]

            max_val = displayed_data[self.column].max()
            min_val = displayed_data[self.column].min()
            denominator = max_val - min_val
            if max_val == min_val:
                values_normalized = [0.5 for _ in displayed_data[self.column]]  # Middle of the graph
            else:
                values_normalized = [(value - min_val) / (max_val - min_val) for value in displayed_data[self.column]]

            # Y-axis value rendering
            if max_val == min_val:
                mid_val = max_val
            else:
                mid_val = (max_val + min_val) / 2

            if self.bar_chart:
                ohlc_data = displayed_data.resample('5T').agg({self.column: ['first', 'max', 'min', 'last']})
                ohlc_data.columns = ['Open', 'High', 'Low', 'Close']
                ohlc_data.dropna(inplace=True)

                bar_width = max(1, self.width / len(ohlc_data) - 2)
                width_ratio = self.width / (len(ohlc_data) - 1)

                transparency = 128  # You can adjust this value. 0 is fully transparent, 255 is opaque.

                for idx, (_, row) in enumerate(ohlc_data.iterrows()):
                    x_pos = self.x + width_ratio * idx
                    y_values = [
                        self.y + self.height - (self.height * (row[key] - min_val) / denominator)
                        for key in ['Open', 'High', 'Low', 'Close']
                    ]

                    current_color = (0, 255, 0) if row['Close'] >= row['Open'] else (
                        255, 0, 0) if self.prof_coloring else self.color

                    # Draw vertical line from Low to High
                    pygame.draw.line(screen, current_color, (int(x_pos), int(y_values[2])),
                                     (int(x_pos), int(y_values[1])), 1)

                    # Drawing a transparent rectangle for the Open and Close prices
                    temp_surface = pygame.Surface((bar_width, abs(y_values[0] - y_values[3])))
                    temp_surface.fill(current_color)
                    temp_surface.set_alpha(transparency)

                    # Adjust positioning based on the Open and Close values
                    rect_y = min(y_values[0], y_values[3])
                    screen.blit(temp_surface, (int(x_pos - bar_width / 2), int(rect_y)))

            # Define y positions for text
            y_pos_max = self.y + 5  # 5 pixels from the top edge of the graph
            y_pos_mid = self.y + self.height / 2 - 12  # centered in the middle, adjusted for text height
            y_pos_min = self.y + self.height - 25  # 25 pixels from the bottom edge to account for text height

            # Render the text
            text_max = font.render(f"{max_val:.2f}", True, self.label_color)
            text_mid = font.render(f"{mid_val:.2f}", True, self.label_color)
            text_min = font.render(f"{min_val:.2f}", True, self.label_color)

            padding = 10  # distance from the right edge of the graph
            x_pos_text = self.x + self.width + padding

            # Blit the text
            screen.blit(text_max, (x_pos_text, y_pos_max))
            screen.blit(text_mid, (x_pos_text, y_pos_mid))
            screen.blit(text_min, (x_pos_text, y_pos_min))

            # Extract time values from the DateTime column
            time_values = displayed_data.index.strftime('%H:%M').tolist()

            # Determine the number of time labels to display based on size_multiplier
            num_intervals = int(self.size_multiplier * 7)  # Multiplying by 7 as a baseline number of intervals
            num_intervals = max(3, min(num_intervals, 7))  # Ensure between 3 and 7 labels are shown

            interval_step = max(len(time_values) // num_intervals, 1)  # Ensure it's at least 1

            # Displaying time values on the X-axis at the determined intervals
            for idx in range(0, len(time_values), interval_step):
                x_pos = self.x + (self.width / (len(displayed_data) - 1) * idx)
                time_text = font.render(time_values[idx], True, self.label_color)
                render_transparent_text(screen, time_values[idx], font, self.label_color,
                                        (x_pos - time_text.get_width() / 2, self.y + self.height + 5), alpha_value)

            prev_x_pos = None
            prev_y_pos = None
            if not self.bar_chart:
                for idx, value in enumerate(values_normalized):
                    relative_idx = idx

                    x_pos = self.x + (self.width / (len(displayed_data) - 1) * relative_idx) if len(
                        displayed_data) > 1 else self.x

                    y_pos = self.y + self.height - (self.height * value)
                    current_color = self.color  # default color

                    # If profit_coloring is active, decide the color based on value change
                    if self.prof_coloring:
                        lookback_period = 5  # or whatever value you deem appropriate
                        if idx >= lookback_period:
                            if displayed_data[self.column].iloc[idx] > displayed_data[self.column].iloc[
                                idx - lookback_period]:
                                current_color = (0, 255, 0)  # green for up
                            else:
                                current_color = (255, 0, 0)  # red for down
                        else:
                            if idx > 0:
                                if displayed_data[self.column].iloc[idx] > displayed_data[self.column].iloc[
                                    idx - 1]:
                                    current_color = (0, 255, 0)  # green for up
                                else:
                                    current_color = (255, 0, 0)  # red for down
                            else:
                                current_color = (0, 255, 0)
                    else:
                        current_color = self.color

                    if prev_x_pos is not None:
                        pygame.draw.line(screen, current_color, (int(prev_x_pos), int(prev_y_pos)),
                                         (int(x_pos), int(y_pos)), 2)

                    prev_x_pos = x_pos
                    prev_y_pos = y_pos

            # Display a point for the highlighted index
            if self.highlight_index is not None and 0 <= self.highlight_index < len(self.df):
                relative_idx = self.highlight_index - start_idx
                x_pos = self.x + (self.width / (len(displayed_data) - 1) * relative_idx) if len(
                    displayed_data) > 1 else self.x

                value = self.df[self.column].iloc[self.highlight_index]
                value_normalized = (value - min_val) / (max_val - min_val)
                y_pos = self.y + self.height - (self.height * value_normalized)
                pygame.draw.circle(screen, (0, 0, 0), (int(x_pos), int(y_pos)), self.point_radius)

        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)

        # Display the original title for the graph
        title_surf = font.render(self.original_title, True, self.color)
        screen.blit(title_surf, (self.x, self.y - 30))

        strategy = Strategy()  # Initialize your strategy instance

        if self.strategy and self.strategy_active and self.strategy_name in self.df.columns:
            for idx, (value, signal) in enumerate(zip(values_normalized, displayed_data[self.strategy_name])):
                x_pos = self.x + (self.width / (len(displayed_data) - 1) * idx) if len(displayed_data) > 1 else self.x
                y_pos = self.y + self.height - (self.height * value)

                color, label = strategy.get_signal_display_info(signal)

                if color is not None:
                    pygame.draw.circle(screen, color, (int(x_pos), int(y_pos)), self.point_radius)

                if label:
                    label_surface = pygame.font.SysFont(None, 24).render(label, True, color)
                    label_width = label_surface.get_width()
                    label_height = label_surface.get_height()

                    # Check space above and below the point
                    space_above = y_pos - self.y
                    space_below = (self.y + self.height) - y_pos

                    # Prefer vertical positioning with added logic for up vs down
                    if space_above > label_height and (
                            self.height / 2) > y_pos:  # if point is in the upper half of the graph
                        text_pos = (int(x_pos - label_width / 2), int(y_pos) - 20 - label_height)
                    elif space_below > label_height and (
                            self.height / 2) <= y_pos:  # if point is in the lower half of the graph
                        text_pos = (int(x_pos - label_width / 2), int(y_pos) + 20)
                    else:  # Adjust based on space available
                        if space_above > space_below:
                            text_pos = (int(x_pos - label_width / 2), int(y_pos) - 20 - label_height)
                        else:
                            text_pos = (int(x_pos - label_width / 2), int(y_pos) + 20)

                    screen.blit(label_surface, text_pos)

        if self.grid:
            screen.blit(self.grid_surface, (self.x, self.y))


    def compute_moving_average(self, window_size=3):
        if self.df is not None:
            return self.df[self.column].rolling(window=window_size).mean()
        return None

    def set_data_file(self, day):
        if not self.data_filename:  # If filename not set, don't continue
            return

        try:
            # print("here")
            new_path = f"./data/{self.strategy_dir}/Day{day}.csv"
            # print(new_path)
            # print(new_path)
            new_df = pd.read_csv(new_path)
            self.df_path = new_path
            if not new_df.empty:
                self.df_path = new_path
                self.df = new_df
                # print(f"Loaded data for Day{day}. First few rows:")
                # print(self.df.head())  # Printing the first few rows of the new data
                self.df['DateTime'] = pd.to_datetime(self.df['DateTime'], format='%m/%d/%Y %H:%M')
                self.df.set_index('DateTime', inplace=True)
                self.ohlc_data = self.df.resample('5T').agg({
                    'Price': ['first', 'max', 'min', 'last']
                })

                self.ohlc_data.columns = ['Open', 'High', 'Low', 'Close']
                self.ohlc_data.dropna(inplace=True)  # drop any empty intervals
            else:
                print(f"Warning: Data file {new_path} is empty.")
        except FileNotFoundError:
            print(f"Error: Data file {new_path} not found.")

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
        # print('Scoob')
        self.toggle_button_grid.update_position(dx, dy)
        self.toggle_button_chart.update_position(dx, dy)
        self.toggle_button_color.update_position(dx, dy)
        self.toggle_button_strategy.update_position(dx, dy)


    def update(self, value):
        """Called when the slider's value changes."""
        if isinstance(value, tuple):  # Range slider updates
            start_idx, end_idx = value
            self.update_range(start_idx, end_idx)

            # Notify observers (which includes the single point slider) about the new range.
            # print("ADSD")
            self.notify_observers(value)
        else:
            # Single point slider updates
            if self.df is not None:
                self.highlight_index = int(value)
                # Ensure the value is within the dataframe's bounds.
                self.highlight_index = max(0, min(len(self.df) - 1, self.highlight_index))

    def update_range(self, start_idx, end_idx):
        # print("USING THIS HERE")
        """Called when the range slider's value changes."""
        self.set_display_range(start_idx, end_idx)

    def set_display_range(self, start_idx, end_idx):
        """Update the graph's displayed range."""
        if self.df is not None:
            max_idx = len(self.df) - 1
            start_idx = max(0, min(max_idx, start_idx))
            end_idx = max(0, min(max_idx, end_idx))
            self.display_range = (start_idx, end_idx)

    def update_day(self, day_value):
        # Handle the change in day and update the graph's data accordingly.
        self.set_data_file(day_value)

    def serialize(self):
        """
        Convert the graph object into a serializable dictionary.
        Returns:
            dict: The dictionary representation of the graph.
        """
        data = super().serialize()

        # print('SAVING', self.df_path, self.data_filename)
        data.update({
            'data_file': self.df_path,
            'size_multiplier': self.size_multiplier,
            'column': self.column,
            'width': self.width,
            'height': self.height,
            'color': self.color,
            'original_title': self.original_title,
            'data_filename': self.data_filename,
            'strategy_name': self.strategy_name,
            'strategy_active': self.strategy_active,
            'is_grid': self.grid,
            'is_bar': self.bar_chart,
            'is_prof': self.prof_coloring
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

        # Construct the default data_file path with 'Day1' and the data_filename.
        default_day = "Day1"
        data_filename = data.get('data_file', '')
        constructed_data_file = data_filename


        return Graph(
            x=data['x'],
            y=data['y'],
            width=data.get('width', None),
            height=data.get('height', None),
            data_file=constructed_data_file,
            column=data.get('column', 'Price'),
            size_multiplier=data['size_multiplier'],
            color=data['color'],
            original_title=data['original_title'],
            strategy_active=data['strategy_active'],
            strategy_name=data['strategy_name'],
            grid=data['is_grid'],
            prof_coloring=data['is_prof'],
            bar_chart=data['is_bar']
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
    test_graph1 = Graph(data_file='./data/strategy_zero/Day1.csv', column='Price1', color=(255, 0, 0), title="Graph 1", strategy_active=True)
    test_graph2 = Graph(data_file='./data/strategy_zero/Day1.csv', column='Price2', color=(0, 255, 0), title="Graph 2", strategy_active=False)

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
