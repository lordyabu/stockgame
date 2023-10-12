import pygame
from utils.uiux import UIElement

class MenuButton(UIElement):
    """
    A class for creating a menu button in a Pygame screen.

    Attributes:
        width (int): The width of the button.
        height (int): The height of the button.
        text (str): The text displayed on the button.
        font (pygame.font.Font): The font used for rendering the text.
        rect (pygame.Rect): The rectangle area of the button.
        active_color (tuple): The color of the button when active (hovered/clicked).
        passive_color (tuple): The default color of the button.
        color (tuple): The current color of the button.

    Methods:
        display(screen): Display the button on the Pygame screen.
        handle_events(event): Handle Pygame events for the button.
        hover(): Change the button color when hovered.
        update_position(dx, dy): Update the button's position by given deltas.
        serialize(): Convert the button object into a serializable dictionary.

    Example:
        button = MenuButton(100, 100, 120, 40, text="Start")
        button.display(screen)
    """

    def __init__(self, x, y, width, height, text="Menu"):
        """
        Initialize a MenuButton instance.

        Args:
            x (int): The x-coordinate position of the button.
            y (int): The y-coordinate position of the button.
            width (int): The width of the button.
            height (int): The height of the button.
            text (str): The text displayed on the button (default is "Menu").
        """
        super().__init__(x, y)
        self.width, self.height = width, height
        self.text = text
        self.font = pygame.font.SysFont('Arial', 16)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active_color = (60, 60, 60)  # Slightly brighter color for hover/click
        self.passive_color = (100, 100, 100)  # Default color
        self.color = self.passive_color  # Current color

    def display(self, screen):
        """
        Display the button on the Pygame screen.

        Args:
            screen (pygame.Surface): The Pygame surface where the button will be displayed.
        """
        # Create a new surface for the button with alpha transparency
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Draw the button background onto the button_surface with desired transparency
        pygame.draw.rect(button_surface, self.color + (128,), (0, 5, self.rect.width, self.rect.height - 10))
        pygame.draw.rect(button_surface, self.color + (128,), (5, 0, self.rect.width - 10, self.rect.height))
        pygame.draw.circle(button_surface, self.color + (128,), (5, 5), 5)
        pygame.draw.circle(button_surface, self.color + (128,), (self.rect.width - 5, 5), 5)
        pygame.draw.circle(button_surface, self.color + (128,), (5, self.rect.height - 5), 5)
        pygame.draw.circle(button_surface, self.color + (128,), (self.rect.width - 5, self.rect.height - 5), 5)

        # Render the text with white color
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_x = (self.rect.width - text_surf.get_width()) // 2
        text_y = (self.rect.height - text_surf.get_height()) // 2
        button_surface.blit(text_surf, (text_x, text_y))

        # Blit the transparent button surface onto the main screen
        screen.blit(button_surface, (self.rect.x, self.rect.y))

    def handle_events(self, event):
        """
        Handle Pygame events for the button.

        Args:
            event (pygame.event.Event): The Pygame event to handle.
        """
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.active_color
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pass
        else:
            self.color = self.passive_color

    def hover(self):
        """
        Change the button color when hovered.
        """
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.active_color
        else:
            self.color = self.passive_color

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
        Convert the button object into a serializable dictionary.

        Returns:
            dict: A dictionary containing serialized data of the button.
        """
        data = super().serialize()  # Get base class serialization data
        data.update({
            "type": "MenuButton",
            "width": self.rect.width,
            "height": self.rect.height,
            "text": self.text
        })
        return data

    @staticmethod
    def deserialize(data):
        """
        Create a MenuButton instance from serialized data.

        Args:
            data (dict): The serialized state of the button.

        Returns:
            MenuButton: A new instance of MenuButton constructed from the serialized data.
        """
        return MenuButton(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            text=data["text"]
        )
