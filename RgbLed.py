import time
from machine import Pin,PWM
 
#RGB
RED = 0
GREEN = 1
BLUE = 2

class RgbLed:

    colors = {
        0: (0, 255, 255), 
        1: (0, 255, 0), 
        2: (255, 255, 0), 
        3: (153, 0, 51), 
        4: (255, 0, 0), 
        5: (0, 0, 255)
        }

    def __init__(self, pwm_pins=[25,27,26]):
        self.pwm_pins = pwm_pins
        # Setup pins for PWM
        self.pwms = [PWM(Pin(self.pwm_pins[RED])),PWM(Pin(self.pwm_pins[GREEN])),
                    PWM(Pin(self.pwm_pins[BLUE]))]
        # Set pwm frequency
        [pwm.freq(1000) for pwm in self.pwms]

    def map_range(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def turn_off_rgb(self):
        self.pwms[RED].duty_u16(0)
        self.pwms[GREEN].duty_u16(0)
        self.pwms[BLUE].duty_u16(0)
        time.sleep(0.1)
    
    # Deinitialize PWM on all pins
    def deinit_pwm_pins(self):
        self.pwms[RED].deinit()
        self.pwms[GREEN].deinit()
        self.pwms[BLUE].deinit()
        
    def light_LED(self, air_quality_index):
        self.turn_off_rgb()
        red, green, blue = RgbLed.colors[air_quality_index]
        
        self.pwms[RED].duty_u16(self.map_range(red, 0, 255, 0, 65535))
        self.pwms[GREEN].duty_u16(self.map_range(green, 0, 255, 0, 65535))
        self.pwms[BLUE].duty_u16(self.map_range(blue, 0, 255, 0, 65535))