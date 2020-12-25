import serial
import struct
import serial.tools.list_ports
from s2Interface import S2_Interface

s2_interface = S2_Interface()
ports = s2_interface.scan()
print(ports)

s2_interface.connect("/dev/cu.usbmodem11203", 115200, 2)
while(1):
    s2_interface.parse_serial()