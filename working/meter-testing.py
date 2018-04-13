#!/usr/bin/python
# -*- coding: utf-8 -*-

import constants
import minimalmodbus
import serial
import time
import math

PHASE_REG_1 = 0x1020
PHASE_REG_2 = 0x1022
PHASE_REG_3 = 0x1024

REACTIVE_POWER_REG_1 = 0x1030
REACTIVE_POWER_REG_2 = 0x1032
REACTIVE_POWER_REG_3 = 0x1034

'''
Instrument Declarations (Note: Ports are not constant)
'''
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True
minimalmodbus.TIMEOUT = 0.3
ENERGY_METER = minimalmodbus.Instrument('/dev/ttyUSB2', 1)
BATTERY_BANK_A = minimalmodbus.Instrument('/dev/ttyUSB2', 1)
BATTERY_BANK_B = minimalmodbus.Instrument('/dev/ttyUSB3', 1)
'''
Instrument Settings for Minimal Modbus Library
'''
ENERGY_METER.serial.baudrate = 9600
ENERGY_METER.serial.bytesize = 8
ENERGY_METER.address = 1
ENERGY_METER.debug = False
'''
FUNCTIONS: BATTERY BANKS
'''
# Retrieves the average state of charge (SOC) for banks A and B #
def get_Average_Charge_Current_Limit():
    chrge_Cur_Lim_A = BATTERY_BANK_A.read_register(40018)
    chrge_Cur_Lim_B = BATTERY_BANK_B.read_register(40018)
    return ceiling((chrge_Cur_Lim_A + chrge_Cur_Lim_B)/2 * 0.6 * 10)
# Retrieves the average state of charge (SOC) for banks A and B #
def get_Average_SOC():
    socA = BATTERY_BANK_A.read_register(40008)
    socB = BATTERY_BANK_B.read_register(40008)
    return ceiling((socA + socB) / 2 / 10)
def get_Average_SOH():
    sohA = instrument_A.read_register(40009)
    sohB = instrument_B.read_register(40009)
    return ceiling((sohA + sohB) / 2 / 10)
# Rounds up to the the ceiling #
def ceiling(x):
    n = int(x)
    return (n if n - 1 < x <= n else n + 1)
'''
FUNCTIONS: ENERGY METER
'''
# Line to Neutral Voltages #
def get_Line_To_Neutral_Voltage_Phase_1():
    return ENERGY_METER.read_long(0x1002);
def get_Line_To_Neutral_Voltage_Phase_2():
    return ENERGY_METER.read_long(0x1004);
def get_Line_To_Neutral_Voltage_Phase_3():
    return ENERGY_METER.read_long(0x1006);
# Line to Line Voltages #
def get_Line_To_Line_Voltage_12():
    return ENERGY_METER.read_long(0x1008);
def get_Line_To_Line_Voltage_23():
    return ENERGY_METER.read_long(0x100A);
def get_Line_To_Line_Voltage_31():
    return ENERGY_METER.read_long(0x100C);
# Line Currents #
def get_Line_Current_Phase_1():
    return ENERGY_METER.read_long(0x1010);
def get_Line_Current_Phase_2():
    return ENERGY_METER.read_long(0x1012);
def get_Line_Current_Phase_3():
    return ENERGY_METER.read_long(0x1014);
# Power Factors #
def get_Power_Factor_Phase_1():
    return ENERGY_METER.read_long(0x1018);
def get_Power_Factor_Phase_2():
    return ENERGY_METER.read_long(0x101A);
def get_Power_Factor_Phase_3():
    return ENERGY_METER.read_long(0x101C);
# Main Functions #
def is_Gridfeeding_():
    power_factor_1 = get_Power_Factor_Phase_1()
    print(power_factor_1)
    #power_factor_2 = get_Power_Factor_Phase_2()
    #power_factor_3 = get_Power_Factor_Phase_3()
    #pf = (power_factor_1 + power_factor_2 + power_factor_3)/3
    if(power_factor_1 >= 0):
        return False
    return True

while True:
    time.sleep(0.5)
    print("Grid feeding? {}".format(is_Gridfeeding_()))
