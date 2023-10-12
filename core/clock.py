import pygame
from datetime import datetime
from utils.pygame_helper_classes import Label
from utils.uiux import UIElement
class Clock(UIElement):
    """
    A class for displaying a digital clock on a Pygame screen.

    Attributes:
        x_position (int): The x-coordinate position of the clock on the screen.
        y_position (int): The y-coordinate position of the clock on the screen.
        text_color (str): The color of the clock's text. Default is "black".
        border_color (str): The color of the clock's border. Default is "black".
        bg_color (str): The background color of the clock. Default is "darkGray".

    Constants:
        COLOR_MAP (dict): A dictionary mapping color names to RGB values.

    Methods:
        display(screen): Display the clock on the Pygame screen.

    Example:
        clock_instance = Clock(10, 10, text_color="lightRed", border_color="darkRed", bg_color="lightGray")
        clock_instance.display(screen)
    """

    COLOR_MAP = {
        "darkGreen": (0, 100, 0),
        "green": (0, 128, 0),
        "lightGreen": (144, 238, 144),
        "darkGray": (169, 169, 169),
        "lightGray": (211, 211, 211),
        "red": (255, 0, 0),
        "darkRed": (139, 0, 0),
        "lightRed": (255, 182, 193),
        "black": (0, 0, 0)
    }

    def __init__(self, x=10, y=10, width=None, height=None, text_color="black", border_color="black",
                 bg_color="darkGray"):
        super().__init__(x, y)
        self.width = width if width else 150
        self.height = height if height else 50
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Set colors using the provided strings and the COLOR_MAP
        self.text_rgb = self.COLOR_MAP.get(text_color, self.COLOR_MAP["green"])
        self.border_rgb = self.COLOR_MAP.get(border_color, self.COLOR_MAP["darkGreen"])
        self.bg_rgb = self.COLOR_MAP.get(bg_color, self.COLOR_MAP["lightGray"])

        self.font = pygame.font.SysFont('Arial', 16)


    def display(self, screen):
        current_time = datetime.now().strftime('%I:%M:%S %p')

        start_x_position = self.x
        x_position = self.x

        labels = []
        max_char_height = 0  # Track the maximum character height

        for char in current_time:
            label = Label(self.font, char, self.text_rgb, (x_position, self.y), anchor="topleft")
            if char == '9':
                label.rect.y -= 2
            x_position += label.rect.width
            labels.append(label)

            # Update the maximum character height
            max_char_height = max(max_char_height, label.rect.height)

        max_width = sum(label.rect.width for label in labels)

        # Draw background rectangle
        pygame.draw.rect(screen, self.bg_rgb, (start_x_position - 5, self.y - 5, max_width + 10, max_char_height + 10))

        # Reset x_position and y_position for drawing the text (centered vertically)
        x_position = start_x_position
        y_position = self.y + (max_char_height - labels[0].rect.height) // 2

        # Draw the text
        for label in labels:
            label.rect.topleft = (x_position, y_position)
            label.draw(screen)
            x_position += label.rect.width

        # Draw the border rectangle
        pygame.draw.rect(screen, self.border_rgb, (start_x_position - 5, self.y - 5, max_width + 10, max_char_height + 10), 2)

    def update_position(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

    def resize(self, new_width, new_height):
        self.set_size(new_width, new_height)  # Use the base class's method

    def serialize(self):
        data = super().serialize()
        data.update({
            'type': 'Clock',
            'text_color': next(k for k, v in self.COLOR_MAP.items() if v == self.text_rgb),
            'border_color': next(k for k, v in self.COLOR_MAP.items() if v == self.border_rgb),
            'bg_color': next(k for k, v in self.COLOR_MAP.items() if v == self.bg_rgb)
        })
        return data

    @staticmethod
    def deserialize(data):
        clock = Clock(
            x=data["x"],
            y=data["y"],
            width=data.get("width", 150),  # Providing default width
            height=data.get("height", 50),  # Providing default height
            text_color=data["text_color"],
            border_color=data["border_color"],
            bg_color=data["bg_color"]
        )
        return clock


if __name__ == "__main__":
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Clock Demo')

    clock_instance = Clock(10, 10, text_color="lightRed", border_color="darkRed", bg_color="lightGray")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # Filling the screen with a white color
        clock_instance.display(screen)

        pygame.display.flip()

    pygame.quit()
