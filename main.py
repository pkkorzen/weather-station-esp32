from Display import Display
from WifiConnection import WifiConnection
from time import sleep
import machine
import program
import senko
import file_config

wifi_connection = WifiConnection()
wifi_connection.connect_wifi()
display = Display()
updates_available = False

def show_checking_update_information():
    clear_screen()
    display.oled.text("Checking updates...", 0, 0)
    show_text()

def show_available_update_information():
    clear_screen()
    display.oled.text("Update available", 0, 0)
    display.oled.text("Downloading", 0, 8)
    display.oled.text("update... ", 0, 16)
    show_text()

def show_reboot_information():
    clear_screen()
    display.oled.text("Updated to the", 0, 0)
    display.oled.text("latest version!", 0, 8)
    display.oled.text("Rebooting... ", 0, 16)
    show_text()
    
def show_starting_information():
    clear_screen()
    display.oled.text("Soft up-to-date!", 0, 0)
    display.oled.text("Launching", 0, 8)
    display.oled.text("the station... ", 0, 16)
    show_text()

def clear_screen():
    display.oled.fill(0)

def show_text():
    display.oled.show()

OTA = senko.Senko(user="pkkorzen", repo="weather-station-esp32", files=file_config.files)
#needs to check updates after reboot in case a new file, that was not present before,
#has been added to file_config.files during an update
show_checking_update_information()
if OTA.fetch():
    show_available_update_information()
    sleep(1)

    OTA.update()

    show_reboot_information()
    machine.reset()

if not updates_available:
    show_starting_information()
    updates_available = program.run(updates_available, display, OTA)

if updates_available:
    show_available_update_information()
    sleep(1)

    OTA.update()

    show_reboot_information()
    machine.reset()