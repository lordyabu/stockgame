import pygame

class SwitchButton:
    def __init__(self, x, y, width, height, text_on="Locked", text_off="Unlocked"):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_on = False  # By default, it's off
        self.text_on = text_on
        self.text_off = text_off

    def toggle(self):
        self.is_on = not self.is_on

    def display(self, screen):
        color = (100, 255, 100) if self.is_on else (255, 100, 100)  # Green if on, red if off
        pygame.draw.rect(screen, color, self.rect)
        font = pygame.font.Font(None, 36)
        text = self.text_on if self.is_on else self.text_off
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
