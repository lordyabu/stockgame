import pygame

class Button:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, 130, 30)  # Adjust button size as needed

        self.font = pygame.font.SysFont('Arial', 16)

    def display(self, screen, highlighted=False):
        button_color = (0, 255, 0) if highlighted else (0, 200, 0)
        text_color = (255, 255, 255) if highlighted else (0, 0, 0)

        pygame.draw.rect(screen, button_color, self.rect)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)