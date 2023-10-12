class Strategy:
    """
    A class for managing and retrieving trading signal string representations.

    Attributes:
        mapping (dict): A dictionary mapping integer signal values to string representations.

    Methods:
        add_mapping(val, string): Add a new value to string mapping.
        get_string(val): Retrieve the string associated with the given value.
        get_signal_display_info(signal): Get color and label information for a given signal.
        __str__(): Return a string representation of the mapping dictionary.

    Example:
        strategy_instance = Strategy()
        strategy_instance.add_mapping(3, 'custom_signal')
        signal_string = strategy_instance.get_string(3)
        color, label = strategy_instance.get_signal_display_info(signal_string)
        print(signal_string, color, label)
    """

    def __init__(self):
        """
        Initialize a Strategy instance with an initial mapping.

        The initial mapping includes the following predefined values:
        - 1: 'buy'
        - 2: 'end_buy'
        - -1: 'short'
        - -2: 'end_short'
        """
        self.mapping = {1: 'buy', 2: 'end_buy', -1: 'short', -2: 'end_short'}

    def add_mapping(self, val, string):
        """
        Add a new value to string mapping.

        Args:
            val (int): The integer value to map to a string.
            string (str): The string representation associated with the value.
        """
        self.mapping[val] = string

    def get_string(self, val):
        """
        Retrieve the string associated with the given value.

        Args:
            val (int): The integer value to look up.

        Returns:
            str: The string representation associated with the value. Returns "Value not found" if not found.
        """
        return self.mapping.get(val, "Value not found")

    def get_signal_display_info(self, signal):
        """
        Get color and label information for a given signal.

        Args:
            signal (int): The signal value to retrieve information for.

        Returns:
            tuple: A tuple containing color information (RGB tuple) and label information (string).
                   Returns (None, None) if the signal is None or not found in the mapping.
        """
        if signal is None:
            return None, None

        signal_string = self.get_string(signal)
        color = None
        label = None

        if signal_string == 'buy':
            color = (0, 255, 50)  # Green for buy
            label = "Buy"
        elif signal_string == 'end_buy':
            color = (255, 255, 50)  # Yellow for end_buy
            label = "End Buy"
        elif signal_string == 'short':
            color = (255, 50, 0)  # Red for sell
            label = "Short"
        elif signal_string == 'end_short':
            color = (255, 255, 255)  # White for end_short
            label = "End Short"

        return color, label

    def __str__(self):
        """
        Return a string representation of the mapping dictionary.

        Returns:
            str: A string representation of the mapping dictionary.
        """
        return str(self.mapping)
