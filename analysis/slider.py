import pygame
from utils.observer_pattern import Observable
from utils.uiux import UIElement
class Slider(UIElement, Observable):

    def __init__(self, x, y, width, min_value, max_value):
        UIElement.__init__(self, x, y)  # Initialize UIElement with position (x and y)
        Observable.__init__(self)

        # Set size directly in the Slider
        self.width = width
        self.height = 20  # Assuming this is the height of your slider.

        # Update the rect to account for the new width and height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


        # Rest of the Slider's attributes initialization
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = self.min_value
        self.handle_width = self.width * 0.05
        self.handle_color = (0, 128, 255)  # Blue
        self.track_color = (200, 200, 200)  # Grey

        # Additional attribute to check if the handle is being dragged
        self.dragging = False
        self.dragging_position = False

    def display(self, screen):
        # Draw the background of the slider
        pygame.draw.rect(screen, self.track_color, self.rect)

        # Calculate the handle position based on the current_value
        handle_x = self.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)

        # Draw the handle
        pygame.draw.rect(screen, self.handle_color, (handle_x, self.y, self.handle_width, self.height))

    def handle_events(self, event, is_locked=False):
        if is_locked:  # Assumes you make GLOBAL_LOCK a class variable of Application
            return
        handle_x = self.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * (
                self.width - self.handle_width)
        handle_rect = pygame.Rect(handle_x, self.y, self.handle_width, self.height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and handle_rect.collidepoint(event.pos):  # Left click on handle
                self.dragging = True
            elif event.button == 3 and self.rect.collidepoint(event.pos):  # Right click on slider
                self.dragging_position = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.dragging_position = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:  # If dragging the handle
                self.update_value_from_pos(event.pos[0])
            elif self.dragging_position:  # If dragging the entire slider's position
                self.update_position(*event.rel)

    def update_position(self, dx, dy):
        """Update the position of the slider."""
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.notify_observers(self.current_value)

    def is_clicked(self, x, y):
        return self.rect.collidepoint(x, y)

    def update_value_from_pos(self, x):
        relative_x = x - self.x
        self.current_value = self.min_value + relative_x / (self.width - self.handle_width) * (self.max_value - self.min_value)
        self.current_value = max(self.min_value, min(self.max_value, self.current_value))
        self.notify_observers(self.current_value)

    def serialize(self):
        data = super().serialize()  # Get base class serialization data.
        data.update({
            "type": "Slider",
            "width": self.width,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "current_value": self.current_value
        })
        return data

    @staticmethod
    def deserialize(data):
        width = data.get("width", 400)  # Default to 400 if width is not present.
        slider = Slider(data["x"], data["y"], width, data["min_value"], data["max_value"])
        slider.current_value = data["current_value"]
        return slider


# Colors
WHITE = (255, 255, 255)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Graph Test with Slider')

    # Instantiate graph and make it observe the slider
    test_graph = Graph(data_file='./data/PriceDay3.csv')  # Replace with the correct path if needed

    if test_graph.df is not None and test_graph.column in test_graph.df.columns:
        slider_max_value = len(test_graph.df[test_graph.column]) - 1
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