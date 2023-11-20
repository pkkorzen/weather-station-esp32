from machine import Pin

class Button:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)

    def irq(self, handler, trigger):
        self.pin.irq(handler = handler, trigger = trigger)