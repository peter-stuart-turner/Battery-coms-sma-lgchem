import phase2

BATTERY_SOC = 0
BATTERY_CHARGE_CURRENT = 0

LOWER_SOC = 0.1
UPPER_SOC = 0.9

CURRENT_STATE = 0

# Enclose in loop

# Read BATTERY_SOC
# Read BATTERY_CHARGE_CURRENT

# Check the state to be in
if BATTERY_SOC < LOWER_SOC:
    # Enter state 1
    enter_state_1()

elif (BATTERY_SOC < UPPER_SOC) && ():
    # Enter state 2
    enter_state_2()

elif (BATTERY_SOC < LOWER_SOC) && ():
    # Enter state 2
    enter_state_2()

elif BATTERY_SOC => UPPER_SOC:
    # Enter state 3
    enter_state_3()

elif BATTERY_SOC == LOWER_SOC:
    # Enter state 4
    enter_state_4()

else:
    # Error state and reset


'''
Useful Functions
'''

def enter_state_1():
    '''
    Load shedding recovery
    '''
    close_contactor()
    change_charge_current("60 percent of max battery charge current")

def enter_state_2():
    '''
    Cycling on batteries
    '''
    open_contactor()
    change_charge_current("nominal")

def enter_state_3():
    '''
    Batteries full
    '''
    close_contactor()
    change_charge_current("zero")

def enter_state_4():
    '''
    Batteries full
    '''
    close_contactor()
    change_charge_current("zero")

def enter_reset():


def open_contactor():


def close_contactor():


def change_charge_current(charge_current):
