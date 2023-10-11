import pygame

class TextButton:
    def __init__(self, x, y, text, font, color, action=None):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color
        self.action = action
        self.rect = pygame.Rect(self.x, self.y, *self.font.size(self.text))

    def display(self, screen):
        text_surf = self.font.render(self.text, True, self.color)
        # Inside TextButton's display or draw method:
        screen.blit(text_surf, (self.rect.x, self.rect.y))  # use text_surf here

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                self.action()

    def update_position(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
