import serial
import struct
import serial.tools.list_ports
from s2Interface import S2_Interface

s2_interface = S2_Interface()
ports = s2_interface.scan()
print(ports)

s2_interface.connect("/dev/tty.usbmodem11303", 115200, 2)
while(1):
    parse_status = 0
    parse_status = s2_interface.parse_serial()
    if parse_status == 1:
        print(s2_interface.parser.dict) # get telem values
        print(s2_interface.parser.units) # get units

