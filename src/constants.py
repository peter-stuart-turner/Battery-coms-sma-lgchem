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

PHASE_REG_1 = 0x1020
PHASE_REG_2 = 0x1022
PHASE_REG_3 = 0x1024

REACTIVE_POWER_REG_1 = 0x1030
REACTIVE_POWER_REG_2 = 0x1032
REACTIVE_POWER_REG_3 = 0x1034
