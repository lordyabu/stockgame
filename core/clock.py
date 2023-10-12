import pygame
from datetime import datetime
from utils.pygame_helper_classes import Label
from utils.uiux import UIElement
class Clock(UIElement):
    """
    A class for displaying a digital clock on a Pygame screen.


    Constants:
        COLOR_MAP (dict): A dictionary mapping color names to RGB values.

    Methods
    -------
    display(screen):
        Displays the current time on the Pygame screen.
    update_position(dx, dy):
        Updates the position of the clock on the screen by the given deltas.
    resize(new_width, new_height):
        Resizes the clock's display area to the specified dimensions.
    serialize():
        Returns a serialized representation of the clock instance as a dictionary.
    deserialize(data):
        Returns a Clock instance created from the provided serialized data.

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
        """
        Initializes a Clock instance with the specified position, dimensions, and colors.

        Parameters
        ----------
        x : int, optional
            The x-coordinate position of the clock on the screen. Default is 10.
        y : int, optional
            The y-coordinate position of the clock on the screen. Default is 10.
        width : int, optional
            The width of the clock. If not provided, the default width will be 150.
        height : int, optional
            The height of the clock. If not provided, the default height will be 50.
        text_color : str, optional
            The color of the clock's text. Must be a key in the COLOR_MAP. Default is "black".
        border_color : str, optional
            The color of the clock's border. Must be a key in the COLOR_MAP. Default is "black".
        bg_color : str, optional
            The background color of the clock. Must be a key in the COLOR_MAP. Default is "darkGray".

        Attributes
        ----------
        rect : pygame.Rect
            The rectangle representing the clock's position and size on the screen.
        text_rgb : tuple[int, int, int]
            RGB values representing the text color of the clock.
        border_rgb : tuple[int, int, int]
            RGB values representing the border color of the clock.
        bg_rgb : tuple[int, int, int]
            RGB values representing the background color of the clock.
        font : pygame.font.Font
            Font object used to render the clock's text.
        """
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
        """
        Renders the current time on the given Pygame screen.

        The time is displayed in the format '%I:%M:%S %p'. The method also handles the rendering of the clock's background
        and border colors based on the instance's attributes.

        Parameters
        ----------
        screen : pygame.Surface
            The Pygame screen on which the clock is rendered.

        """
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
        """
        Updates the position of the Clock by the given deltas.

        Parameters
        ----------
        dx : int
            The change in x-coordinate.
        dy : int
            The change in y-coordinate.
        """
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

    def resize(self, new_width, new_height):
        """
        Resizes the Clock to the given width and height.

        Parameters
        ----------
        new_width : int
            The new width for the Clock.
        new_height : int
            The new height for the Clock.
        """
        self.set_size(new_width, new_height)  # Use the base class's method

    def serialize(self):
        """
        Serializes the Clock instance into a dictionary for saving its state.

        Returns
        -------
        dict
            Dictionary containing the serialized Clock data.
        """
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
        """
        Creates a Clock instance from serialized data.

        Parameters
        ----------
        data : dict
            Dictionary containing serialized Clock data.

        Returns
        -------
        Clock
            A Clock instance constructed from the serialized data.
        """
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
