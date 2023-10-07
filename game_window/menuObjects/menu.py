import pygame
from menuObjects.switch_button import SwitchButton

class Menu:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 200)  # adjust as necessary
        self.is_active = False
        self.lock_button = SwitchButton(x + 10, y + 10, 80, 40)

    def display(self, screen):
        if not self.is_active:
            return
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        self.lock_button.display(screen)

    def toggle(self):
        self.is_active = not self.is_active

