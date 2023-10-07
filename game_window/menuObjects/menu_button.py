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

        # Compute position relative to the rect's position
        text_x = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2

        screen.blit(text_surf, (text_x, text_y))

    def update_position(self, dx, dy):
        # In case you want to move the button around:
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)



    def serialize(self):
        return {
            "type": "MenuButton",
            "x": self.rect.x,
            "y": self.rect.y,
            "width": self.rect.width,
            "height": self.rect.height,
            "text": self.text
        }