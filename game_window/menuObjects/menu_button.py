import pygame

class MenuButton:
    def __init__(self, x, y, width, height, text="Menu"):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def display(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)  # Drawing a gray button
        text_surf = self.font.render(self.text, True, (0, 0, 0))  # Black text
        screen.blit(text_surf, (self.x + 10, self.y + 5))  # Adjust the x and y values as needed

    def update_position(self, dx, dy):
        # In case you want to move the button around:
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
