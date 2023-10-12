import pandas as pd
import pygame
from utils.observering import Observable, Observer
from core.graph import Graph
from analysis.slider import Slider
from utils.uiux import UIElement
from analysis.helper_button import Button
# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

class DataTable(UIElement, Observer):
    """
        Initializes a DataTable instance with the given parameters.

        Parameters
        ----------
        x : int
            The x-coordinate position of the table on the screen.
        y : int
            The y-coordinate position of the table on the screen.
        graphs : list of Graph
            A list of Graph instances containing data to display.
        font : pygame.font.Font
            Font object used for rendering text within the table.
        initial_index : int, optional
            The initial index for the data values. Default is 0.
        visible_rows : int, optional
            The number of visible rows in the table. Default is 10.

        Methods
        -------
        - display(screen): Renders the table on a Pygame screen.
        - ... (other methods)

        """
    def __init__(self, x, y, graphs, font, initial_index=0, visible_rows=10):
        """
        Initializes the DataTable instance with the given parameters.

        Parameters
        ----------
        x : int
            The x-coordinate position of the data table on the screen.
        y : int
            The y-coordinate position of the data table on the screen.
        graphs : list[Graph]
            A list of `Graph` objects that represent the data to be displayed in the table.
        font : pygame.font.Font
            Font object used for rendering the table's text.
        initial_index : int, optional
            The starting index for the rows to be displayed. Default is 0.
        visible_rows : int, optional
            The number of rows that will be visible at once in the table. Default is 10.

        Attributes
        ----------
        graphs : list[Graph]
            A list of `Graph` objects representing the data.
        font : pygame.font.Font
            Font object used for rendering text.
        current_values : dict
            Dictionary storing the current rows of data to be displayed, with column names as keys.
        row_height : int
            Height of each row in the table.
        visible_rows : int
            Number of rows visible at once in the table.
        height : int
            Total height of the table.
        column_spacing : int
            Spacing between each column in the table.
        width : int
            Total width of the table.
        alternate_color : tuple
            RGB color for alternating rows in the table.
        current_index : int
            Current index indicating which rows are being displayed.
        dragging : bool
            Boolean indicating whether the table is currently being dragged.
        rect : pygame.Rect
            Pygame rectangle object representing the table's position and size.
        column_stats : dict
            Dictionary storing statistical data (max, average, min) for each column.
        highlighted_row : int
            Index of the currently highlighted row, or -1 if no row is highlighted.

        Returns
        -------
        None
        """
        super().__init__(x, y)
        self.graphs = graphs
        self.font = font
        self.current_values = {}

        self.row_height = 20
        self.visible_rows = visible_rows  # Number of rows you want to display at once.

        self.height = self.row_height * (self.visible_rows + 1)  # +1 for the headers
        # Assuming an average width of 60 pixels for the DateTime column and each graph column
        column_widths = [60 for _ in range(len(graphs) + 1)]  # +1 for the DateTime column

        # Now, let's calculate the total width required:
        self.width = sum(column_widths)

        # For column spacing, use:
        self.column_spacing = 10  # 10 pixels between columns, adjust as needed

        # Add column spacing to width:
        self.width += (len(graphs)) * self.column_spacing  # Add spacing for all but the last column`

        self.alternate_color = (235, 235, 235)  # Light gray for alternating rows

        self.current_index = initial_index

        self.dragging = False

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.column_stats = {}


        self.set_values(initial_index)

        for graph in self.graphs:
            high_val = graph.df[graph.column].max()
            low_val = graph.df[graph.column].min()
            avg_val = graph.df[graph.column].mean()

            self.column_stats[graph.column] = (high_val, avg_val, low_val)

        self.highlighted_row = -1  # Initially no row is highlighted

    def get_gradient_color(self, value, high_val, avg_val, low_val):
        """
        Determine the color for a specific value based on a gradient.

        The gradient goes from red (low values) to white (average values)
        to green (high values).

        Parameters:
        - value (float): The specific value for which the color is being determined.
        - high_val (float): The high threshold value.
        - avg_val (float): The average value.
        - low_val (float): The low threshold value.

        Returns:
        - pygame.Color: The interpolated color based on the given value's position within the gradient.
        """
        high_color = pygame.Color('green')
        avg_color = pygame.Color('white')
        low_color = pygame.Color('red')

        # Determine which segment of the gradient we're in and interpolate
        if value >= avg_val:
            weight = (value - avg_val) / (high_val - avg_val)
            color = self.interpolate_color(avg_color, high_color, weight)
        else:
            weight = (value - low_val) / (avg_val - low_val)
            color = self.interpolate_color(low_color, avg_color, weight)

        return color

    def interpolate_color(self, color1, color2, weight):
        """
        Linearly interpolate between two RGB colors based on a given weight.

        Parameters:
        - color1 (pygame.Color): The first color.
        - color2 (pygame.Color): The second color.
        - weight (float): The weight for interpolation, ranging from 0 to 1.

        Returns:
        - pygame.Color: The interpolated color.
        """
        # Linearly interpolate between the two RGB values
        r = color1.r * (1 - weight) + color2.r * weight
        g = color1.g * (1 - weight) + color2.g * weight
        b = color1.b * (1 - weight) + color2.b * weight

        return pygame.Color(int(r), int(g), int(b))

    def set_values(self, index):
        """
        Set the values to be displayed in the DataTable based on a given index.

        The method determines which rows of data to display based on the provided index.
        It updates the current_values dictionary with the data for the current view and also
        recalculates column widths based on the content.

        Parameters:
        - index (int): The index around which the view should be centered.

        Returns:
        - None
        """
        self.current_values.clear()

        start_index = index - self.visible_rows // 2
        end_index = start_index + self.visible_rows

        # Adjust start and end indices
        if end_index > len(self.graphs[0].df):  # Assuming all graphs have the same length
            end_index = len(self.graphs[0].df)
            start_index = end_index - self.visible_rows
        if start_index < 0:
            start_index = 0
            end_index = self.visible_rows

        graph_df = pd.read_csv(self.graphs[0].df_path)  # Assuming all graphs share the same DateTime column
        dates_times = graph_df["DateTime"].str.split(' ').tolist()[start_index:end_index]

        self.current_values["DateTime"] = [dt[1] for dt in dates_times]  # Extracting the time part


        self.column_widths = []  # List to store widths of each column

        for graph in self.graphs:
            high_val = graph.df[graph.column].max()
            low_val = graph.df[graph.column].min()
            avg_val = graph.df[graph.column].mean()

            self.column_stats[graph.column] = (high_val, avg_val, low_val)
            if graph.column not in self.current_values:
                self.current_values[graph.column] = graph.df[graph.column].iloc[start_index:end_index].tolist()

        for column in ["DateTime"] + [graph.column for graph in self.graphs]:  # Including the DateTime column
            if column in self.current_values:
                max_width = max([len(str(v)) for v in self.current_values[column]])
                self.column_widths.append(max_width * 10)  # Multiplied by 10 as a rough estimate for pixel width

        # Adjust the width of the table based on the total width of columns
        self.width = sum(self.column_widths) + len(self.column_widths) * self.column_spacing - self.column_spacing
        self.rect.width = self.width  # Adjust the width of the rectangle as well

        self.highlighted_row = self.current_index - start_index

    def display(self, screen):
        """
        Display the data table on the given Pygame screen.

        This method renders the table with its headers, data values, and appropriate colors.
        The method uses various helper functions and attributes of the class to draw the table
        with its columns and rows, color the cells based on their values, and highlight selected rows.

        Parameters:
        - screen (pygame.Surface): The Pygame screen where the table should be rendered.

        Returns:
        - None

        Note:
        - The method assumes that the DateTime column is always present.
        - Colors for columns are determined by their associated graph objects.
        """
        def adjust_color(color, alpha=128):
            """
            Adjusts the color brightness and transparency.

            Parameters:
            - color (tuple): An RGB tuple representing the color to adjust.
            - alpha (int, optional): The desired transparency level (alpha channel). Default is 128.

            Returns:
            - tuple: The adjusted color with reduced brightness and the given alpha value.
            """
            return (color[0] // 2, color[1] // 2, color[2] // 2, alpha)

        if self.current_values:
            x_offset = self.x
            for idx, column in enumerate(["DateTime"] + [graph.column for graph in self.graphs]):
                color = pygame.Color("black") if column == "DateTime" else self.graphs[idx - 1].color
                if column == "DateTime":
                    column = 'Time'
                text = self.font.render(column, True, color)

                # Calculate centering for column header text
                header_text_x = x_offset + (self.column_widths[idx] - text.get_width()) / 2
                screen.blit(text, (header_text_x, self.y))
                x_offset += self.column_widths[idx] + self.column_spacing

            border_width = 1

            # Inside the loop where you're displaying data row-wise:
            for row in range(self.visible_rows):
                x_offset = self.x

                for idx, column in enumerate(self.current_values):
                    value = self.current_values[column][row]

                    # Determine text color
                    text_color = pygame.Color("white") if row == self.highlighted_row else pygame.Color("black")
                    original_color = pygame.Color("black") if column == "DateTime" else self.graphs[idx - 1].color
                    column_color = adjust_color(original_color)

                    # Draw the left border of each column
                    pygame.draw.line(screen, column_color,
                                     (x_offset, self.y + row * self.row_height),
                                     (x_offset, self.y + (row + 1) * self.row_height), border_width)

                    if column in self.column_stats:  # This checks if the column is not DateTime
                        high_val = max(self.current_values[column])
                        low_val = min(self.current_values[column])
                        avg_val = sum(self.current_values[column]) / len(self.current_values[column])

                        try:
                            cell_bg_color = self.get_gradient_color(value, high_val, avg_val, low_val)
                        except:
                            cell_bg_color = (100, 100, 100)
                        cell_rect = pygame.Rect(x_offset, self.y + (row + 1) * self.row_height, self.column_widths[idx],
                                                self.row_height)

                        # Create a temporary surface and fill it with the desired color and alpha transparency
                        temp_surface = pygame.Surface((self.column_widths[idx], self.row_height), pygame.SRCALPHA)
                        temp_surface.fill(
                            (cell_bg_color[0], cell_bg_color[1], cell_bg_color[2], 150))  # 128 for semi-transparency

                        # Blit the surface onto the main screen at the cell's location
                        screen.blit(temp_surface, (x_offset, self.y + (row + 1) * self.row_height))

                    text_surface = self.font.render(f"{value}", True, text_color)

                    # Calculate the centered x and y positions:
                    text_x = x_offset + (self.column_widths[idx] - text_surface.get_width()) / 2
                    text_y = self.y + (row + 1) * self.row_height + (self.row_height - text_surface.get_height()) / 2

                    screen.blit(text_surface, (text_x, text_y))

                    # Increment the x_offset for the next column before drawing the right border
                    x_offset += self.column_widths[idx]

                    # Draw the right border for each column
                    pygame.draw.line(screen, column_color,
                                     (x_offset, self.y + row * self.row_height),
                                     (x_offset, self.y + (row + 1) * self.row_height), border_width)

                    x_offset += self.column_spacing

                # Draw horizontal line at the bottom of each row
                pygame.draw.line(screen, pygame.Color("black"),
                                 (self.x, self.y + (row + 1) * self.row_height),
                                 (self.x + self.width, self.y + (row + 1) * self.row_height), border_width)

            # Draw a border for the entire table
            pygame.draw.rect(screen, pygame.Color("black"), self.rect, 1)

    def handle_events(self, event):
        """
        Handle Pygame events related to the DataTable object.

        This method manages dragging interactions with the table, allowing the user to reposition
        the table on the screen by clicking and dragging.

        Parameters:
        - event (pygame.event.Event): A Pygame event object representing the current event to handle.

        Returns:
        - None
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx, dy = event.rel
            self.update_position(dx, dy)

    def update(self, value):
        """
        Update the table data based on the new index value.

        The method updates the current index of the table and recalculates the values
        that should be shown based on the new index.

        Parameters:
        - value (float or int): The new value or index to use for displaying data in the table.

        Returns:
        - None
        """
        self.current_index = int(value)
        self.set_values(self.current_index)

    def update_position(self, dx, dy):
        """
        Update the position of the DataTable on the screen.

        Parameters:
        - dx (int): Change in x-coordinate.
        - dy (int): Change in y-coordinate.

        Returns:
        - None
        """
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)  # Update the rect's position as well


    def serialize(self):
        """
        Serialize the essential attributes of the DataTable for saving or transmission.

        Only attributes essential for reconstructing the table's state are serialized,
        as other attributes can be recalculated upon deserialization.

        Returns:
        - dict: A dictionary containing serialized data of the DataTable.
        """
        return {
            "type": "DataTable",
            "x": self.x,
            "y": self.y,
            'vals_shown' : self.visible_rows
        }

    @staticmethod
    def deserialize(data, graphs, font):
        """
        Deserialize a dictionary of serialized data to recreate a DataTable instance.

        Parameters:
        - data (dict): A dictionary containing serialized data of a DataTable.
        - graphs (list): A list of Graph objects to associate with the table.
        - font (pygame.font.Font): A Pygame font object to be used for text rendering in the table.

        Returns:
        - DataTable: A new DataTable object constructed from the serialized data.
        """
        table = DataTable(data["x"], data["y"], graphs, font, visible_rows=data['vals_shown'])
        return table

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Interactive Data Visualization')

    # Graph instances
    test_graph1 = Graph(data_file='./data/PriceDay3.csv', color=(255, 0, 0), title="Graph 1")
    test_graph2 = Graph(data_file='./data/PriceDay3.csv', color=(0, 255, 0), title="Graph 2")

    # Slider instance
    test_slider = Slider(x=50, y=500, width=700, min_value=0, max_value=max(len(test_graph1.df), len(test_graph2.df)) - 1)
    test_slider.add_observer(test_graph1)
    test_slider.add_observer(test_graph2)

    # DataTable instance
    font = pygame.font.SysFont(None, 24)
    graphs = [test_graph1, test_graph2]
    data_table = DataTable(x=650, y=50, graphs=graphs, font=font)

    # Add the DataTable and Graph as observers of the slider
    test_slider.add_observer(data_table)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            test_slider.handle_events(event)

        screen.fill(WHITE)
        test_graph1.display(screen)
        test_graph2.display(screen)
        test_slider.display(screen)
        data_table.display(screen)
        pygame.display.flip()

    pygame.quit()

