"""
	Class to handle receiving telemetry and sending commands to boards

    Michigan Aeronautical Science Association
    Authors: Arthur Zhang (arthurzh@umich.edu) and Nathaniel Kalantar (nkalan@umich.edu)
    Modified from Engine Controller 3 code
    Created: December 24, 2020
"""

import os
import sys
import serial
import time
import threading

from telemParse import TelemParse
class S2_Interface:
    def __init__(self):
        self.ser            = serial.Serial(port=None)
        self.ports_box      = []
        self.serial_name    = ""
        self.parser         = TelemParse()    # Contains all telem data

    ## TODO: add close function
    ## TODO: add write function
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
            self.ser = serial.Serial(port=port_name, baudrate=baud, bytesize=8,
                                timeout=timeout, stopbits=serial.STOPBITS_ONE)
            if not self.ser.isOpen():
                self.ser.open()
            self.serial_name = str(port_name) # assign port name
            print("Connection established on %s" % str(port_name))
        except Exception as e:
            print("Unable to connect to selected port ", e)

    """
    experimental multithreading
    def begin_listening():
        # Creates listener thread to listen for serial
        child_thread = threading.Thread(target=parse_serial)
        child_thread.start()
    """

    # Updates global parser variable for python gui to use
    # @returns: 0 if unsuccessful parse and 1 for successful parse
    #       
    def parse_serial(self):
        try:
            if (self.ser.is_open):
                packet = self.ser.read_until()
                if len(packet) > 0:
                    print(len(packet))
                    packet = self.unstuff_packet(packet)
                    try:
                        self.parser.parse_packet(packet)
                        return 1
                    except Exception as e:
                        print("Packet lost with error ", e)
        except Exception as e:
            print(e)
        return 0

    def unstuff_packet(self, packet):
        unstuffed = b''
        replacement = 1
        index = int(packet[0])
        #print("packet ", index)
        for n in range(1, len(packet)):
            temp = packet[n:n+1]
            if(n == index):
                index = int(packet[n])+n
                temp = bytes(replacement) # creates zero byte of integer size 1
            unstuffed = unstuffed + temp
        packet = unstuffed
        return packet