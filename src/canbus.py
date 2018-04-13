#!/usr/bin/python
# -*- coding: utf-8 -*-
import constants
import modbus
import serial
import time
import math

port = '/dev/ttyACM0'
# Initialize CAN Shield Arduino Serial Line
uno = serial.Serial(port, 115200, timeout=5)


'''
FUNCTIONS
'''
def send_Buffer_To_Inverter(buffer):
    if uno.inWaiting()>0:
        uno.write(buffer)
def set_Battery_Charge_Current(ChargeCurrent):
    send_Buffer_To_Inverter(create_Buffer_To_Send_Over_CAN(0x351, ChargeCurrent))
    send_Buffer_To_Inverter(create_Buffer_To_Send_Over_CAN(0x355, ChargeCurrent))
# Create a buffer of instantaneous battery bank values, to send to inverter over CANBUS #
def create_Buffer_To_Send_Over_CAN(InverterAddress, ChargeCurrent):
    sendBuffer = []
    if InverterAddress == 0x351:
        sendBuffer.append(1)
        sendBuffer.append(constants.CONST_BAT_CHARGE_VOLTAGE)
        sendBuffer.append(ChargeCurrent)
        sendBuffer.append(constants.CONST_BAT_DCHRG_CURR_LIM)
        sendBuffer.append(constants.CONST_BAT_DISCHARGE_VOLTAGE)
    elif InverterAddress == 0x355:
        sendBuffer.append(5)
        sendBuffer.append(modbus.get_Average_SOC())
        sendBuffer.append(modbus.get_Average_SOH())
    else:
        sendBuffer.append(0)

    byteSendBuffer = bytearray()
    for i in sendBuffer:
        LSB, MSB = toHex(i)
        byteSendBuffer.append(LSB)
        byteSendBuffer.append(MSB)

    return byteSendBuffer
# Convert an integer into the parts of its most and least significant bits #
def toHex(x):
    LSB = x & 0x00FF
    MSB = x >> 8
    return LSB, MSB
