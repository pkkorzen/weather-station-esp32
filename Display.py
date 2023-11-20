import sh1106
from sh1106_setup import setup
from writer import Writer
import freesans24

class Display():

    SCREENS = {
    0: ["Temp zew", "Temp wew", None, None],
    1: ["Wilg zew", "Wilg wew", None, None],
    2: ["Cisn zew", "Cisn wew", None, None],
    3: ["European air quality index", "PMS_1.0", None, None],
    4: ["PMS_2.5", "PMS_10.0", None, None],
    5: ["SHT_30_Temp", "SHT_30_Hum", None, None]
    }

    def __init__(self):
        self.oled = setup(False, False)
        self.oled.flip()

        self.writer = Writer(self.oled, freesans24, verbose=False)
    
    def display(self, screen_number):
        self.oled.fill(0)
        #First half of the screen - outside readings
        self.oled.text(self.SCREENS[screen_number][0], 0, 0)
        self.writer.set_textpos(self.oled, 8, 0)
        self.writer.printstring(self.SCREENS[screen_number][2])
    
        #Second half of the screen - inside readings
        self.oled.fill_rect(0, 28, 72, 8, 1)
        self.oled.text(self.SCREENS[screen_number][1], 0, 28, 0)
        self.writer.set_textpos(self.oled, 36, 0)
        self.writer.printstring(self.SCREENS[screen_number][3], True)

        self.oled.show()
    
    def set_readings(self, readings):
        self.SCREENS[0][2] = readings[0][0]
        self.SCREENS[2][2] = readings[0][1]
        self.SCREENS[1][2] = readings[0][2]
        self.SCREENS[0][3] = readings[1][0]
        self.SCREENS[2][3] = readings[1][1]
        self.SCREENS[1][3] = readings[1][2]
        self.SCREENS[3][2] = readings[3]
        self.SCREENS[3][3] = readings[2][0]
        self.SCREENS[4][2] = readings[2][1]
        self.SCREENS[4][3] = readings[2][2]
        self.SCREENS[5][2] = readings[4][0]
        self.SCREENS[5][3] = readings[4][1]

        