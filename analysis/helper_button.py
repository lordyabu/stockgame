import pygame

class Button:
    """
    Represents a rectangular button UI element in Pygame.

    Attributes
    ----------
    x : int
        x-coordinate of the top-left corner of the button.
    y : int
        y-coordinate of the top-left corner of the button.
    text : str
        The label/text displayed on the button.
    rect : pygame.Rect
        The rectangle representing the button's position and dimensions.
    font : pygame.font.Font
        Font object used to render the button's text.

    Methods
    -------
    display(screen, highlighted=False)
        Renders the button onto the given screen.
    """

    def __init__(self, x, y, text):
        """
        Initialize a Button instance.

        Parameters
        ----------
        x : int
            x-coordinate of the top-left corner of the button.
        y : int
            y-coordinate of the top-left corner of the button.
        text : str
            The label/text displayed on the button.
        """
        self.x = x
        self.y = y
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, 130, 30)  # Adjust button size as needed

        self.font = pygame.font.SysFont('Arial', 16)

    def display(self, screen, highlighted=False):
        """
        Renders the button onto the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The Pygame screen to render the button on.
        highlighted : bool, optional
            If True, the button will be displayed in a highlighted color scheme, default is False.
        """
        button_color = (0, 255, 0) if highlighted else (0, 200, 0)
        text_color = (255, 255, 255) if highlighted else (0, 0, 0)

        pygame.draw.rect(screen, button_color, self.rect)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)