import time
import serial
import struct
import serial.tools.list_ports
from s2Interface import S2_Interface

s2_interface = S2_Interface()
ports = s2_interface.scan()
#print(ports)

s2_interface.connect("COM4", 115200, 2)
set_vlv = {
    "function_name": "set_vlv",
    "target_board_addr": 3,
    "timestamp": 99,
    "args": [1, 1]
}

start = {
    "function_name": "start_logging",
    "target_board_addr": 3,
    "timestamp": 100,
    "args": []
}

stop = {
    "function_name": "stop_logging",
    "target_board_addr": 3,
    "timestamp": 101,
    "args": []
}

erase = {
    "function_name" : "wipe_flash",
    "target_board_addr": 3,
    "timestamp":102,
    "args": []
}

zero_stepper = {
    "function_name": "set_stepper_zero",
    "target_board_addr": 3,
    "timestamp": 103,
    "args": [1]
}

move_stepper = {
    "function_name": "set_stepper_pos",
    "target_board_addr": 3,
    "timestamp": 103,
    "args": [1, 90]
}
s2_interface.s2_command(move_stepper)
time.sleep(2)
s2_interface.s2_command(zero_stepper)
time.sleep(2)
s2_interface.s2_command(move_stepper)

#s2_interface.s2_command(set_vlv)
#$time.sleep(1)
"""
s2_interface.s2_command(erase)
time.sleep(5)
s2_interface.s2_command(start)
time.sleep(1)
s2_interface.s2_command(stop)
time.sleep(1)
s2_interface.download_flash(3, 103)
"""

"""
while(1):
    parse_status = 0
    parse_status = s2_interface.parse_serial()
    if parse_status == 1:
        print(s2_interface.parser.dict) # get telem values
        print(s2_interface.parser.units) # get units
"""


