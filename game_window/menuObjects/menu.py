import pygame
from menuObjects.switch_button import SwitchButton
from menuObjects.menu_button import MenuButton

class Menu:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 200)
        self.is_active = False
        self.lock_button = SwitchButton(x + 10, y + 10, 80, 40)
        self.save_button = MenuButton(x + 10, y + 60, 80, 40, text="Save")
        self.load_button = MenuButton(x + 10, y + 110, 80, 40, text="Load")


    def update_position(self, x, y):
        # Set the new position for the menu
        self.rect.topleft = (x, y)
        # Update positions of contained elements accordingly
        self.lock_button.rect.topleft = (x + 10, y + 10)
        self.save_button.rect.topleft = (x + 10, y + 60)
        self.load_button.rect.topleft = (x + 10, y + 110)

    def display(self, screen):
        if not self.is_active:
            return
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        self.lock_button.display(screen)
        self.save_button.display(screen)
        self.load_button.display(screen)

    def toggle(self):
        self.is_active = not self.is_active


    def serialize(self):
        # For this example, I'm saving the x, y, and active state of the Menu.
        # Add any other attributes you think are necessary to save and recreate the Menu's state.
        return {
            "type": "Menu",
            "x": self.rect.x,
            "y": self.rect.y,
            "is_active": self.is_active
        }


    def serialize(self):
        return {
            "type": "Menu",
            "x": self.rect.x,
            "y": self.rect.y,
            "is_active": self.is_active,
            "children": [self.lock_button.serialize(), self.save_button.serialize(), self.load_button.serialize()]
        }