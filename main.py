import Button
import Display
import IFTTT
import Reading
import RgbLed
import WebServer
import WifiConnection
from time import sleep, time

import gc
gc.collect()

reading = Reading()
#setting alert limits
reading.sht30_sensor.write_high_alert_limit(98.5, 69.0)
reading.sht30_sensor.write_high_alert_limit_clear(99.0, 65.0)
display = Display()
ifttt = IFTTT()
rgb_led = RgbLed()
web_server = WebServer()
wifi_connection = WifiConnection()
backward_button = Button(17)
forward_button = Button(18)

def initialise_air_quality_readings():
    initialization_counter = 0
    seconds_counter = 30
    while seconds_counter > 0:
        display.oled.fill(0)
        display.oled.text("Air quality readings initialisation starts in " + seconds_counter + " seconds.", 0, 0)
        display.oled.show()
        sleep(1)

    display.oled.fill(0)
    display.oled.text("Air quality readings initialisation in progress...", 0, 0)
    display.oled.show()
    for x in range(reading.measurements_per_hour):
        reading.add_air_quality_readings_to_periodic_lists(initialization_counter)
        initialization_counter += 1
        display.oled.fill(0)
        display.oled.text("Air quality readings initialisation in progress..." + (100 / reading.measurements_per_hour * (initialization_counter + 1)) + " %", 0, 0)
        display.oled.show()
        sleep(3)
    reading.pms7003.sleep()
    display.oled.fill(0)


def next_screen(irq) :
    global screen_number
    if screen_number == len(display.SCREENS) - 1:
        screen_number = 0
    else:
        screen_number += 1
    
def previous_screen(irq) :
    global screen_number
    if screen_number == 0:
        screen_number = len(display.SCREENS) - 1
    else:
        screen_number -= 1


#initialize air quality readings
initialise_air_quality_readings()

sleep_period_start = time() - 810
measurement_counter = 0
measurement_period_start = 0
screen_number = 0

#connect to wifi
wifi_connection.connect_wifi()
#open socket
web_server.open_socket()

while True:
    #catching button clicks
    backward_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = previous_screen)
    forward_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = next_screen)

    if time() - sleep_period_start >= 810:
        reading.pms7003.wakeUp()
        measurement_period_start = time()
        sleep_period_start = measurement_period_start
    
    if measurement_period_start > 0 and time() - measurement_period_start > 90:
        reading.add_air_quality_readings_to_periodic_lists(measurement_counter)
        #send readings to google sheets using IFTTT
        ifttt.make_ifttt_request(reading.get_all_readings())
        if measurement_counter == reading.measurements_per_hour - 1:
            measurement_counter = 0
        else:
            measurement_counter += 1
        
        reading.pms7003.sleep()
        measurement_period_start = 0
        sleep_period_start = time()
    
    readings = reading.get_all_readings()
    #display readings on OLED
    display.set_readings(readings)
    display.display(screen_number)
    
    try:
        if gc.mem_free() < 102000:
            gc.collect()
        web_server.serve(readings)
        rgb_led.light_LED(readings[3])
    except KeyboardInterrupt:
        rgb_led.deinit_pwm_pins()
        machine.reset()
    sleep(1)