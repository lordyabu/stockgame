import time
from utils.strategy_rules import Strategy
import pygame
import pandas as pd
from core.clock import Clock
from utils.observering import Observer, Observable
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

    Constants:
        WHITE (tuple): RGB color tuple for white.
        MARGIN (int): Margin size for the graph.
        spacing (int): Spacing between graphs.
        current_x_offset (int): Current x-offset for arranging multiple graphs.

    Methods:
        __init__(self, is_live=False, data_file=None, column='Price',
                 size_multiplier=1.0, y_offset_percentage=0.6,
                 x=None, y=None, width=None, height=None, color=(0, 0, 255),
                 title='', original_title='', strategy_active=False, strategy_name='Strategy', prof_coloring=False, bar_chart=0, grid=True, font=None)
        setup_grid(self)
        create_toggle_buttons(self)
        _create_button(self, text, position, width, height, callback)
        _draw_grid_on_surface(self, surface, line_color, line_spacing)
        toggle_grid(self)
        toggle_bar(self)
        toggle_strategy(self)
        toggle_color(self)
        calculate_colors(self)
        set_highlight_index(self, index)
        get_overlapping_graphs(self, all_graphs)
        display(self, screen, all_graphs=[])
        render_transparent_text(self, surface, text, font, color, position, alpha)
        compute_moving_average(self, window_size=3)
        set_data_file(self, day)
        update_position(self, dx, dy, other_graphs=[])
        update(self, value)
        update_range(self, start_idx, end_idx)
        set_display_range(self, start_idx, end_idx)
        update_day(self, day_value)
        serialize(self)
        deserialize(self, data)
    """


    current_x_offset = 0  # Class variable to track x-offset for new graphs
    spacing = 20  # Space between each graph
    MARGIN = 10  # Margin for all sides

    def __init__(self, is_live=False, data_file=None, column='Price',
                 size_multiplier=1.0, y_offset_percentage=0.6,
                 x=None, y=None, width=None, height=None, color=(0, 0, 255),
                 title='', original_title='', strategy_active=False, strategy_name='Strategy', prof_coloring=False, bar_chart=0, grid=True, font=None):
        """
        Initialize a Graph instance.

        Args:
            is_live (bool, optional): Flag indicating if the graph is live or static. Default is False.
            data_file (str, optional): Path to the CSV data file. Default is None.
            size_multiplier (float, optional): Multiplier to adjust the graph's display size. Default is 1.0.
            y_offset_percentage (float, optional): Y-offset percentage from the top of the screen. Default is 0.6.
            x (int, optional): The x-coordinate of the top-left corner. Default is None.
            y (int, optional): The y-coordinate of the top-left corner. Default is None.
            width (int, optional): The width of the graph. Default is None.
            height (int, optional): The height of the graph. Default is None.
            color (tuple, optional): The RGB color tuple for the graph. Default is (0, 0, 255).
            title (str, optional): The title of the graph. Default is an empty string.
            original_title (str, optional): The original title of the graph. Default is an empty string.
            strategy_active (bool, optional): Flag indicating if a strategy is active. Default is False.
            strategy_name (str, optional): The name of the strategy. Default is 'Strategy'.
            prof_coloring (bool, optional): Flag indicating if color-coding by profit is enabled. Default is False.
            bar_chart (int, optional): Flag indicating the type of chart (0 for line, 1 for candlestick, 2 for basic). Default is 0.
            grid (bool, optional): Flag indicating if the grid is enabled. Default is True.
            font (pygame.font.Font, optional): The font for text rendering. Default is None.
        """
        # Initialize the Graph instance.
        UIElement.__init__(self, x, y)  # Initialize UIElement base class.
        Observer.__init__(self)  # Initialize Observer base class.
        Observable.__init__(self)  # Initialize Observable base class.

        # Graph attributes
        self.is_live = is_live  # Flag indicating if the graph is live or static.
        self.size_multiplier = size_multiplier  # Multiplier to adjust the graph's display size.

        try:
            self.df = pd.read_csv(data_file) if data_file else None  # Read data from CSV file if provided.
        except FileNotFoundError:
            print(f"Error: Data file {data_file} not found.")
            self.df = None

        self.df_path = data_file  # Store the data file path.
        self.column = column  # Column of data to display on the graph.

        # Initialize graph dimensions and position
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

        # Create a bounding rectangle for the graph.
        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)

        # Graph visual attributes
        self.current_time_highlight = None  # Attribute to hold the current time from the slider.
        self.point_radius = 5  # Size of the point to display on the graph for the current time.
        self.highlight_index = None  # Index of the highlighted point on the graph.
        self.color = color  # Graph color.
        self.title_color = darken_color(color)  # Darkened title color.
        self.title = [title, self.title_color]  # Graph title and its color.
        self.original_title = title  # Original title of the graph.
        self.data_filename = os.path.basename(data_file) if data_file else None  # Extract filename from data file path.
        self.strategy_name = strategy_name  # Default name for the strategy column.
        self.strategy_active = False  # Flag indicating if the strategy is active.
        self.strategy_dir = data_file.split("/")[2]  # Extract directory from data file path.

        # Initialize the strategy
        self.strategy = Strategy()

        # Set the strategy_active attribute
        self.strategy_active = strategy_active

        # Define the display range based on the loaded data
        self.display_range = (0, len(self.df) - 1) if self.df is not None else (0, 0)

        self.prof_coloring = prof_coloring  # Flag for profit-based coloring of the graph.

        # Calculate colors for the graph
        self.colors = self.calculate_colors()

        self.bar_chart = bar_chart  # Type of chart to display (0: Candlestick, 1: OHLC, 2: Line).

        self.df['DateTime'] = pd.to_datetime(self.df['DateTime'],
                                             format='%m/%d/%Y %H:%M')  # Convert 'DateTime' to datetime.

        # Assuming 'DateTime' column is of type datetime64, set it as the index.
        self.df.set_index('DateTime', inplace=True)

        # Resample in 5-minute intervals and compute OHLC data
        self.ohlc_data = self.df.resample('5T').agg({
            'Price': ['first', 'max', 'min', 'last']
        })

        self.ohlc_data.columns = ['Open', 'High', 'Low', 'Close']
        self.ohlc_data.dropna(inplace=True)  # Drop any empty intervals.

        self.label_color = (192, 192, 192)  # Label color for the graph.

        # Setup grid
        self.setup_grid(grid)

        self.font = font  # Font for rendering text on the graph.

    def setup_grid(self, grid):
        """
        Set up the grid for the graph.

        Parameters:
        - grid (bool): Flag indicating whether to display the grid.

        Returns:
        - None
        """
        # Create a surface for drawing the grid with transparency.
        self.grid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Set the grid attribute based on the provided value.
        self.grid = grid

        if self.grid:
            # If grid is enabled, draw the grid on the surface.
            self._draw_grid_on_surface()

        # Create toggle buttons for grid-related settings.
        self.create_toggle_buttons()

    def create_toggle_buttons(self):
        """
        Create interactive toggle buttons for the graph.

        Returns:
            None
        """
        self.toggle_button_grid = self._create_button(self.x + 75, "Grid On", self.toggle_grid)
        self.toggle_button_chart = self._create_button(self.x + 150, "Candle", self.toggle_bar)
        self.toggle_button_strategy = self._create_button(self.x + 225, "Indicators Off", self.toggle_strategy)
        self.toggle_button_color = self._create_button(self.x + 350, "RG Color", self.toggle_color)


    def _create_button(self, x_pos, label, action):
        """
        Helper function to create a button.

        Parameters:
            x_pos (int): The x-coordinate of the button's top-left corner.
            label (str): The text label for the button.
            action (function): The function to be executed when the button is clicked.

        Returns:
            UIElement: The created button element.
        """
        return TextButton(x_pos, self.y - 29, label, pygame.font.SysFont('arial', 16), (255, 255, 255), action, alpha=100)

    def _draw_grid_on_surface(self):
        """
        Draws the transparent grid onto self.grid_surface.

        Returns:
            None
        """
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
        """
        Toggle the display of the grid and update the corresponding button text.

        Returns:
            None
        """
        self.grid = not self.grid
        if self.grid:
            self.toggle_button_grid.text = "Grid On"
        else:
            self.toggle_button_grid.text = "Grid Off"
        self.toggle_button_grid.image = self.toggle_button_grid.font.render(self.toggle_button_grid.text, True,
                                                                  self.toggle_button_grid.color)

    def toggle_bar(self):
        """
        Cycle through different bar chart display modes and update the button text.

        Returns:
            None
        """
        self.bar_chart += 1
        if self.bar_chart == 3:
            self.bar_chart = 0
        if self.bar_chart ==  2:
            self.toggle_button_chart.text = "Basic"
        elif self.bar_chart == 1:
            self.toggle_button_chart.text = "Candle"
        else:
            self.toggle_button_chart.text = "Line"
        self.toggle_button_chart.image = self.toggle_button_chart.font.render(self.toggle_button_chart.text, True,
                                                                  self.toggle_button_chart.color)

    def toggle_strategy(self):
        """
        Toggle the display of strategy indicators and update the corresponding button text.

        Returns:
            None
        """
        self.strategy_active = not self.strategy_active
        if self.strategy_active:
            self.toggle_button_strategy.text = "Indicator On"
        else:
            self.toggle_button_strategy.text = "Indicator Off"
        self.toggle_button_strategy.image = self.toggle_button_strategy.font.render(self.toggle_button_strategy.text, True,
                                                                  self.toggle_button_strategy.color)

    def toggle_color(self):
        """
        Toggle the color scheme between profit-based (RG Color) and fixed (B Color).

        Returns:
            None
        """
        self.prof_coloring = not self.prof_coloring
        if self.prof_coloring:
            self.toggle_button_color.text = "RG Color"
        else:
            self.toggle_button_color.text = "B Color"
        self.toggle_button_color.image = self.toggle_button_color.font.render(self.toggle_button_color.text, True,
                                                                  self.toggle_button_color.color)

    def calculate_colors(self):
        """
        Calculate colors for data points based on the previous average.

        Returns:
            List[tuple]: A list of RGB color tuples for each data point.
        """
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
        """
        Get the overlapping graphs with the current graph.

        Args:
            other_graphs (list): List of other graph objects to check for overlap.

        Returns:
            List[Graph]: List of graph objects that overlap with the current graph.
        """
        overlapping_graphs = [graph for graph in other_graphs if self.rect.colliderect(graph.rect)]
        return overlapping_graphs

    def display(self, screen, all_graphs=[]):
        """
        Display the graph on the given screen. This Function is scuffed but works.

        Args:
            screen (pygame.Surface): The Pygame surface to display the graph on.
            all_graphs (list): List of other graph objects for overlap detection.

        Returns:
            None
        """
        def render_transparent_text(surface, text, font, color, position, alpha):
            """
            Render transparent text on a given surface.

            Args:
                surface (pygame.Surface): The Pygame surface to render the text on.
                text (str): The text to be rendered.
                font (pygame.font.Font): The font used for rendering.
                color (tuple): RGB color tuple for the text.
                position (tuple): (x, y) position to render the text.
                alpha (int): Transparency value for the text.

            Returns:
                None
            """

            text_surf = font.render(text, True, color).convert_alpha()
            text_surf.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            surface.blit(text_surf, position)



        alpha_value = 128
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)


        if self.df is not None:
            start_idx, end_idx = self.display_range
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

            if self.bar_chart == 0:
                ohlc_data = displayed_data.resample('5T').agg({
                    self.column: ['first', 'max', 'min', 'last']
                })
                ohlc_data.columns = ['Open', 'High', 'Low', 'Close']
                ohlc_data.dropna(inplace=True)

                candle_width = max(1, self.width / len(ohlc_data) - 2)

                for idx, (timestamp, row) in enumerate(ohlc_data.iterrows()):
                    x_pos = self.x + (self.width / (len(ohlc_data) - 1) * idx)
                    y_open = self.y + self.height - (self.height * (row['Open'] - min_val) / (max_val - min_val))
                    y_high = self.y + self.height - (self.height * (row['High'] - min_val) / (max_val - min_val))
                    y_low = self.y + self.height - (self.height * (row['Low'] - min_val) / (max_val - min_val))
                    y_close = self.y + self.height - (self.height * (row['Close'] - min_val) / (max_val - min_val))

                    if self.prof_coloring:
                        lookback_period = 5
                        # Ensure you don't get an index out of range and then check the logic.
                        if idx - lookback_period >= 0 and ohlc_data['Close'].iloc[idx] > ohlc_data['Close'].iloc[
                            idx - lookback_period]:
                            current_color = (0, 255, 0)  # green for up
                        else:
                            current_color = (255, 0, 0)  # red for down
                    else:
                        current_color = self.color

                    # Draw the wick from Low to High
                    pygame.draw.line(screen, current_color, (int(x_pos), int(y_low)), (int(x_pos), int(y_high)), 1)

                    # Draw the body of the candlestick
                    if row['Close'] >= row['Open']:
                        pygame.draw.rect(screen, current_color, (
                            int(x_pos - candle_width / 2), int(y_open), candle_width, int(y_close - y_open)))
                    else:
                        pygame.draw.rect(screen, current_color, (
                            int(x_pos - candle_width / 2), int(y_close), candle_width, int(y_open - y_close)))


            # Define y positions for text
            y_pos_max = self.y + 5  # 5 pixels from the top edge of the graph
            y_pos_mid = self.y + self.height / 2 - 12  # centered in the middle, adjusted for text height
            y_pos_min = self.y + self.height - 25  # 25 pixels from the bottom edge to account for text height

            # Render the text
            text_max = self.font.render(f"{max_val:.2f}", True, self.label_color)
            text_mid = self.font.render(f"{mid_val:.2f}", True, self.label_color)
            text_min = self.font.render(f"{min_val:.2f}", True, self.label_color)

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
                time_text = self.font.render(time_values[idx], True, self.label_color)
                render_transparent_text(screen, time_values[idx], self.font, self.label_color,
                                        (x_pos - time_text.get_width() / 2, self.y + self.height + 5), alpha_value)

            prev_x_pos = None
            prev_y_pos = None

            if self.bar_chart == 1:
                ohlc_data = displayed_data.resample('5T').agg({self.column: ['first', 'max', 'min', 'last']})
                ohlc_data.columns = ['Open', 'High', 'Low', 'Close']
                ohlc_data.dropna(inplace=True)

                bar_width = max(1, self.width / len(ohlc_data) - 2)
                width_ratio = self.width / (len(ohlc_data) - 1)

                transparency = 128  # Adjust as needed. 0 is fully transparent, 255 is opaque.

                for idx, (_, row) in enumerate(ohlc_data.iterrows()):
                    x_pos = self.x + width_ratio * idx
                    y_values = [
                        self.y + self.height - (self.height * (row[key] - min_val) / denominator)
                        for key in ['Open', 'High', 'Low', 'Close']
                    ]

                    if self.prof_coloring:
                        lookback_period = 5  # Adjust as needed.

                        # Ensure you don't get an index out of range and then check the logic.
                        if idx - lookback_period >= 0 and ohlc_data['Close'].iloc[idx] > ohlc_data['Close'].iloc[
                            idx - lookback_period]:
                            current_color = (0, 255, 0)  # green for up
                        else:
                            current_color = (255, 0, 0)  # red for down
                    else:
                        current_color = self.color

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
            if self.bar_chart == 2:
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
                pygame.draw.circle(screen, (255, 255, 255), (int(x_pos), int(y_pos)), self.point_radius * 1.2)

        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)

        # Display the original title for the graph
        title_surf = self.font.render(self.original_title, True, self.color)
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
                    label_surface = self.font.render(label, True, color)
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
        """
        Compute the moving average of the graph's data.

        Args:
            window_size (int, optional): The size of the moving average window. Default is 3.

        Returns:
            pandas.Series or None: The moving average values if data is available, otherwise None.
        """
        if self.df is not None:
            return self.df[self.column].rolling(window=window_size).mean()
        return None

    def set_data_file(self, day):
        """
        Set the data file for the graph based on the specified day.

        Args:
            day (int): The day value to set for the data file.

        Returns:
            None
        """
        if not self.data_filename:  # If filename not set, don't continue
            return

        try:
            new_path = f"./data/{self.strategy_dir}/Day{day}.csv"
            new_df = pd.read_csv(new_path)
            self.df_path = new_path
            if not new_df.empty:
                self.df_path = new_path
                self.df = new_df
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
        """
        Update the graph when the slider's value changes.

        Args:
            value (int or tuple): The new value of the slider. Can be a single point or a range.

        Returns:
            None
        """
        if isinstance(value, tuple):  # Range slider updates
            start_idx, end_idx = value
            self.update_range(start_idx, end_idx)
            self.notify_observers(value)
        else:
            # Single point slider updates
            if self.df is not None:
                self.highlight_index = int(value)
                # Ensure the value is within the dataframe's bounds.
                self.highlight_index = max(0, min(len(self.df) - 1, self.highlight_index))

    def update_range(self, start_idx, end_idx):
        """
        Update the graph's displayed range when the range slider's value changes.

        Args:
            start_idx (int): The start index of the new range.
            end_idx (int): The end index of the new range.

        Returns:
            None
        """
        self.set_display_range(start_idx, end_idx)

    def set_display_range(self, start_idx, end_idx):
        """
        Set the displayed range for the graph.

        Args:
            start_idx (int): The start index of the new range.
            end_idx (int): The end index of the new range.

        Returns:
            None
        """
        if self.df is not None:
            max_idx = len(self.df) - 1
            start_idx = max(0, min(max_idx, start_idx))
            end_idx = max(0, min(max_idx, end_idx))
            self.display_range = (start_idx, end_idx)

    def update_day(self, day_value):
        """
        Update the graph's data file based on the specified day value.

        Args:
            day_value (int): The day value to set for the data file.

        Returns:
            None
        """
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
            bar_chart=data['is_bar'],
            font=pygame.font.SysFont('arial', 14)
        )




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
