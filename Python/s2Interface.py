import os
import serial
import time
import threading

import telemParse import TelemParse

class S2_Interface:
    nonlocal ser, ports_box, serial_name
    global parser = TelemParse()    # Contains all telem data

    def scan():
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports

    """
    @params
        port_name (string)  - name of port  ex: COM8
        baud (integer)      - baud rate     ex: 115200
        timeout (decimal)   - time before timing out    ex: 0.5
    """
    def connect(port_name, baud, timeout):
        if ser.isOpen():
            ser.close()
        try:
            ser = serial.Serial(port=port_name, baud, timeout)
            ser.open()
            ser.readline()
            serial_name = str(port_name) # assign port name
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
    def parse_serial():
        try:
            if (ser.is_open):
                packet = ser.readLine()
                print(len(packet))

	            packet = unstuff_packet(packet)
                try:
                    parser.parse_packet(packet)
                except:
                    print("Packet lost")
        Exception as e:
            print(e)

    def unstuff_packet(packet):
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
