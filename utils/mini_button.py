import pygame

class TextButton:
    """
    A class representing a clickable text button in a Pygame window.

    Attributes:
        x (int): The x-coordinate position of the button.
        y (int): The y-coordinate position of the button.
        text (str): The text displayed on the button.
        font (pygame.font.Font): The font used for rendering the text.
        color (tuple): The color of the text (RGB tuple).
        alpha (int): The alpha value for transparency (0 to 255).
        action (function): The function to execute when the button is clicked.
        rect (pygame.Rect): The rectangular area of the button.

    Methods:
        display(screen): Display the button on the Pygame screen.
        handle_event(event): Handle mouse button clicks on the button.
        update_position(dx, dy): Update the button's position.

    Example:
        font = pygame.font.SysFont('Arial', 24)
        button = TextButton(100, 100, "Click Me", font, (255, 0, 0), action=handle_click)
        button.display(screen)
        button.handle_event(event)
        button.update_position(10, 0)
    """

    def __init__(self, x, y, text, font, color, action=None, alpha=255):
        """
        Initialize a TextButton.

        Args:
            x (int): The x-coordinate position of the button.
            y (int): The y-coordinate position of the button.
            text (str): The text displayed on the button.
            font (pygame.font.Font): The font used for rendering the text.
            color (tuple): The color of the text (RGB tuple).
            action (function, optional): The function to execute when the button is clicked.
            alpha (int, optional): The alpha value for transparency (0 to 255).
        """
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color
        self.alpha = alpha
        self.action = action
        self.rect = pygame.Rect(self.x, self.y, *self.font.size(self.text))

    def display(self, screen):
        """
        Display the button on the Pygame screen.

        Args:
            screen (pygame.Surface): The Pygame surface where the button will be displayed.
        """
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        screen.blit(text_surf, (self.rect.x, self.rect.y))

    def handle_event(self, event):
        """
        Handle mouse button clicks on the button.

        Args:
            event (pygame.event.Event): The Pygame event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                self.action()

    def update_position(self, dx, dy):
        """
        Update the button's position.

        Args:
            dx (int): The change in the x-coordinate position.
            dy (int): The change in the y-coordinate position.
        """
        self.rect.x += dx
        self.rect.y += dy
