import pygame
from utils.observer_pattern import Observable, Observer
from core.graph import Graph
from analysis.slider import Slider

# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

class DataTable(Observer):
    def __init__(self, x, y, graphs, font, initial_index=0):
        self.x = x
        self.y = y
        self.graphs = graphs  # A list of graphs
        self.font = font
        self.current_values = {}

        # Define the rectangle to represent the position and size
        self.width = 150  # Adjust this value based on your needs
        self.height = len(graphs) * 20 + 20  # 20 pixel gap between each value, adjust this if necessary
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.set_values(initial_index)

    def set_values(self, index):
        self.current_values.clear()  # Clear any previous values
        for graph in self.graphs:
            if graph.df is not None and 0 <= index < len(graph.df):
                unique_key = f"{graph.df_path}_{graph.column}"  # Create a unique key combining both file name and column name
                self.current_values[unique_key] = graph.df[graph.column].iloc[index]

    def display(self, screen):
        if self.current_values:
            for i, (key, value) in enumerate(self.current_values.items()):
                column_name = key.split('_')[-1]  # Extract the column name from the unique key
                text = self.font.render(f"{column_name}: {value}", True, (0, 0, 0))
                screen.blit(text, (self.x, self.y + i * 20))

    def handle_events(self, event):
        pass

    def update(self, value):
        # Set the values to display based on the slider's value.
        self.set_values(int(value))

    def update_position(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)  # Update the rect's position as well


    def serialize(self):
        # Here, we only serialize the position of the DataTable, as other attributes can be reconstructed
        return {
            "type": "DataTable",
            "x": self.x,
            "y": self.y
        }

    @staticmethod
    def deserialize(data, graphs, font):
        table = DataTable(data["x"], data["y"], graphs, font)
        return table

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Interactive Data Visualization')

    # Graph instances
    test_graph1 = Graph(data_file='./data/PriceDay1.csv')
    test_graph2 = Graph(data_file='./data/PriceDay2.csv')

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

