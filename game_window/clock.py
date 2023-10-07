import pygame
from datetime import datetime
from pygame_helper_classes import Label

class Clock:
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

    def __init__(self, x=10, y=10, width=None, height=None, text_color="black", border_color="black", bg_color="darkGray"):
        """
        Initialize a Clock instance.

        Args:
            x (int, optional): The x-coordinate position of the clock. Default is 10.
            y (int, optional): The y-coordinate position of the clock. Default is 10.
            text_color (str, optional): The color of the clock's text. Default is "black".
            border_color (str, optional): The color of the clock's border. Default is "black".
            bg_color (str, optional): The background color of the clock. Default is "darkGray".
        """
        self.x_position = x
        self.y_position = y

        self.width = width
        self.height = height

        # Set colors using the provided strings and the COLOR_MAP
        self.text_rgb = self.COLOR_MAP.get(text_color, self.COLOR_MAP["green"])
        self.border_rgb = self.COLOR_MAP.get(border_color, self.COLOR_MAP["darkGreen"])
        self.bg_rgb = self.COLOR_MAP.get(bg_color, self.COLOR_MAP["lightGray"])
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)

    def display(self, screen):
        """
        Display the clock on the Pygame screen.

        Args:
            screen (pygame.Surface): The Pygame surface where the clock will be displayed.
        """
        current_time = datetime.now().strftime('%I:%M:%S %p')
        font = pygame.font.Font(None, 36)

        start_x_position = self.x_position  # Save the starting position for later resetting
        x_position = self.x_position

        labels = []

        # First, calculate positions and dimensions without drawing
        for char in current_time:
            label = Label(font, char, self.text_rgb, (x_position, self.y_position), anchor="topleft")
            if char == '9':
                label.rect.y -= 2
            x_position += label.rect.width
            labels.append(label)

        max_width = sum(label.rect.width for label in labels)
        max_height = max(label.rect.height for label in labels)

        # Draw background rectangle
        pygame.draw.rect(screen, self.bg_rgb, (start_x_position - 5, self.y_position - 5, max_width + 10, max_height + 10))

        # Reset x_position for drawing the text
        x_position = start_x_position

        # Draw the text
        for label in labels:
            label.draw(screen)

        # Draw the border rectangle
        pygame.draw.rect(screen, self.border_rgb, (start_x_position - 5, self.y_position - 5, max_width + 10, max_height + 10), 2)

    def update_position(self, dx, dy):
        self.x_position += dx  # Corrected from self.x
        self.y_position += dy  # Corrected from self.y
        self.rect.topleft = (self.x_position, self.y_position)

    def resize(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.rect.size = (self.width, self.height)


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
