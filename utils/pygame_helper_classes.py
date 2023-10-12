class Label:
    """
    A class for rendering and displaying text labels on a Pygame surface.

    Attributes:
        image (pygame.Surface): The rendered text image.
        rect (pygame.Rect): The rectangle representing the label's position and size.

    Methods:
        draw(surface): Draw the label on a Pygame surface.

    Example:
        font = pygame.font.SysFont('Arial', 16)
        label_instance = Label(font, "Hello, World!", (255, 255, 255), (100, 100), anchor="topleft")
        label_instance.draw(screen)
    """

    def __init__(self, font, text, color, position, anchor="topleft"):
        """
        Initialize a Label instance with the specified text, font, color, position, and anchor.

        Args:
            font (pygame.font.Font): The font used for rendering the text.
            text (str): The text content of the label.
            color (tuple): The RGB color tuple for the text.
            position (tuple): The (x, y) coordinates of the label's position.
            anchor (str, optional): The anchor point for positioning the label. Default is "topleft".

        Returns:
            Label: A Label instance.
        """
        self.image = font.render(text, 1, color)
        self.rect = self.image.get_rect()
        setattr(self.rect, anchor, position)

    def draw(self, surface):
        """
        Draw the label on a Pygame surface.

        Args:
            surface (pygame.Surface): The Pygame surface on which to draw the label.
        """
        surface.blit(self.image, self.rect)
