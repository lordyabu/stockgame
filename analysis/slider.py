import pygame
from utils.observer_pattern import Observable
from core.graph import Graph

class Slider(Observable):
    def __init__(self, x, y, width, min_value, max_value):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = self.min_value
        self.handle_width = self.width * 0.05
        self.handle_color = (0, 128, 255)  # Blue
        self.track_color = (200, 200, 200)  # Grey

        # Additional attribute to check if the handle is being dragged
        self.dragging = False

    def display(self, screen):
        pygame.draw.rect(screen, self.track_color, (self.x, self.y, self.width, self.height))
        handle_x = self.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * (
                    self.width - self.handle_width)
        pygame.draw.rect(screen, self.handle_color, (handle_x, self.y, self.handle_width, self.height))

    def handle_events(self, event):
        handle_x = self.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if the click is within the handle's boundaries
                if handle_x <= event.pos[0] <= handle_x + self.handle_width and self.y <= event.pos[
                    1] <= self.y + self.height:
                    self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                rel_x = event.pos[0] - self.x
                self.current_value = (rel_x / self.width) * (self.max_value - self.min_value) + self.min_value
                self.current_value = max(min(self.current_value, self.max_value), self.min_value)

                # Notify observers about the change
                self.notify_observers(self.current_value)




# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Graph Test')


    # Instantiate graph and make it observe the slider
    test_graph = Graph(data_file='./data/PriceDay.csv')  # Replace with the correct path if needed
    if test_graph.df is not None:
        slider_max_value = len(test_graph.df) - 1
    else:
        slider_max_value = 100  # Default value if the DataFrame is not available.

    slider = Slider(100, 550, 400, 0, slider_max_value)
    slider.add_observer(test_graph)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            slider.handle_events(event)

        screen.fill(WHITE)
        test_graph.display(screen)
        slider.display(screen)  # Ensure you're drawing the slider
        pygame.display.flip()

    pygame.quit()

