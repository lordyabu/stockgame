class Label:
    def __init__(self, font, text, color, position, anchor="topleft"):
        self.image = font.render(text, 1, color)
        self.rect = self.image.get_rect()
        setattr(self.rect, anchor, position)
        # print(self.rect)  <-- Remove or comment out this line

    def draw(self, surface):
        surface.blit(self.image, self.rect)
