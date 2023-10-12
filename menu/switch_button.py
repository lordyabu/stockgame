import pygame
from utils.uiux import UIElement
class SwitchButton(UIElement):
    """
    A class representing a toggle (switch) button in a Pygame screen.

    Attributes:
        rect (pygame.Rect): The rectangle object representing the button's position and size.
        is_on (bool): Represents whether the button is currently in the 'on' state.
        text_on (str): The label text for the button when it's in the 'on' state.
        text_off (str): The label text for the button when it's in the 'off' state.

    Methods:
        toggle(): Toggle the button's state between 'on' and 'off'.
        display(screen): Display the button on the given Pygame screen.
        serialize(): Returns a dictionary containing the serialized state of the button.

    Example:
        button = SwitchButton(10, 10, 100, 50)
        button.toggle()
        button.display(screen)
    """
    def __init__(self, x, y, width, height, text_on="Locked", text_off="Unlocked"):
        """
        Initialize a SwitchButton instance.

        Args:
            x (int): The x-coordinate of the button's top left corner.
            y (int): The y-coordinate of the button's top left corner.
            width (int): The width of the button.
            height (int): The height of the button.
            text_on (str, optional): The label text for the button when it's in the 'on' state. Default is "Locked".
            text_off (str, optional): The label text for the button when it's in the 'off' state. Default is "Unlocked".
        """
        super().__init__(x, y)
        self.rect = pygame.Rect(x, y, width, height)
        self.is_on = False  # By default, it's off
        self.text_on = text_on
        self.text_off = text_off
        self.font = pygame.font.SysFont('arial', 16)

    def toggle(self):
        """
        Toggle the button's state between 'on' and 'off'.

        Returns:
            bool: The new state of the button after toggling.
        """
        self.is_on = not self.is_on
        return self.is_on

    def display(self, screen):
        """
        Display the button on a Pygame screen.

        Args:
            screen (pygame.Surface): The Pygame surface where the button will be displayed.
        """
        color = (100, 255, 100) if self.is_on else (255, 100, 100)  # Green if on, red if off

        # Create a new surface for the button with alpha transparency
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Draw the button background onto the button_surface with desired transparency
        pygame.draw.rect(button_surface, color + (128,), (0, 5, self.rect.width, self.rect.height - 10))
        pygame.draw.rect(button_surface, color + (128,), (5, 0, self.rect.width - 10, self.rect.height))
        pygame.draw.circle(button_surface, color + (128,), (5, 5), 5)
        pygame.draw.circle(button_surface, color + (128,), (self.rect.width - 5, 5), 5)
        pygame.draw.circle(button_surface, color + (128,), (5, self.rect.height - 5), 5)
        pygame.draw.circle(button_surface, color + (128,), (self.rect.width - 5, self.rect.height - 5), 5)

        # Render the text with black color
        text_surface = self.font.render(self.text_on if self.is_on else self.text_off, True, (0, 0, 0))
        text_x = (self.rect.width - text_surface.get_width()) // 2
        text_y = (self.rect.height - text_surface.get_height()) // 2
        button_surface.blit(text_surface, (text_x, text_y))

        # Blit the transparent button surface onto the main screen
        screen.blit(button_surface, (self.rect.x, self.rect.y))

    def serialize(self):
        data = super().serialize()  # Get base class serialization data
        data.update({
            "type": "SwitchButton",
            "width": self.rect.width,
            "height": self.rect.height,
            "is_on": self.is_on,
            "text_on": self.text_on,
            "text_off": self.text_off
        })
        return data

    @staticmethod
    def deserialize(data):
        """
        Create a SwitchButton instance from serialized data.

        Args:
            data (dict): The serialized state of the button.

        Returns:
            SwitchButton: A new instance of SwitchButton constructed from the serialized data.
        """
        switch_button = SwitchButton(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            text_on=data.get("text_on", "Locked"),  # Default to "Locked" if not present
            text_off=data.get("text_off", "Unlocked")  # Default to "Unlocked" if not present
        )
        switch_button.is_on = data.get("is_on", False)  # Default to off (False) if not present
        return switch_button