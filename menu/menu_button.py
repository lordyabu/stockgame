import pygame

class MenuButton:
    """
    A class representing a button with a label in a Pygame screen.

    Attributes:
        x (int): The x-coordinate of the button's top left corner.
        y (int): The y-coordinate of the button's top left corner.
        width (int): The width of the button.
        height (int): The height of the button.
        text (str): The label text for the button. Default is "Menu".
        font (pygame.font.Font): The font used for rendering the button's text.
        rect (pygame.Rect): The rectangle object representing the button's position and size.

    Methods:
        display(screen): Displays the button on the given Pygame screen.
        update_position(dx, dy): Updates the button's position by a given delta.
        serialize(): Returns a dictionary containing the serialized state of the button.

    Example:
        button = MenuButton(10, 10, 100, 50, "Start")
        button.display(screen)
    """
    def __init__(self, x, y, width, height, text="Menu"):
        """
        Initialize a MenuButton instance.

        Args:
            x (int): The x-coordinate of the button's top left corner.
            y (int): The y-coordinate of the button's top left corner.
            width (int): The width of the button.
            height (int): The height of the button.
            text (str, optional): The label text for the button. Default is "Menu".
        """
        self.x, self.y, self.width, self.height = x, y, width, height
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def display(self, screen):
        """
        Display the button on a Pygame screen.

        Args:
            screen (pygame.Surface): The Pygame surface where the button will be displayed.
        """
        pygame.draw.rect(screen, (100, 100, 100), self.rect)  # Drawing a gray button

        text_surf = self.font.render(self.text, True, (0, 0, 0))  # Black text

        # Compute position relative to the rect's position
        text_x = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2

        screen.blit(text_surf, (text_x, text_y))

    def update_position(self, dx, dy):
        """
        Update the button's position by given deltas.

        Args:
            dx (int): The delta x to change the button's x-coordinate.
            dy (int): The delta y to change the button's y-coordinate.
        """
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)



    def serialize(self):
        """
        Serialize the state of the button into a dictionary.

        Returns:
            dict: A dictionary containing the serialized state of the button.
        """
        return {
            "type": "MenuButton",
            "x": self.rect.x,
            "y": self.rect.y,
            "width": self.rect.width,
            "height": self.rect.height,
            "text": self.text
        }