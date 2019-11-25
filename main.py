import board
import gc
import time
from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

import adafruit_dotstar

gc.collect()  # make some rooooom
# HID keyboard support
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# BANK Constant variables
DEFAULT_BANK = 0;
BLUE_BANK = 1;
GREEN_BANK = 2;
YELLOW_BANK = 3;
RED_BANK = 4;

# how long it takes to register long press in seconds
LONG_PRESS_TIME = .55

# String template to output to the serial console
# Used for the PC script that can launch color box windows
MODE_ACTIVATED_TEMPLATE = "%s mode activated"

pressed_times = [-1, -1, -1, -1]
old_pin_states = [True, True, True, True]
button_pins = [board.D7, board.D9, board.D10, board.D11]
button_names = ["blue_btn", "green_btn", "yellow_btn", "red_btn"]
bank_list = [BLUE_BANK, GREEN_BANK, YELLOW_BANK, RED_BANK]
keycode_list = [Keycode.F11, Keycode.F10, Keycode.F9, Keycode.F8]
led_pins = [DigitalInOut(board.A3), DigitalInOut(board.A4), DigitalInOut(board.A5), DigitalInOut(board.A2)]

for pin in led_pins:
    pin.direction = Direction.OUTPUT
    
# used for color wheel function
wheel_i = 0



#################### Macro definition Functions ####################
# Add a function for each macro you want to use
def ctrl_shift_s():
    kbd.press(Keycode.CONTROL)
    kbd.press(Keycode.SHIFT)
    kbd.press(Keycode.S)
    kbd.release_all()


def ctrl_shift_e():
    kbd.press(Keycode.CONTROL)
    kbd.press(Keycode.SHIFT)
    kbd.press(Keycode.E)
    kbd.release_all()

def ctrl_shift_t():
    kbd.press(Keycode.CONTROL)
    kbd.press(Keycode.SHIFT)
    kbd.press(Keycode.T)
    kbd.release_all()
    
def ctrl_shift_w():
    kbd.press(Keycode.CONTROL)
    kbd.press(Keycode.SHIFT)
    kbd.press(Keycode.W)
    kbd.release_all()

def post_skeletron():
    keyboard_layout.write(
        'this is awesome because\nit works like this\nwhat makes it unique\nbenefit?\nopen?\nvideo?\nin-link\n')

def bio_skeletron():
    keyboard_layout.write(
        'How did this person contribute to science?\nDid they hack anything?\nWhat adversities did this person face?\nHow is their impact felt today?\nHow did their zeitgeist affect their work and the public perception of them or their work?\n'
)

def tip_thankyou():
    keyboard_layout.write(
        'Great build! Thanks for sending it in. I\'ve written a post that should appear on the blog some time in the next couple of days or so.\nHappy hacking!\n')


def h2_tag():
    keyboard_layout.write('<h2 style="clear: none;"></h2>')
    for i in range(0, 5):
        kbd.press(Keycode.LEFT_ARROW)
        kbd.release_all()

def ahref_tag():
    keyboard_layout.write('<a href=""></a>')
    for i in range(0, 4):
        kbd.press(Keycode.LEFT_ARROW)
        kbd.release_all()  
        
def superfine_diz():
    keyboard_layout.write("<3 my superfine dizbang!")


def blue_test():
    keyboard_layout.write("blue")


def green_test():
    keyboard_layout.write("green")


def yellow_test():
    keyboard_layout.write("yellow")


def red_test():
    keyboard_layout.write("red")


#################### Macro banks list definition ####################
# set up which functions map to which buttons and banks
MACRO_BANKS = [
    # DEFAULT_BANK
    {
        "blue_btn": ctrl_shift_w, #close all gimp windows
        "green_btn": ctrl_shift_t, #reopen closed browser tab
        "yellow_btn": ctrl_shift_e, #export in gimp
        "red_btn": ctrl_shift_s #take screenshot in firefox
    },
    # BLUE_BANK
    {
        "blue_btn": superfine_diz,
        "green_btn": blue_test,
        "yellow_btn": blue_test,
        "red_btn": blue_test
    },
    # GREEN_BANK
    {
        "blue_btn": green_test,
        "green_btn": green_test,
        "yellow_btn": green_test,
        "red_btn": green_test
    },
    # YELLOW_BANK
    {
        "blue_btn": yellow_test,
        "green_btn": yellow_test,
        "yellow_btn": yellow_test,
        "red_btn": yellow_test
    },
    # RED_BANK
    {
        "blue_btn": post_skeletron,
        "green_btn": bio_skeletron,
        "yellow_btn": ahref_tag,
        "red_btn": h2_tag
    }

]

# variable to track which bank is selected currently
current_bank = DEFAULT_BANK

# One pixel connected internally!
dot = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# Built in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT



# Digital input with pullup on D1, D2, D3, and D4
buttons = []
for p in button_pins:
    button = DigitalInOut(p)
    button.direction = Direction.INPUT
    button.pull = Pull.UP
    buttons.append(button)

time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems
# Increase this if board gets into broken state when it's plugged in

# Used if we do HID output. Must be after time.sleep()
kbd = Keyboard()
keyboard_layout = KeyboardLayoutUS(kbd)  # We're in the US :)


######################### HELPERS ##############################

# Helper to give us a nice color swirl
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0):
        return [0, 0, 0]
    if (pos > 255):
        return [0, 0, 0]
    if (pos < 85):
        return [int(pos * 3), int(255 - (pos * 3)), 0]
    elif (pos < 170):
        pos -= 85
        return [int(255 - pos * 3), 0, int(pos * 3)]
    else:
        pos -= 170
        return [0, int(pos * 3), int(255 - pos * 3)]


# return the RGB value of the currently selected banks color
def get_bank_color():
    if current_bank == DEFAULT_BANK:
        return wheel(wheel_i & 255)
        # return [225,255,255]
    elif current_bank == BLUE_BANK:
        return [0, 0, 255]
    elif current_bank == GREEN_BANK:
        return [0, 255, 0]
    elif current_bank == YELLOW_BANK:
        return [255, 255, 0]
    elif current_bank == RED_BANK:
        return [255, 0, 0]

def leds_off():
    for pin in led_pins:
        pin.value = False   
def set_led(led_pin):
    #print("inside set_pin %s" % led_pin)
    leds_off()
    led_pin.value = True
######################### MAIN LOOP ##############################

while True:
    # set current banks color
    dot[0] = get_bank_color()
    # update i variable for color wheel function
    wheel_i = (wheel_i + 1) % 256  # run from 0 to 255
    # time.sleep(0.01) # make bigger to slow down

    # if any button goes down record the time and print debug message
    # 0 - blue, 1 - green, 2 - yellow, 3 - red
    for i in range(0, 4):
        if not buttons[i].value and old_pin_states[i]:
            pressed_times[i] = time.monotonic()
            print("btn %s down %s" % (i, pressed_times[i]), end="\t")

    # Check if any button has been released
    # 0 - blue, 1 - green, 2 - yellow, 3 - red
    for i in range(0, 4):
        if buttons[i].value and not old_pin_states[i]:
            now = time.monotonic()
            # check for long press
            if pressed_times[i] > 0 and now - pressed_times[i] > LONG_PRESS_TIME:
                print("%s long pressed!" % i, end="\t")
                if current_bank == DEFAULT_BANK:
                    # print message to the PC script that launches the color pop-up
                    # print(MODE_ACTIVATED_TEMPLATE % ("blue"), end ="\t")
                    kbd.press(Keycode.GUI, keycode_list[i])
                    kbd.release_all()  # release!

                    # set current bank to blue
                    current_bank = bank_list[i]
                    
                    set_led(led_pins[i])
                else:  # not currently on default bank
                    if current_bank == bank_list[i]:
                        # print message to the PC script that launches the color pop-up
                        # print(MODE_ACTIVATED_TEMPLATE % ("default"), end ="\t")
                        # set current bank to default
                        current_bank = DEFAULT_BANK
                        kbd.press(Keycode.GUI, Keycode.F12)
                        kbd.release_all()  # release!
                        leds_off()
                    else:
                        kbd.press(Keycode.GUI, keycode_list[i])
                        kbd.release_all()  # release!

                        # set current bank to selected
                        current_bank = bank_list[i]
                        set_led(led_pins[i])
            else:
                print("Button %s pressed!" % i, end="\t")

                # call the blue_btn macro for the current bank
                print("calling bank %s button %s" % (current_bank, button_names[i]))
                MACRO_BANKS[current_bank][button_names[i]]()
                # No regular LEDs on the micro footstool
                """
                A3_led.value = True
                time.sleep(0.5)
                A3_led.value = False
                """
            # reset the pressed down time variable
            pressed_times[i] = -1

        # save current state for next iteration
        old_pin_states[i] = buttons[i].value