from utils.uiux import UIElement
import pygame
import os
from core.graph import Graph


class DaySwitch(UIElement):
    def __init__(self, x, y, graphs=[], max_days=99):
        super().__init__(x, y)
        self.max_days = max_days
        self.current_day = 1
        self.font = pygame.font.SysFont(None, 24)

        self.arrow_size = 20
        self.padding = 10

        self.graphs = graphs

        # Define clickable areas
        self.left_arrow_rect = pygame.Rect(x, y, self.arrow_size, self.arrow_size)
        self.right_arrow_rect = pygame.Rect(x + 2 * self.padding + self.arrow_size, y, self.arrow_size, self.arrow_size)

    def display(self, screen):
        pygame.draw.polygon(screen, (0, 0, 0), [(self.left_arrow_rect.x + self.arrow_size, self.left_arrow_rect.y),
                                                (self.left_arrow_rect.x, self.left_arrow_rect.centery),
                                                (self.left_arrow_rect.x + self.arrow_size,
                                                 self.left_arrow_rect.y + self.arrow_size)])

        pygame.draw.polygon(screen, (0, 0, 0), [(self.right_arrow_rect.x, self.right_arrow_rect.y),
                                                (self.right_arrow_rect.x + self.arrow_size,
                                                 self.right_arrow_rect.centery),
                                                (self.right_arrow_rect.x, self.right_arrow_rect.y + self.arrow_size)])

        day_text = self.font.render(f"Day{self.current_day}", True, (0, 0, 0))
        screen.blit(day_text, (self.x + self.padding + self.arrow_size, self.y))

    def _move_day(self, direction):
        ...
        # Notify all graph objects to change their data file
        for graph in self.graphs:
            graph.set_data_file(self.current_day)

    def check_click(self, pos):
        if self.left_arrow_rect.collidepoint(pos):
            self._move_day(-1)
        elif self.right_arrow_rect.collidepoint(pos):
            self._move_day(1)

    def _move_day(self, direction):
        self.current_day += direction
        if self.current_day > self.max_days:
            self.current_day = 1
        elif self.current_day < 1:
            self.current_day = self.max_days

        # Check if directory exists, otherwise wrap around
        while not os.path.exists(f"./data/Day{self.current_day}"):
            self.current_day += direction
            if self.current_day > self.max_days:
                self.current_day = 1
            elif self.current_day < 1:
                self.current_day = self.max_days

        for graph in self.graphs:
            graph.set_data_file(self.current_day)

    def serialize(self):
        """Serialize the DaySwitch instance into a dictionary."""
        data = {
            'type': "Dayswitch",
            'x': self.x,
            'y': self.y,
            'current_day': self.current_day,
            'max_days': self.max_days
        }
        return data

    @staticmethod
    def deserialize(data, graphs=[]):
        """Create a DaySwitch instance from serialized data."""
        x = data['x']
        y = data['y']
        current_day = data.get('current_day', 1)
        max_days = data.get('max_days', 99)

        # Restore the DaySwitch instance with the saved day and position.
        day_switch = DaySwitch(x, y, graphs=graphs, max_days=max_days)
        day_switch.current_day = current_day
        return day_switch


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
