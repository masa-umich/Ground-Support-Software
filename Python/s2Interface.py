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
from _s2InterfaceAutogen import _S2_InterfaceAutogen  # Private autogenerated helper class

class S2_Interface:
    def __init__(self):
        self.ser            = serial.Serial(port=None)
        self.ports_box      = []
        self.serial_name    = ""
        self.parser         = TelemParse()    # Contains all telem data
        self.helper         = _S2_InterfaceAutogen()
        self.last_raw_packet = None
        self.init_valves()

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
                self.last_raw_packet = packet
                if len(packet) > 0:
                    #print(len(packet))
                    packet = self.unstuff_packet(packet)
                    try:
                        self.parser.parse_packet(packet)
                        self.unpack_valves()
                        return 1
                    except Exception as e:
                        print("Packet lost with error ", e)
        except Exception as e:
            print(e)
        return 0

    # initializes valve states in dict and item list
    def init_valves(self):
        valve_prefix = "vlv"
        vlvs_list = [key for key in self.parser.items
                            if key.startswith(valve_prefix)]
        num_valves = 0
        for key in vlvs_list: # dont assume greatest vlv in list is last
            vlv_num = str(key)[3:4] # get vlv num
            vlv_num = int(vlv_num)
            if (vlv_num > num_valves):
                num_valves = vlv_num
        num_valves += 1
        self.num_valves = num_valves
        self.parser.num_items += num_valves # update num items in array
        for n in range(0, num_valves):
            valve_name = 'vlv' + str(n) + '.en'
            self.parser.items.append(valve_name)
    
    # Unpack valves and generates valves key in dict
    def unpack_valves(self):
        valve_states = int(self.parser.dict["valve_states"]) 
        mask = 1
        for n in range(0, self.num_valves):
            state = 0
            if (mask & valve_states):
                state = 1
            valve_name = 'vlv' + str(n) + '.en'
            self.parser.dict[valve_name] = state
            mask = mask << 1

    # returns list of channels, cleaned up
    def channels(self):
        return [item for item in self.parser.items if (item != 'zero' and item != '')]

    """
    Decodes a COBS-encoded packet
    """
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

    """
	Calls an autogenerated function to pack command data into a packet according to a
    template csv file and sends it to the board
	@params
		ser (pyserial object)  - serial object to write to
		cmd_info (dict)        - dictionary with the following key value pairs:
			"function_name"     : function name (string)
			"target_board_addr" : address of board to send command to (integer)
			"timestamp"         : time the command was sent (integer)
			"args"              : list of arguments to send to the function (list)
	"""
    def s2_command(self, cmd_info):
        helper.s2_command(self, self.ser, cmd_info)

    """
    Getter function that returns a dictionary mapping a command name to its packet_type ID
    """
    def get_cmd_names_dict(self):
        return helper.cmd_names_dict
    
    """
    Getter function that returns a dictionary mapping a command's packet_type ID to a list of tuples
    containing function arguments in the order (arg_name, arg_type, xmit_scale)
    """
    def get_cmd_args_dict(self):
        return helper.cmd_args_dict
    
    def getBoardAddr(self, name):
        mapping = {
            "Engine Controller": 2, 
            "Flight Computer": 1, 
            "Pressurization Controller": 3, 
            "Recovery Controller": 4, 
            "GSE Controller": 0, 
            "Black Box": 5
        }
        return mapping[name]
