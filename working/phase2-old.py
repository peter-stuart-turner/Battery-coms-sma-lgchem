#!/usr/bin/python
# -*- coding: utf-8 -*-

import minimalmodbus
import serial
import syslog
import time
import math

# Looping constants

running = 1
counter = 0


# Bank A
# port name, slave address (in decimal)
minimalmodbus.BAUDRATE = 9600
minimalmodbus.TIMEOUT = 0.3
energy_meter = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
energy_meter.serial.baudrate = 9600
energy_meter.serial.bytesize = 8
energy_meter.address = 1
energy_meter.debug = True


print(energy_meter)

while running:
    time.sleep(1)
    # line_to_line_1 = energy_meter.read_register(1046)
    #print line_to_line_1
    #getBatteryData(0x351)
    #print (instrument_A.read_register(40008))

    # Voltage line to line register = 1008
    # Frequency register = 1046
    # Temperature register = 1096
    try:
        line_to_line_1 = energy_meter.read_long(0x1046)
        # line_to_line_1 = energy_meter.read_bit(0x1008)
        print line_to_line_1
    except IOError as e:
        print('I/O error')
        print('The response is: {!r}'.format(e))
        pass
    except ValueError as e:
        print('Value error')
        print('The response is: {!r}'.format(e))
        pass
    except:
        print "Failure..."
        pass

    time.sleep(0.3)

    print '---------------------------'


def test_function():

    print('test')
