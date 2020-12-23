import os
import serial
import time
import threading

from telemParse import TelemParse

class S2_Interface:
    def __init__(self):
        self.ser            = None
        self.ports_box      = []
        self.serial_name    = ""
        self.parser         = TelemParse()    # Contains all telem data

    def scan(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports

    """
    @params
        port_name (string)  - name of port  ex: COM8
        baud (integer)      - baud rate     ex: 115200
        timeout (decimal)   - time before timing out    ex: 0.5
    """
    def connect(self, port_name, baud, timeout):
        if self.ser.isOpen():
            self.ser.close()
        try:
            self.ser = serial.Serial(port=port_name, baud_rate=baud, timeout=timeout)
            self.ser.open()
            self.ser.readline()
            self.serial_name = str(port_name) # assign port name
            print("Connection established on %s" % str(port_name))
        except:
            print("Unable to connect to selected port or no ports available")

    """
    experimental multithreading
    def begin_listening():
        # Creates listener thread to listen for serial
        child_thread = threading.Thread(target=parse_serial)
        child_thread.start()
    """

    # Updates global parser variable for python gui to use
    def parse_serial(self):
        try:
            if (self.ser.is_open):
                packet = self.ser.readLine()
                print(len(packet))

                packet = unstuff_packet(packet)
                try:
                    self.parser.parse_packet(packet)
                except:
                    print("Packet lost")
        except Exception as e:
            print(e)

    def unstuff_packet(self, packet):
        unstuffed = b''
        index = int(packet[0])
        for n in range(1, len(packet)):
            temp = packet[n:n+1]
            if(n == index):
                index = int(packet[n])+n
                temp = b'\n'
            unstuffed = unstuffed + temp
        packet = unstuffed
        return packet
