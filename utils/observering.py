class Observer:
    """
    An abstract base class for observers that can receive updates from observables.

    Subclasses must implement the `update` method.

    Methods:
        update(value): Called by the observable to update the observer with a new value.

    Example:
        class MyObserver(Observer):
            def update(self, value):
                # Implement the update method to handle value updates.
                pass
    """

    def update(self, value):
        """
        Update the observer with a new value.

        Args:
            value: The new value received from the observable.
        """
        pass


class Observable:
    """
    A class representing an observable object that can notify its observers.

    Attributes:
        _observers (list): A list of observers subscribed to this observable.

    Methods:
        add_observer(observer): Add an observer to the list of observers.
        remove_observer(observer): Remove an observer from the list of observers.
        notify_observers(value): Notify all observers with a new value.

    Example:
        observable = Observable()
        observer1 = MyObserver()
        observer2 = MyObserver()
        observable.add_observer(observer1)
        observable.add_observer(observer2)
        observable.notify_observers(42)
    """

    def __init__(self):
        """
        Initialize an observable object with an empty list of observers.
        """
        self._observers = []

    def add_observer(self, observer):
        """
        Add an observer to the list of observers.

        Args:
            observer: The observer object to be added.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """
        Remove an observer from the list of observers.

        Args:
            observer: The observer object to be removed.
        """
        self._observers.remove(observer)

    def notify_observers(self, value):
        """
        Notify all observers with a new value.

        Args:
            value: The new value to be sent to observers.
        """
        for observer in self._observers:
            observer.update(value)
