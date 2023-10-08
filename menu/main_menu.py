import pygame
from menu.switch_button import SwitchButton
from menu.menu_button import MenuButton

class Menu:
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
        serialize(): Convert the menu object into a serializable dictionary.
    """
    def __init__(self, x, y):
        """
        Initialize a Menu instance.

        Args:
            x (int): The x-coordinate position of the menu.
            y (int): The y-coordinate position of the menu.
        """
        self.rect = pygame.Rect(x, y, 100, 200)
        self.is_active = False
        self.lock_button = SwitchButton(x + 10, y + 10, 80, 40)
        self.save_button = MenuButton(x + 10, y + 60, 80, 40, text="Save")
        self.load_button = MenuButton(x + 10, y + 110, 80, 40, text="Load")


    def update_position(self, x, y):
        """
        Update the position of the menu and its contained elements.

        Args:
            x (int): The new x-coordinate position of the menu.
            y (int): The new y-coordinate position of the menu.
        """
        # Set the new position for the menu
        self.rect.topleft = (x, y)

        # Update positions of contained elements accordingly
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
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
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
        Serialize the state of the menu into a dictionary.

        Returns:
            dict: A dictionary containing the serialized state of the menu.
        """
        return {
            "type": "Menu",
            "x": self.rect.x,
            "y": self.rect.y,
            "is_active": self.is_active,
            "children": [self.lock_button.serialize(), self.save_button.serialize(), self.load_button.serialize()]
        }

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
        # Might do children here
        return menu