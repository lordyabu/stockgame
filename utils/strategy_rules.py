class Strategy:
    def __init__(self):
        self.mapping = {1 : 'buy',
                        2 : 'end_buy',
                        -1: 'short',
                        -2: 'end_short'}

    def add_mapping(self, val, string):
        """Add a new value to string mapping."""
        self.mapping[val] = string

    def get_string(self, val):
        """Retrieve the string associated with the given value."""
        return self.mapping.get(val, "Value not found")


    def get_signal_display_info(self, signal):
        if signal is None:
            return None, None

        signal_string = self.get_string(signal)
        color = None
        label = None

        if signal_string == 'buy':
            color = (0, 255, 50)  # Green for buy
            label = "Buy"
        elif signal_string == 'end_buy':
            color = (0, 255, 50)  # Yellow for end_buy
            label = "End Buy"
        elif signal_string == 'short':
            color = (255, 50, 0)  # Red for sell
            label = "Short"
        elif signal_string == 'end_short':
            color = (255, 50, 0)  # White for end_short
            label = "End Short"

        return color, label

    def __str__(self):
        return str(self.mapping)