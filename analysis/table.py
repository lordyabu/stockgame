import pygame
from utils.observer_pattern import Observable, Observer
from core.graph import Graph
from analysis.slider import Slider

# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

class DataTable(Observer):
    def __init__(self, x, y, df, font):
        self.x = x
        self.y = y
        self.df = df
        self.font = font
        self.current_price = None

    def set_row(self, index):
        if 0 <= index < len(self.df):
            self.current_price = self.df['Price'].iloc[index]

    def display(self, screen):
        if self.current_price is not None:
            text = self.font.render(f"Price: {self.current_price}", True, (0, 0, 0))
            screen.blit(text, (self.x, self.y))

    def handle_events(self, event):
        # Handle scrolling, row selection, etc.
        pass

    def update(self, value):
        # Set the row to display based on the slider's value.
        self.set_row(int(value))


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Interactive Data Visualization')

    # Graph instance
    test_graph = Graph(data_file='./data/PriceDay.csv')

    # Slider instance
    test_slider = Slider(x=50, y=500, width=700, min_value=0, max_value=len(test_graph.df) - 1)

    # DataTable instance
    font = pygame.font.SysFont(None, 24)
    data_table = DataTable(x=650, y=50, df=test_graph.df, font=font)

    # Add the DataTable and Graph as observers of the slider
    test_slider.add_observer(test_graph)
    test_slider.add_observer(data_table)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            test_slider.handle_events(event)

        screen.fill(WHITE)
        test_graph.display(screen)
        test_slider.display(screen)
        data_table.display(screen)
        pygame.display.flip()

    pygame.quit()
