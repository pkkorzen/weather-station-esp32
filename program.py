from Button import Button
from IFTTT import IFTTT
from CT8 import CT8
from Reading import Reading
from RgbLed import RgbLed
from ExceptionLogger import ExceptionLogger
from time import sleep, time
import machine
import sys
import uio
import os
from logToFile import logToFile

import gc
gc.collect()
reading = None
display = None
ifttt = None
ct8 = None
rgb_led = None
exception_logger = None

backward_button = None
forward_button = None

sleep_period_start = None

def initialise_objects(screen):
    global reading
    global display
    global ifttt
    global ct8
    global rgb_led
    global backward_button
    global forward_button
    global exception_logger
    global sleep_period_start

    reading = Reading()
    #setting alert limits
    #reading.sht30_sensor.write_high_alert_limit_set(98.5, 69.0)
    #reading.sht30_sensor.write_high_alert_limit_clear(99.0, 65.0)
    #set limits to disable heater since it probably broke
    reading.sht30_sensor.write_high_alert_limit_set(98.5, 10.0)
    reading.sht30_sensor.write_high_alert_limit_clear(99.0, 5.0)

    display = screen
    ifttt = IFTTT()
    ct8 = CT8()
    rgb_led = RgbLed()

    backward_button = Button(18)
    forward_button = Button(19)
    
    sleep_period_start = time() - 806

    exception_logger = ExceptionLogger()

def initialise_air_quality_readings():
    reading.pms7003.wakeup()
    initialization_counter = 0
    seconds_counter = 30
    while seconds_counter > 0:
        display.oled.fill(0)
        display.oled.text("Air quality ", 0, 0)
        display.oled.text("readings init ", 0, 8)
        display.oled.text("starts in ", 0, 16)
        display.oled.text(str(seconds_counter) + " seconds.", 0, 24)
        display.oled.show()
        seconds_counter -= 1
        sleep(1)

    display.oled.fill(0)
    display.oled.text("Air quality ", 0, 0)
    display.oled.text("readings init ", 0, 8)
    display.oled.text("in progress... ", 0, 16)
    display.oled.show()
    for x in range(reading.measurements_per_hour):
        reading.add_air_quality_readings_to_periodic_lists(initialization_counter)
        initialization_counter += 1
        display.oled.fill(0)
        display.oled.text("Air quality ", 0, 0)
        display.oled.text("readings init ", 0, 8)
        display.oled.text("in progress... ", 0, 16)
        display.oled.text(str((100 / reading.measurements_per_hour * (initialization_counter))) + " %", 0, 24)
        display.oled.show()
        sleep(3)
    reading.pms7003.sleep()
    sleep(1)
    display.oled.fill(0)
    display.oled.show()

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

measurement_counter = 0
measurement_period_start = 0
screen_number = 0
last_update_time = time()

eaqi_level_index_temp = None

def run(updates_available, display, OTA):
    os.dupterm(logToFile())
    try:
        initialise_objects(display)
        initialise_air_quality_readings()

        while not updates_available:
            updates_available = run_tasks(updates_available, OTA)
            if updates_available:
                return updates_available
            sleep(1)
    except Exception as e:
        buf = uio.StringIO()
        sys.print_exception(e, buf)
        traceback = buf.getvalue()
        print(traceback)
        exception_logger.log_exception(traceback)
        rgb_led.deinit_pwm_pins()
        machine.reset()

def check_for_updates(updates_available, OTA):
    try:
        updates_available = OTA.fetch()
        return updates_available
    except:
        print('unable to reach internet')
        return updates_available

def run_tasks(updates_available, OTA):
    global sleep_period_start
    global eaqi_level_index_temp
    global measurement_counter
    global measurement_period_start
    global screen_number
    global last_update_time

    backward_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = previous_screen)
    forward_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = next_screen)

    if time() - sleep_period_start >= 806:
        reading.pms7003.wakeup()
        measurement_period_start = time()
        sleep_period_start = measurement_period_start

    if measurement_period_start > 0 and time() - measurement_period_start > 90:
        reading.add_air_quality_readings_to_periodic_lists(measurement_counter)
        readings = reading.get_all_readings()
        ifttt.make_ifttt_request(readings)
        ct8.make_ct8_request(readings)
        if measurement_counter == reading.measurements_per_hour - 1:
            measurement_counter = 0
        else:
            measurement_counter += 1
        
        reading.pms7003.sleep()
        measurement_period_start = 0
        sleep_period_start = time()
        if time() - last_update_time > 21600: #6h update_time
            last_update_time = time()
            updates_available = check_for_updates(updates_available, OTA)

    readings = reading.get_all_readings()
    sleep(1)
    #display readings on OLED
    display.set_readings(readings)
    display.display(screen_number)
    
    if gc.mem_free() < 102000:
        gc.collect()

    eaqi_level_index = readings[3]
    if eaqi_level_index != eaqi_level_index_temp:
        rgb_led.light_LED(eaqi_level_index)
        eaqi_level_index_temp = eaqi_level_index
    return updates_available