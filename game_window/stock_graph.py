import pygame
import pandas as pd
from clock import Clock
# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600


class Graph:
    current_x_offset = 0  # Class variable to track x-offset for new graphs
    spacing = 20  # Space between each graph
    MARGIN = 10  # Margin for all sides

    def __init__(self, is_live=False, data_file=None, size_multiplier=1.0, y_offset_percentage=0.6):
        global HEIGHT
        self.is_live = is_live

        # Load data if data_file is provided
        self.df = pd.read_csv(data_file) if data_file else None

        # Define size
        self.width = (WIDTH - 2 * Graph.MARGIN) * 0.5 * size_multiplier
        self.height = (HEIGHT - 2 * Graph.MARGIN) * 0.5 * size_multiplier

        # x and y position adjusted for margin and spacing
        self.x = Graph.current_x_offset + Graph.MARGIN
        self.y = HEIGHT * y_offset_percentage - self.height * 0.5

        # Increase the offset for next graphs by width + spacing
        Graph.current_x_offset += self.width + Graph.spacing

    def display(self, screen):
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

        self.rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)

    def update_position(self, dx, dy):
        self.x += dx
        self.y += dy


if __name__ == "__main__":
    pygame.init()

    # Initialize the Clock and Graph objects
    clock_instance = Clock(10, 10, text_color="black", border_color="black", bg_color="darkGray")
    main_graph = Graph(is_main=True, is_live=False, data_file='./data/PriceDay.csv', size_multiplier=1.5)

    # Create side (auxiliary) graphs; this will adjust the global HEIGHT as necessary
    side_graph1 = Graph(is_main=False, is_live=False, data_file='./data/PriceDay2.csv', size_multiplier=.9)
    side_graph2 = Graph(is_main=False, is_live=False, data_file='./data/PriceDay3.csv', size_multiplier=.9)

    # Now, initialize the Pygame screen with possibly adjusted WIDTH and HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('StockGame with Graph')

    # Main loop for rendering
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        clock_instance.display(screen)
        main_graph.display(screen)
        side_graph1.display(screen)
        side_graph2.display(screen)

        pygame.display.flip()

    pygame.quit()