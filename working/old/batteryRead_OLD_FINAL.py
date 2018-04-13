#!/usr/bin/python
# -*- coding: utf-8 -*-

import minimalmodbus
import serial
import syslog
import time
import math
import sys
# Looping constants

running = 1
counter = 0

# Some constants which are decided by us, and are sent to the inverter - not coming from the BMS
# Voltage at which battery need be charged. 58,5V

CONST_BAT_CHARGE_VOLTAGE = 585

# Voltage at which the battery stops discharging

CONST_BAT_DISCHARGE_VOLTAGE = 40 * 10

# Battery Rack DC Charge Current Limitation, integer

VAR_BAT_CHRGE_CURR_LIM = 80 * 10
VAR_PREV_AVERAGE_SOC = 80
VAR_TEST = 12
# Battery Rack DC Discharge Current Limitation, integer

CONST_BAT_DCHRG_CURR_LIM = 200 * 10
CONST_BAT_RCK_AVG_SOC = 75  # Battery Rack, average module SOC Value, integer
CONST_BAT_RCK_AVG_SOH = 98  # Battery Rack, average module SOH Value, integer

# Bank A
# port name, slave address (in decimal)

instrument_A = minimalmodbus.Instrument('/dev/ttyUSB0', 1)

# Bank B

instrument_B = minimalmodbus.Instrument('/dev/ttyUSB1', 1)
# Port on which to send via serial to CAN Shield Arduino

port = '/dev/ttyACM0'

# Initialize CAN Shield Arduino Serial Line

ard = serial.Serial(port, 115200, timeout=5)


################### FUNCTIONS ###################
# Convert integer to binary string

def int2bin(i):
    if i == 0:
        return '0'
    s = ''
    while i:
        if i & 1 == 1:
            s = '1' + s
        else:
            s = '0' + s
        i /= 2
    return s


# Rounds up to the the ceiling

def ceiling(x):
    n = int(x)
    return (n if n - 1 < x <= n else n + 1)


# To determine the number of bits within a type of object

def bitLen(int_type):
    length = 0
    while int_type:
        int_type >>= 1
        length += 1
    return length


# Convert an integer into the parts of its most and least significant bits

def toHex(x):
    LSB = x & 0x00FF
    MSB = x >> 8
    return (LSB, MSB)


# Get battery data

def getBatteryData(InverterAddress):
    global VAR_PREV_AVERAGE_SOC
    # Initializing send buffer, this buffer is populated with integers - ready for transformation into a byte array

    sendBuffer = []
    if InverterAddress == 0x351:
        sendBuffer.append(1)
        chrge_Cur_Lim_A = instrument_A.read_register(40018)
        chrge_Cur_Lim_B = instrument_B.read_register(40018)
        chrge_Cur = ceiling((chrge_Cur_Lim_A + chrge_Cur_Lim_B)/2 * 0.6 * 10)
        print "The previous average SOC:"
        print VAR_PREV_AVERAGE_SOC
        if VAR_PREV_AVERAGE_SOC > 90:
            chrge_Cur = 0
        print "Will charge batteries @ "
        print chrge_Cur/10
        sendBuffer.append(CONST_BAT_CHARGE_VOLTAGE)
        sendBuffer.append(chrge_Cur)
        sendBuffer.append(CONST_BAT_DCHRG_CURR_LIM)
        sendBuffer.append(CONST_BAT_DISCHARGE_VOLTAGE)
    elif InverterAddress == 0x355:
        sendBuffer.append(5)

        # Battery Rack A, Average module SOC Value, integer

        socA = instrument_A.read_register(40008)
        socB = instrument_B.read_register(40008)
        soc = ceiling((socA + socB) / 2 / 10)
        sendBuffer.append(soc)
        # print "SOC For Bank A"
        # print socA
        # print "SOC For Bank B"
        # print socB
        # Battery Rack, average module SOH Value, integer
        print "Average SOC Value, both banks"
        print soc
        VAR_PREV_AVERAGE_SOC = soc
        sohA = instrument_A.read_register(40009)
        sohB = instrument_B.read_register(40009)
        soh = ceiling((sohA + sohB) / 2 / 10)
        # print "Average SOH Value, both banks"
        # print soh
        sendBuffer.append(soh)
    elif InverterAddress == 0x35A:
        sendBuffer.append(0x65)
        sendBuffer.append(0)
        sendBuffer.append(0)
    else:
        sendBuffer.append(0)

    byteSendBuffer = bytearray()
    for i in sendBuffer:
        (LSB, MSB) = toHex(i)
        byteSendBuffer.append(LSB)
        byteSendBuffer.append(MSB)

    # print "The following is the byte array to be sent to the Inverter"

    # for byte in byteSendBuffer:
    #     print byte
    return byteSendBuffer


while running:
    print 'Starting read and serial write cycle'
    try:
        print "Attempting read and send..."
        if ard.inWaiting()>0:
            ard.write(getBatteryData(0x351))
            time.sleep(0.1)
        if ard.inWaiting()>0:
            ard.write(getBatteryData(0x355))
            time.sleep(0.1)
        if ard.inWaiting()>0:
            ard.write(getBatteryData(0x35A))
    except:
        e = sys.exc_info()[0]
        print "Failure...Error is:"
        print e
        pass

    time.sleep(0.3)

    print 'Ending read and serial write cycle'
