import time
import constants
import modbus
import canbus
import dummies
from threading import Timer

import RPi.GPIO as GPIO

'''
The Chuck Norris Perfect Battery Cycle'r

This program runs on a raspberry pi, and is reposible
for reading values from 2 banks or LG Chem batteries,
as well as a a bi-directional energy meter. These values
are read using Modbus (RTU) over RS-485.

The information is used to control the logic of a heavy
duty contactor, as well as the quantity of charge current
to batteries. Information is relayed via canbus to a SMA
Sunny Island master inverter, which is the source of
control for the charge current.

START OF PROGRAM
'''
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
'''
GLOBAL VARIABLES
'''

RELAY_PIN = 4

# Battery Related Globals #
BATTERY_VALUES = None

IS_GRIDFEEDING = None
LOWER_SOC = 0.1
UPPER_SOC = 0.9
# Program Related Globals #
RUNNING = True
CURRENT_STATE = None
NEXT_STATE = None
# Variable Charge Current #
BATTERY_CHARGE_CURRENT = 0
'''
MAIN FUNCTIONS
'''
#> 90 and feeding fix
def get_State_Variables():
    battery_soc = dummies.get_Average_SOC(0.05)
    gridfeeding = dummies.is_Gridfeeding(False)
    return battery_soc, gridfeeding
def determine_Next_State(battery_soc):
    battery_soc = battery_soc / 100.0
    is_gridfeeding = modbus.IS_GRID_FEEDING

    if (battery_soc < LOWER_SOC):
        next_state = 1
    elif (battery_soc < UPPER_SOC and is_gridfeeding):
        next_state = 2
    elif (battery_soc > LOWER_SOC) and not (is_gridfeeding):
	next_state = 2
    elif (battery_soc >= UPPER_SOC):
        next_state = 3
    elif (battery_soc == LOWER_SOC) and not(is_gridfeeding):
        next_state = 4
    else:
        next_state = 1
    return next_state
'''
MISC FUNCTIONS
'''
def close_Contactor():
    print "Closing contactor..."
    GPIO.output(RELAY_PIN, True)


def open_Contactor():
    print "Opening contactor..."
    GPIO.output(RELAY_PIN, False)

def set_Charge_Current(charge_current):
    canbus.set_Battery_Charge_Current(BATTERY_VALUES)
    print("Charge current set to: {}".format(charge_current))
'''
STATE FUNCTIONS
'''
def change_State(current_state, next_state):
    if(current_state == next_state):
        return
    else:
        if (next_state == 1):
            enter_state_1()
        elif (next_state == 2):
            enter_state_2()
        elif (next_state == 3):
            enter_state_3()
        elif (next_state == 4):
            enter_state_4()
    return next_state
def enter_state_1():
    '''
    Load shedding recovery
    '''
    # close_contactor()
    # change_charge_current("60 percent of max battery charge current")
    print "Entered into state load shedding recovery"
    close_Contactor()
    charge_current_limit = modbus.get_Average_Charge_Current_Limit()/10
    set_Charge_Current(int(0.6 * charge_current_limit))

def enter_state_2():
    '''
    Cycling on batteries
    '''
    # open_contactor()
    # change_charge_current("nominal")
    print "Entered into state Cycling on batteries"
    open_Contactor()
    set_Charge_Current(100)

def enter_state_3():
    '''
    Batteries full
    '''
    print "Entered into state Batteries full"
    close_Contactor()
    set_Charge_Current(0)

def enter_state_4():
    '''
    Batteries empty
    '''
    close_Contactor()
    set_Charge_Current(0)

def enter_reset():
    print "Resetting..."

def initialize():
    print("Initializing...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)

    is_grid_feeding_timer = Timer(modbus.PERIOD, modbus.is_Gridfeeding)

    is_grid_feeding_timer.start()

    modbus.initialize_Bank_Readings()
'''
Main Program Starts
'''

# Initialize GPIO pins, Gridfeeding timer, and initial battery bank readings
initialize()

# Main Loop #
while RUNNING:
    time.sleep(0.5)

    BATTERY_VALUES = modbus.get_Bank_Readings()
    errorMessage = modbus.generate_Error_Message()

    print("SOC: {}".format(BATTERY_VALUES["SOC"]))
    print("SOH: {}".format(BATTERY_VALUES["SOH"]))
    print("Battery Current: {}".format(BATTERY_VALUES["Current"]))
    print("Battery Current Limit: {}".format(BATTERY_VALUES["Current_Limit"]))
    print("Gridfeeding History: {}".format(modbus.PREVIOUS_VALS))
    print("Is Gridfeeding? {}".format(modbus.IS_GRID_FEEDING))
    print("Errors: \n")
    print(errorMessage)

    print("--------------------------------------")
    print("Determining State...")
    print("--------------------------------------")
    _, IS_GRIDFEEDING = get_State_Variables()
    NEXT_STATE = determine_Next_State(combinedBankReadings["SOC"])
    CURRENT_STATE = change_State(CURRENT_STATE, NEXT_STATE)
    print("--------------------------------------")
