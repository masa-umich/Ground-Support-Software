"""
	Class to handle receiving telemetry and sending commands to boards

    Michigan Aeronautical Science Association
    Authors: Arthur Zhang (arthurzh@umich.edu) and Nathaniel Kalantar (nkalan@umich.edu)
    Modified from Engine Controller 3 code
    Created: December 24, 2020
"""

import os
import pdb
import time
import struct
from datetime import datetime
import traceback
# import sys
# import pdb
# import threading

import serial
import serial.tools.list_ports

from parsers.pressBoardParse import PressurizationController
from parsers.flightCompParse import FlightComputer
from parsers.gseControllerParse import GSEController
from _s2InterfaceAutogen import _S2_InterfaceAutogen  # Private autogenerated helper class
from binary_parser import BinaryParser


class S2_Interface:
    def __init__(self, ser=serial.Serial(port=None)):
        self.ser            = ser
        self.ports_box      = []
        self.serial_name    = ""
        #self.board_parser   = [None, FlightComputer(), None, None, None, None] # Maps board to associated packet parser
        self.board_parser   = [GSEController(), None, None, PressurizationController(), None, None] # Maps board to associated packet parser
        self.helper         = _S2_InterfaceAutogen()
        self.last_raw_packet = None

        # init valves and motors
        self.num_valves = [0]*len(self.board_parser)
        self.num_motors = [0]*len(self.board_parser)
        self.num_tanks = [0]*len(self.board_parser)
        self.init_valves()
        self.init_motors()
        self.init_tanks()

        # compile channels from all parsers
        self.channels = []
        self.units = {}
        for i in range(len(self.board_parser)):
            prefix = self.getPrefix(self.getName(i))
            parser = self.board_parser[i]
            if parser:
                for item in parser.items:
                    name = str(prefix+item)
                    self.channels.append(name)
                    self.units[name] = parser.units[item]
        
        # init binary parser
        self.binparse = BinaryParser(interface=self)

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
            traceback.print_exc()

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
        board_addr = 3
        try:
            if (self.ser.is_open):
                packet = self.ser.read_until(b'\x00')
                self.last_raw_packet = packet
                return self.parse_packet(packet)
        except Exception as e:
            #traceback.print_exc()
            pass
        # Return -1 is the serial parse fails
        return -1

    def parse_packet(self, packet):
        if len(packet) > 0:
            packet = self.unstuff_packet(packet)
            #print(packet)
            # TODO: modify packet header to include origin packet
            board_addr = self.get_board_addr_from_packet(packet)
            #print("board_addr:", board_addr)
            try:
                self.board_parser[board_addr].parse_packet(packet)
                self.unpack_valves(board_addr)
                # print(self.parser.dict)
                return board_addr
            except Exception as e:
                #traceback.print_exc()
                print("Packet lost with error ", e)

        # Return -2 if the packet parse fails
        return -2

    def init_valves(self):
        for board_addr in range(len(self.board_parser)):
            if self.board_parser[board_addr]:
                valve_prefix = "vlv"
                vlvs_list = [key for key in self.board_parser[board_addr].items
                                    if key.startswith(valve_prefix)]
                num_valves = -1
                for key in vlvs_list: # dont assume greatest vlv in list is last
                    vlv_num = str(key.split(".")[0])[3:] # get vlv num
                    vlv_num = int(vlv_num)
                    if (vlv_num > num_valves):
                        num_valves = vlv_num
                num_valves += 1
                self.num_valves[board_addr] = num_valves
                self.board_parser[board_addr].num_items += num_valves # update num items in array
                for n in range(0, num_valves):
                    valve_name = 'vlv' + str(n) + '.en'
                    self.board_parser[board_addr].items.append(valve_name)
                    self.board_parser[board_addr].units[valve_name] = 'ul'
        #print(self.num_valves)

    def init_motors(self):
        for board_addr in range(len(self.board_parser)):
            if self.board_parser[board_addr]:
                motor_prefix = "mtr"
                mtrs_list = [key for key in self.board_parser[board_addr].items
                                    if key.startswith(motor_prefix)]
                num_motors = -1
                for key in mtrs_list: # dont assume greatest vlv in list is last
                    mtr_num = str(key)[3:4] # get vlv num
                    mtr_num = int(mtr_num)
                    if (mtr_num > num_motors):
                        num_motors = mtr_num
                num_motors += 1
                self.num_motors[board_addr] = num_motors
        #print(self.num_motors)

    def init_tanks(self):
        for board_addr in range(len(self.board_parser)):
            if self.board_parser[board_addr]:
                tank_prefix = "tnk"
                tnks_list = [key for key in self.board_parser[board_addr].items
                                    if key.startswith(tank_prefix)]
                num_tanks = -1
                for key in tnks_list: # dont assume greatest vlv in list is last
                    tnk_num = str(key)[3:4] # get vlv num
                    tnk_num = int(tnk_num)
                    if (tnk_num > num_tanks):
                        num_tanks = tnk_num
                num_tanks += 1
                self.num_tanks[board_addr] = num_tanks
        #print(self.num_tanks)


    # Unpack valves and generates valves key in dict
    def unpack_valves(self, board_addr=3):
        valve_states = int(self.board_parser[board_addr].dict["valve_states"])
        mask = 1
        for n in range(0, self.num_valves[board_addr]):
            state = 0
            if (mask & valve_states):
                state = 1
            valve_name = 'vlv' + str(n) + '.en'
            self.board_parser[board_addr].dict[valve_name] = int(state)
            mask = mask << 1

    """
    Reads a byte array and returns an integer array (for debugging)
    """
    def bytes_to_array(self, bytes):
        array = [0]*len(bytes)

        for i in range(len(bytes)):
            array[i] = int(struct.unpack("<B", bytes[i:i+1])[0])

        return array

    def get_board_addr_from_packet(self, packet):
        board_addr = int((float(struct.unpack("<B", packet[1:2])[0]))/1)
        #print("addr ", board_addr)
        return board_addr

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
                #print(unstuffed, temp)
                unstuffed = unstuffed + bytes(temp)
            #print(self.bytes_to_array(unstuffed))
            packet = unstuffed
            return packet
        except Exception as e:
            print("error in unstuff_packet ", e)
            #traceback.print_exc()

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
        return self.helper.cmd_names_dict

    """
    Getter function that returns a dictionary mapping a command's packet_type ID to a list of tuples
    containing function arguments in the order (arg_name, arg_type, xmit_scale)
    """
    def get_cmd_args_dict(self):
        return self.helper.cmd_args_dict

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

                while(readfile):
                    # Read the flash page (2048 bytes)
                    ser_page = self.ser.read(2048)
                    if (len(ser_page) != 2048):
                        readfile = False
                    else:
                        binfile.write(bytes(ser_page))  # Log to bin
        except Exception as e:
            print("Error: could not open file to write flash contents because of error ", e)
        telem_info["args"] = [0]
        self.s2_command(telem_info)
        print("Finished downloading flash data to " + os.path.join(datadir, filename))

        # Convert binary file to csv
        try:
            print("Converting "+filename+"...", end='')
            self.binparse.bin2csv(filename=os.path.join(datadir, filename), verbose=False)
            print(" done.")
        except Exception as e:
            print("Error when converting binary file to csv ", e)
            traceback.print_exc()

    """
    Returns the board address given a board name
    """
    def getBoardAddr(self, name):
        #print(name)
        mapping = {
            "Engine Controller": 2,
            "Flight Computer": 1,
            "Pressurization Controller": 3,
            "Recovery Controller": 4,
            "GSE Controller": 0,
            "Black Box": 5
        }
        return mapping[name]

    def getName(self, num):
        mapping = ["GSE Controller", "Flight Computer", "Engine Controller", "Pressurization Controller", "Recovery Controller", "Black Box"]
        return mapping[num]

    def getPrefix(self, name):
        mapping = {
            "Engine Controller": "ec.",
            "Flight Computer": "fc.",
            "Pressurization Controller": "press.",
            "Recovery Controller": "rec.",
            "GSE Controller": "gse.",
            "Black Box": "bb."
        }
        return mapping[name]

    def get_header(self):
        header = ""
        for channel in self.channels:
            header += "%s (%s)," % (channel, self.units[channel])
        header += "\n"
        return header


