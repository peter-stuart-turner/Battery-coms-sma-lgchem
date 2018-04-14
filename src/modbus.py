#!/usr/bin/python
# -*- coding: utf-8 -*-

import constants
import ctypes
import minimalmodbus
import serial
import time
import math
from threading import Timer

IS_GRID_FEEDING = False
PERIOD = 5
LENGTH = 10
ENERGY_COUNTER = 0
PREVIOUS_VALS = []

minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True
minimalmodbus.TIMEOUT = 0.3
'''
Error Handling
'''
GLOBAL_BATTERY_ERROR = None
GLOBAL_ENERGY_METER_ERROR = None
'''
Instrument Stored Values (To use), and Counter
'''
# Battery banks ( Format: Current, Current Limit, SOC, SOH)
BANK_A_VALUES = {}
BANK_B_VALUES = {}
BANK_A_EXCEPTION = None
BANK_B_EXCEPTION = None
BANK_COUNTER = 0
'''
Instrument Declarations (Note: Ports are not constant)
'''
ENERGY_METER = minimalmodbus.Instrument('/dev/ttyUSB1', 1)
BATTERY_BANK_A = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
BATTERY_BANK_B = minimalmodbus.Instrument('/dev/ttyUSB2', 1)
'''
Instrument Settings for Minimal Modbus Library
'''

ENERGY_METER.serial.baudrate = 9600
ENERGY_METER.serial.bytesize = 8
ENERGY_METER.address = 1
ENERGY_METER.debug = False
'''
FUNCTIONS: Error Checking
'''
def generate_Error_Message():
    global BANK_A_EXCEPTION, BANK_B_EXCEPTION, GLOBAL_BATTERY_ERROR, GLOBAL_ENERGY_METER_ERROR
    errorMessage = "No Errors"
    if(GLOBAL_BATTERY_ERROR):
        errorMessage = GLOBAL_BATTERY_ERROR
    if(GLOBAL_ENERGY_METER_ERROR):
        errorMessage = errorMessage + "\n" + GLOBAL_ENERGY_METER_ERROR
    return errorMessage
'''
FUNCTIONS: BATTERY BANKS
'''
def get_Bank_Readings():
    global BANK_A_VALUES, BANK_B_VALUES, BANK_A_EXCEPTION, BANK_B_EXCEPTION, GLOBAL_BATTERY_ERROR, BANK_COUNTER
    if(BANK_COUNTER <= 100):
        BANK_COUNTER = BANK_COUNTER + 1
        aValues = check_Bank_Existing_Values("A")
        bValues = check_Bank_Existing_Values("B")
        if aValues and bValues:
            return combine_Bank_Readings(BANK_A_VALUES, BANK_B_VALUES)
        elif aValues and not bValues:
            return combine_Bank_Readings(BANK_A_VALUES, BANK_A_VALUES)
        elif bValues and not aValues:
            return combine_Bank_Readings(BANK_B_VALUES, BANK_B_VALUES)
        else:
            print("No Battery Banks Connected, or there are errors for both")
            exit()
    else:
        BANK_COUNTER = 0
        aStable = get_Bank_A_Readings()
        bStable = get_Bank_B_Readings()
        if( aStable and bStable ):
            GLOBAL_BATTERY_ERROR = None
            BANK_A_EXCEPTION = None
            BANK_B_EXCEPTION = None
            return combine_Bank_Readings(BANK_A_VALUES, BANK_B_VALUES)
        elif ( aStable and not bStable ):
            BANK_A_EXCEPTION = None
            GLOBAL_BATTERY_ERROR = "Error with bank B: " + BANK_B_EXCEPTION
            return combine_Bank_Readings(BANK_A_VALUES,BANK_A_VALUES)
        elif ( bStable and not aStable ):
            BANK_B_EXCEPTION = None
            GLOBAL_BATTERY_ERROR = "Error with bank A: " + BANK_A_EXCEPTION
            return combine_Bank_Readings(BANK_B_VALUES,BANK_B_VALUES)
        else:
            GLOBAL_BATTERY_ERROR = "Errors with both battery banks"
def initialize_Bank_Readings():
    aStable = get_Bank_A_Readings()
    bStable = get_Bank_B_Readings()
    print("Bank A Stable: {}".format(aStable))
    print("Bank B Stable: {}".format(bStable))
def check_Bank_Existing_Values(bank):
    global BANK_A_VALUES, BANK_B_VALUES
    if bank == "A":
        if len(BANK_A_VALUES) == 4:
            return True
        else:
            return False
    elif bank == "B":
        if len(BANK_B_VALUES) == 4:
            return True
        else:
            return False
def combine_Bank_Readings(bankA, bankB):
    current =       (bankA["Current"] + bankB["Current"]) / 2
    current_Lmit =  ceiling(bankA["Current_Limit"] + bankB["Current_Limit"] / 2 * 0.6 * 10)
    soc =           ceiling((bankA["SOC"] + bankA["SOC"])/2 /10)
    soh =           ceiling((bankA["SOH"] + bankA["SOH"])/2 /10)
    BANK_VALUES = {
            "Current":          current,
            "Current_Limit":    current_Lmit,
            "SOC":              soc,
            "SOH":              soh
            }
    print("Bank Values", BANK_VALUES)
    return BANK_VALUES
# Retrieves all relevant battery settings for A, returns false on error
def get_Bank_A_Readings():
    global BANK_A_VALUES
    global BANK_A_EXCEPTION
    try:
        battery_current_A = BATTERY_BANK_A.read_register(40007)
	print("A Current", battery_current_A)
        chrge_Cur_Lim_A = BATTERY_BANK_A.read_register(40018)
        socA = BATTERY_BANK_A.read_register(40008)
        sohA = BATTERY_BANK_A.read_register(40009)
        BANK_A_VALUES = {
                "Current":          battery_current_A,
                "Current_Limit":    chrge_Cur_Lim_A,
                "SOC":              socA,
                "SOH":              sohA
            }
        return True
    except Exception as e:
	print("A exception", e)
        BANK_A_EXCEPTION = e
        return False
# Retrieves all relevant battery settings for B, returns false on error
def get_Bank_B_Readings():
    global BANK_B_VALUES
    global BANK_B_EXCEPTION
    try:
        battery_current_B = BATTERY_BANK_B.read_register(40007)
        chrge_Cur_Lim_B = BATTERY_BANK_B.read_register(40018)
        socB = BATTERY_BANK_B.read_register(40008)
        sohB = BATTERY_BANK_B.read_register(40009)
        BANK_B_VALUES = {
                "Current":          battery_current_B,
                "Current_Limit":    chrge_Cur_Lim_B,
                "SOC":              socB,
                "SOH":              sohB
            }
        return True
    except Exception as e:
	print("B Exception", e)
        BANK_B_EXCEPTION = e
        return False
# Rounds up to the the ceiling #
def ceiling(x):
    n = int(x)
    return (n if n - 1 < x <= n else n + 1)
'''
FUNCTIONS: ENERGY METER
'''
# Power Factors #
def get_Power_Factor_Phase_1():
    return ENERGY_METER.read_long(0x1018);
def get_Power_Factor_Phase_2():
    return ENERGY_METER.read_long(0x101A);
def get_Power_Factor_Phase_3():
    return ENERGY_METER.read_long(0x101C);
# Active Powers #
def get_Reactive_Phase_1():
    return ENERGY_METER.read_long(0x102A);
def get_Reactive_Phase_2():
    return ENERGY_METER.read_long(0x1032);
def get_Reactive_Phase_3():
    return ENERGY_METER.read_long(0x1034);
def get_Average_Reactive_Power():
    global GLOBAL_ENERGY_METER_ERROR
    try:
        # time.sleep(0.1)
    	reactive1 = get_Reactive_Phase_1()
    	# time.sleep(0.1)
    	reactive2 = get_Reactive_Phase_2()
    	# time.sleep(0.1)
    	reactive3 = get_Reactive_Phase_3()
        reactive = ceiling((reactive1+reactive2+reactive3)/3)
        return reactive
    except Exception as ee:
        return False
        GLOBAL_ENERGY_METER_ERROR = "Energy Meter Error: " + ee;


# Main Functions #
def is_Gridfeeding():
    global IS_GRID_FEEDING, LENGTH, PREVIOUS_VALS, ENERGY_COUNTER
    temp_gf = False
    reativePower = get_Average_Reactive_Power()
    if(reativePower):
    	length = len(PREVIOUS_VALS)
    	if(reativePower > 1000):
            temp_gf = True
    	if length < LENGTH:
            PREVIOUS_VALS.append(temp_gf)
    	else:
            PREVIOUS_VALS = PREVIOUS_VALS[1:LENGTH]
     	    PREVIOUS_VALS.append(temp_gf)
     	    ENERGY_COUNTER = 0

    	for ii in range(0, length) :
            if not(PREVIOUS_VALS[ii]):
                ENERGY_COUNTER = ENERGY_COUNTER + 1

	    threshold = ceiling( 0.7 * LENGTH )
        valuesForGridfeed = LENGTH - ENERGY_COUNTER
        if valuesForGridfeed < threshold:
            gf = True
        else:
            gf = False

	if length == 0:
            IS_GRID_FEEDING = False
    	else:
    	    IS_GRID_FEEDING = gf
    timer = Timer(PERIOD, is_Gridfeeding)
    timer.start()
