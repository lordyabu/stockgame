class Strategy:
    def __init__(self):
        self.mapping = {1 : 'buy',
                        2 : 'end buy',
                        -1: 'short',
                        -2: 'end short'}

    def add_mapping(self, val, string):
        """Add a new value to string mapping."""
        self.mapping[val] = string

    def get_string(self, val):
        """Retrieve the string associated with the given value."""
        return self.mapping.get(val, "Value not found")

    def __str__(self):
        return str(self.mapping)