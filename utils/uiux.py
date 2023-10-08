class UIElement:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def display(self, screen):
        """Display the UI element on the screen."""
        pass

    def handle_event(self, event):
        """Handle Pygame events for the UI element."""
        pass

    def update_position(self, dx, dy):
        """Update the position of the UI element."""
        self.x += dx
        self.y += dy

    def serialize(self):
        """Serialize the state of the UI element into a dictionary."""
        return {
            'type': self.__class__.__name__,
            'x': self.x,
            'y': self.y
        }

    @staticmethod
    def deserialize(data):
        """Create an instance of a UI element from serialized data."""
        # This method is more of a placeholder. Actual deserialization logic will be in subclasses.
        pass