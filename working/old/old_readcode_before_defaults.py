# Retrieves actual current to (or from) batteries
def get_Battery_Current():
    battery_current_A = BATTERY_BANK_A.read_register(40007)
    battery_current_B = battery_current_A
    #battery_current_B = BATTERY_BANK_B.read_register(40007)
    battery_current = (ctypes.c_int(battery_current_A).value + ctypes.c_int(battery_current_B).value)/2
    return battery_current
# Retrieves the average state of charge (SOC) for banks A and B #
def get_Average_Charge_Current_Limit():
    chrge_Cur_Lim_A = BATTERY_BANK_A.read_register(40018)
    #chrge_Cur_Lim_B = BATTERY_BANK_B.read_register(40018)
    chrge_Cur_Lim_B=chrge_Cur_Lim_A
    return ceiling((chrge_Cur_Lim_A + chrge_Cur_Lim_B)/2 * 0.6 * 10)
# Retrieves the average state of charge (SOC) for banks A and B #
def get_Average_SOC():
    socA = BATTERY_BANK_A.read_register(40008)
    #socB = BATTERY_BANK_B.read_register(40008)
    socB=socA
    return ceiling((socA + socB) / 2 / 10)
def get_Average_SOH():
    sohA = BATTERY_BANK_A.read_register(40009)
    #sohB = BATTERY_BANK_B.read_register(40009)
    sohB=sohA
    return ceiling((sohA + sohB) / 2 / 10)

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

def is_Gridfeeding():

    global IS_GRID_FEEDING
    global LENGTH
    global PREVIOUS_VALS
    global COUNTER

    temp_gf = False

    try:
    	time.sleep(0.1)
    	power_factor_1 = get_Power_Factor_Phase_1()
    	time.sleep(0.1)
    	power_factor_2 = get_Power_Factor_Phase_2()
    	time.sleep(0.1)
    	power_factor_3 = get_Power_Factor_Phase_3()
    	print "PF1"
	print power_factor_1
	print power_factor_2
	print power_factor_3

	# TESTING
	#activePtest = get_Active_Phase_1()
	#tempX = ctypes.c_long(activePtest).value
	#print "THE ACTIVE POWERRRRRR-----"
	#print activePtest
	#print tempX

	pf = (power_factor_1 + power_factor_2 + power_factor_3)/3

    	length = len(PREVIOUS_VALS)

    	if(pf > 1000):
            temp_gf = True

    	if length < LENGTH:
	    PREVIOUS_VALS.append(temp_gf)
    	else:
	    PREVIOUS_VALS = PREVIOUS_VALS[1:LENGTH]
	    PREVIOUS_VALS.append(temp_gf)
	    COUNTER = 0

    	gf = False

    	for ii in range(0, length) :
	    if not(PREVIOUS_VALS[ii]):
	        #gf = False
	    	COUNTER = COUNTER + 1
	print "counter_----------------------------------------------------"
	print COUNTER
	if COUNTER < 4:
	    gf = True

	if length == 0:
            IS_GRID_FEEDING = False
	else:
	    IS_GRID_FEEDING = gf

    except Exception as ex:
	print("AN ERROR OCCURRED WITH GRID FEEDING")
	print("The error is shown below")
	print(ex)
	pass

    timer = Timer(PERIOD, is_Gridfeeding)
    timer.start()
