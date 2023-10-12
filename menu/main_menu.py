import pygame
from menu.switch_button import SwitchButton
from menu.menu_button import MenuButton
from utils.uiux import UIElement

class Menu(UIElement):
    """
    A class for creating an interactive menu in a Pygame screen.

    Attributes:
        rect (pygame.Rect): The rectangle area of the menu.
        is_active (bool): Whether the menu is currently active.
        lock_button (SwitchButton): A button to lock the menu.
        save_button (MenuButton): A button to save the current state.
        load_button (MenuButton): A button to load a saved state.

    Methods:
        toggle(): Toggles the visibility of the menu.
        display(screen): Display the menu on the Pygame screen.
        update_position(x, y): Update the menu's position.
        serialize(): Convert the menu object into a serializable dictionary.
        update_position_from_button(menu_button_x, menu_button_y, menu_button_height): Update the menu's position based on a MenuButton's position.
    """

    def __init__(self, x, y):
        """
        Initialize a Menu instance.

        Args:
            x (int): The x-coordinate position of the menu.
            y (int): The y-coordinate position of the menu.
        """
        super().__init__(x, y)
        self.rect = pygame.Rect(self.x, self.y, 100, 200)
        self.is_active = False
        self.lock_button = SwitchButton(self.x + 10, self.y + 10, 80, 40)
        self.save_button = MenuButton(self.x + 10, self.y + 60, 80, 40, text="Save")
        self.load_button = MenuButton(self.x + 10, self.y + 110, 80, 40, text="Load")

    def update_position(self, x, y):
        """
        Update the menu's position.

        Args:
            x (int): The new x-coordinate position of the menu.
            y (int): The new y-coordinate position of the menu.
        """
        self.rect.topleft = (x, y)
        self.lock_button.rect.topleft = (x + 10, y + 10)
        self.save_button.rect.topleft = (x + 10, y + 60)
        self.load_button.rect.topleft = (x + 10, y + 110)

    def display(self, screen):
        """
        Display the menu on the Pygame screen.

        Args:
            screen (pygame.Surface): The Pygame surface where the menu will be displayed.
        """
        if not self.is_active:
            return
        menu_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, (200, 200, 200, 50), (0, 0, self.rect.width, self.rect.height))
        self.lock_button.display(screen)
        self.save_button.display(screen)
        self.load_button.display(screen)

    def toggle(self):
        """
        Toggle the visibility of the menu.

        Returns:
            bool: The new visibility state of the menu.
        """
        self.is_active = not self.is_active

    def serialize(self):
        """
        Convert the menu object into a serializable dictionary.

        Returns:
            dict: A dictionary containing serialized data of the menu.
        """
        data = super().serialize()
        data.update({
            "type": "Menu",
            "is_active": self.is_active,
            "children": [self.lock_button.serialize(), self.save_button.serialize(), self.load_button.serialize()]
        })
        return data

    def update_position_from_button(self, menu_button_x, menu_button_y, menu_button_height):
        """
        Update the menu's position based on a MenuButton's position.

        Args:
            menu_button_x (int): The x-coordinate position of the MenuButton.
            menu_button_y (int): The y-coordinate position of the MenuButton.
            menu_button_height (int): The height of the MenuButton.
        """
        self.rect.topleft = (menu_button_x, menu_button_y + menu_button_height)

    @staticmethod
    def deserialize(data):
        """
        Create a Menu instance from serialized data.

        Args:
            data (dict): The serialized state of the menu.

        Returns:
            Menu: A new instance of Menu constructed from the serialized data.
        """
        menu = Menu(data["x"], data["y"])
        menu.is_active = data.get("is_active", False)
        return menu
