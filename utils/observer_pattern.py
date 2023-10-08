class Observer:
    def update(self, value):
        pass



class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, value):
        for observer in self._observers:
            observer.update(value)
