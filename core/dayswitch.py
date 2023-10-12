from utils.uiux import UIElement
from utils.observer_pattern import Observable
import pygame
import os
from core.graph import Graph
import pandas as pd

class DaySwitch(UIElement, Observable):
    def __init__(self, x, y, graphs=[], max_days=99, strategy_dir='strategy_zero', show_date=True):
        super().__init__(x, y)
        self.show_date = show_date
        self.max_days = max_days
        self.current_day = 1
        self.font = pygame.font.SysFont('arial', 32)  # Increased the font size

        self.arrow_size = 40  # Increased from 20 to 80
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
        self.show_date = show_date  # New variable

    def display(self, screen):
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
        self.graphs = []

    def add_graphs(self, graphs):
        self.graphs.extend(graphs)


    def check_click(self, pos):
        if self.left_arrow_rect.collidepoint(pos):
            self._move_day(-1)
        elif self.right_arrow_rect.collidepoint(pos):
            self._move_day(1)
        else:
            pass

    def _move_day(self, direction):
        #  print("MOVING")
        self.current_day += direction
        if self.current_day > self.max_days:
            self.current_day = 1
        elif self.current_day < 1:
            self.current_day = self.max_days

        # Check if directory exists, otherwise wrap around
        # print(f"./data/{self.strategy_dir}/Day{self.current_day}")
        while not os.path.exists(f"./data/{self.strategy_dir}/Day{self.current_day}.csv"):
            self.current_day += direction
            if self.current_day > self.max_days:
                self.current_day = 1
            elif self.current_day < 1:
                self.current_day = self.max_days

        for graph in self.graphs:
            # print("SETTING DAY", self.current_day)
            graph.set_data_file(self.current_day)

    def serialize(self):
        """Serialize the DaySwitch instance into a dictionary."""
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
        """Create a DaySwitch instance from serialized data."""
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
        """Update the position of the DaySwitch and its sub-elements."""
        self.x += dx
        self.y += dy

        self.rect.move_ip(dx, dy)
        self.left_arrow_rect.move_ip(dx, dy)
        self.right_arrow_rect.move_ip(dx, dy)

    def resize(self, new_width, new_height):
        pass  # Implement if needed


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
