"""
	Class to handle receiving telemetry and sending commands to boards

    Michigan Aeronautical Science Association
    Authors: Arthur Zhang (arthurzh@umich.edu) and Nathaniel Kalantar (nkalan@umich.edu)
    Modified from Engine Controller 3 code
    Created: December 24, 2020
"""

import os
import sys
import pdb
import serial
import time
import threading
import struct
from datetime import datetime

from telemParse import TelemParse
from _s2InterfaceAutogen import _S2_InterfaceAutogen  # Private autogenerated helper class

class S2_Interface:
    def __init__(self, ser=serial.Serial(port=None)):
        self.ser            = ser
        self.ports_box      = []
        self.serial_name    = ""
        self.parser         = TelemParse()    # Contains all telem data
        self.helper         = _S2_InterfaceAutogen()
        self.last_raw_packet = None
        self.init_valves()
        self.init_motors()
        self.init_tanks()

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
                packet = self.ser.read_until(b'\x00')
                self.last_raw_packet = packet
                if len(packet) > 0:
                    packet = self.unstuff_packet(packet)
                    try:
                        self.parser.parse_packet(packet)
                        self.unpack_valves()
                        #print(self.parser.dict)
                        return 1
                    except Exception as e:

                        print("Packet lost with error ", e)
        except Exception as e:
            print(e)
        return 0


    def init_valves(self):
        valve_prefix = "vlv"
        vlvs_list = [key for key in self.parser.items
                            if key.startswith(valve_prefix)]
        num_valves = -1
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
            self.parser.units[valve_name] = 'ul'

    def init_motors(self):
        motor_prefix = "mtr"
        mtrs_list = [key for key in self.parser.items
                            if key.startswith(motor_prefix)]
        num_motors = -1
        for key in mtrs_list: # dont assume greatest vlv in list is last
            mtr_num = str(key)[3:4] # get vlv num
            mtr_num = int(mtr_num)
            if (mtr_num > num_motors):
                num_motors = mtr_num
        num_motors += 1
        self.num_motors = num_motors

    def init_tanks(self):
        tank_prefix = "tnk"
        tnks_list = [key for key in self.parser.items
                            if key.startswith(tank_prefix)]
        num_tanks = -1
        for key in tnks_list: # dont assume greatest vlv in list is last
            tnk_num = str(key)[3:4] # get vlv num
            tnk_num = int(tnk_num)
            if (tnk_num > num_tanks):
                num_tanks = tnk_num
        num_tanks += 1
        self.num_tanks = num_tanks

    
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
    Reads a byte array and returns an integer array (for debugging)
    """
    def bytes_to_array(self, bytes):
        array = [0]*len(bytes)

        for i in range(len(bytes)):
            array[i] = int(struct.unpack("<B", bytes[i:i+1])[0])
        
        return array

    """
    Decodes a COBS-encoded packet
    """
    def unstuff_packet(self, packet):
        try:
            #print(self.bytes_to_array(packet))
            #print('\n\n')
            unstuffed = b''
            replacement = 1
            index = int(packet[0])
            for n in range(1, len(packet)):
                temp = packet[n:n+1]
                if (temp == 0):
                    break # early return on zero
                if(n == index):
                    index = int(packet[n])+n
                    temp = bytes(replacement) # creates zero byte of integer size 1
                unstuffed = unstuffed + temp
            #print(self.bytes_to_array(unstuffed))
            packet = unstuffed
            return packet
        except Exception as e:
            print("error in unstuff_packet ", e)

    """
	Calls an autogenerated function to pack command data into a packet according to a
    template csv file and sends it to the board.
    Note: For the download_flash command, use the download_flash() function instead.
	@params
		ser (pyserial object)  - serial object to write to
		cmd_info (dict)        - dictionary with the following key value pairs:
			"function_name"     : function name (string)
			"target_board_addr" : address of board to send command to (integer)
			"timestamp"         : time the command was sent (integer)
			"args"              : list of arguments to send to the function (list)
	"""
    def s2_command(self, cmd_info):
        self.helper.s2_command(self.ser, cmd_info)

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

    """
    Sends the command to download flash. This uses the s2_command() function from this class,
    but does some extra stuff to ensure it reads and saves the resulting flash data immediately.
    Saves flash data to a .bin binary file in the directory given by the filepath parameter.
    @params
        target_board_addr    <int>:     board to send command to, same as for s2_command()
        timestamp            <int>:     time the command was sent, also same as s2_command()
        command_log          <File>:    command log file object
        filepath (optional)  <string>:  Directory to save flash data to. Defaults to current directory.
    """
    def download_flash(self, target_board_addr, timestamp, command_log, filepath=""):
        cmd_info = dict()
        cmd_info["function_name"] = "download_flash"
        cmd_info["target_board_addr"] = target_board_addr
        cmd_info["timestamp"] = timestamp
        cmd_info["args"] = []
        telem_info = dict()
        telem_info["function_name"] = "set_telem"
        telem_info["target_board_addr"] = target_board_addr
        telem_info["timestamp"] = timestamp
        telem_info["args"] = [1] # 1 stops telem

        # Double check the filepath works
        """
        if (filepath == ""):
            filepath = "./"
        elif (filepath[-1] != "/"):
            filepath += "/"
        """
        filepath = os.getcwd()
        time_file_stamp = time.strftime("%Y_%m_%d_%H-%M-%S")
        datadir = filepath+"/flash_dump/"+time_file_stamp
        os.makedirs(datadir)        
        
        # Output file should have timestamp in name
        filename = "board_" + str(cmd_info["target_board_addr"]) + "_flash_data.bin"
    
        try:
            with open(os.path.join(datadir, filename), "wb+") as binfile:   # Open the binary
                readfile = True                
                
                self.s2_command(telem_info)
                time.sleep(1)
                self.ser.reset_input_buffer()
                time.sleep(1)
                self.s2_command(cmd_info)                           # Send command to download flash
                command_log.write(datetime.now().strftime("%H:%M:%S,") + str(cmd_info)+ '\n')
                # Serial checks first 11 bytes ()
                
                while(readfile):                            
                    # Read the packet header (11 bytes), flash page (2048 bytes)
                    ser_page = self.ser.read(2048 + 11)
                    #if (len(ser_page) > 0):
                    # Check that packet_type in the CLB header is 1 (flash data)
                    #if (ser_page[0] != 1):
                    if (len(ser_page) != 2048 + 11):
                        readfile = False
                    else:
                        # Unencode COBS # Update: no cobs anymore
                        #self.unstuff_packet(ser_page)
                        #TODO get rid off "11:" once the firmware no longer sends a packet header during a flash data dump
                        #print(self.bytes_to_array(ser_page[11:]))
                        binfile.write(bytes(ser_page[11:]))  # Log to bin
        except Exception as e:
            print("Error: could not open file to write flash contents because of error ", e)
        telem_info["args"] = [0]
        self.s2_command(telem_info)
        print("Finished downloading flash data to " + os.path.join(datadir, filename))

        # Convert binary file to csv
        """
        try:
            print("Converting "+binfile+"...", end='')
            csv_file = binfile.rstrip(".bin")+".csv"
            os.system("fc_bin2csv.exe "+str(binfile)+" > "+csv_file)
            #print("Generating pdf...", end='')
            #os.system("fc_autoplot "+csv_file)
            #if("-s" in sys.argv):
            #   os.system("start chrome "+binfile.rstrip(".bin")+"_plots.pdf")  # Only for EC
            print(" done.")
        except Exception as e:
            print("Error when converting binary file to csv ", e)
        """
    
    """
    Returns the board address given a board name
    """
    def getBoardAddr(self, name):
        print(name)
        mapping = {
            "Engine Controller": 2, 
            "Flight Computer": 1, 
            "Pressurization Controller": 3, 
            "Recovery Controller": 4, 
            "GSE Controller": 0, 
            "Black Box": 5
        }
        return mapping[name]
