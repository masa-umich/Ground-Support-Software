### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### _s2InterfaceAutogen.py
### Autogenerated by firmware-libraries/SerialComms/python/cmd_file_generator.py on Sat Apr 24 01:18:39 2021

import serial

class _S2_InterfaceAutogen:
	def __init__(self):
		# A dictionary mapping command name to packet_type (command ID)
		self.cmd_names_dict = {
			"set_vlv"	:	8,
			"send_telem_short"	:	9,
			"send_telem_all"	:	10,
			"set_stepper_period"	:	11,
			"set_stepper_direction"	:	12,
			"set_kp"	:	13,
			"set_ki"	:	14,
			"set_kd"	:	15,
			"set_control_calc_period"	:	16,
			"set_state"	:	17,
			"move_stepper_degrees"	:	18,
			"download_flash"	:	19,
			"wipe_flash"	:	20,
			"start_logging"	:	21,
			"stop_logging"	:	22,
			"set_stepper_pos"	:	23,
			"set_stepper_zero"	:	24,
			"set_control_target_pressure"	:	25,
			"ambientize_pressure_transducers"	:	26,
			"set_low_toggle_percent"	:	27,
			"set_high_toggle_percent"	:	28,
			"set_control_loop_duration"	:	29,
			"set_stepper_speed"	:	30,
			"set_telem"	:	31,
			"set_presstank_status"	:	32,
			"ambientize_pot"	:	33,
			"led_write"	:	34,
			"tare_load_cells"	:	35,
			"set_system_clock"	:	36
		}

		# A dictionary mapping packet_type (command ID) to a list of function argument information.
		# The nth tuple in each list corresponds to the nth argument for that command's function,
		# in the order (arg_name, arg_type, xmit_scale)
		self.cmd_args_dict = {
			8	:	[('vlv_num', 'uint32_t', 1), ('state', 'uint8_t', 1)],
			9	:	[('board_num', 'uint8_t', 1)],
			10	:	[('board_num', 'uint8_t', 1)],
			11	:	[('stepper_num', 'uint8_t', 1), ('period', 'uint16_t', 1)],
			12	:	[('stepper_num', 'uint8_t', 1), ('direction', 'int8_t', 1)],
			13	:	[('motor_num', 'uint8_t', 1), ('gain', 'double', 100)],
			14	:	[('motor_num', 'uint8_t', 1), ('gain', 'double', 100)],
			15	:	[('motor_num', 'uint8_t', 1), ('gain', 'double', 100)],
			16	:	[('period', 'uint8_t', 1)],
			17	:	[('next_state', 'uint8_t', 1)],
			18	:	[('motor_num', 'uint8_t', 1), ('deg', 'uint16_t', 1)],
			19	:	[],
			20	:	[],
			21	:	[],
			22	:	[],
			23	:	[('motor_num', 'uint8_t', 1), ('position', 'float', 100)],
			24	:	[('motor_num', 'uint8_t', 1)],
			25	:	[('tank_num', 'uint8_t', 1), ('target_pressure', 'float', 1000)],
			26	:	[],
			27	:	[('tank_num', 'uint8_t', 1), ('lower_threshold_pct', 'float', 1000)],
			28	:	[('tank_num', 'uint8_t', 1), ('upper_threshold_pct', 'float', 1000)],
			29	:	[('duration', 'uint32_t', 1)],
			30	:	[('motor_num', 'uint8_t', 1), ('target_speed', 'uint16_t', 1)],
			31	:	[('state', 'uint8_t', 1)],
			32	:	[('tank_num', 'uint8_t', 1), ('state', 'uint8_t', 1)],
			33	:	[('pot_num', 'uint8_t', 1)],
			34	:	[('led_num', 'uint8_t', 1), ('state', 'uint8_t', 1)],
			35	:	[],
			36	:	[('system_time', 'uint32_t', 1)]
		}

	"""
	Encodes command info and arguments with COBS and transmits them over serial
	@params
		ser (pyserial object)  - serial obejct to write to
		cmd_info (dict)        - dictionary with the following key value pairs:
			"function_name" : function name (string)
			"target_board_addr" : address of board to send command to (integer)
			"timestamp" : time the command was sent (integer)
			"args" : list of arguments to send to the function (list). Size of all arguments combined cannot exceed 242 bytes.
	"""
	def s2_command(self, ser, cmd_info):
		# Check that it's a valid function
		if (cmd_info["function_name"] not in self.cmd_names_dict.keys()):
			print(cmd_info["function_name"] + " is not a valid function name. No command was sent.")
			return

		# Initialize empty packet
		packet = [0]*12 # Header is 12 bytes, will add bytes to fit function arguments

		# Fill first 12 bytes of packet with CLB packet header information
		packet[0] = self.cmd_names_dict[cmd_info["function_name"]]	# packet_type
		packet[1] = 0	# ground computer addr
		packet[2] = cmd_info["target_board_addr"]	# target_addr
		packet[3] = 1	# priority
		packet[4] = 1	# num_packets
		packet[5] = 1	# do_cobbs
		packet[6] = 0	# checksum
		packet[7] = 0	# checksum
		packet[8] = (cmd_info["timestamp"] >> 0) & 0xFF	# timestamp
		packet[9] = (cmd_info["timestamp"] >> 8) & 0xFF	# timestamp
		packet[10] = (cmd_info["timestamp"] >> 16) & 0xFF	# timestamp
		packet[11] = (cmd_info["timestamp"] >> 24) & 0xFF	# timestamp

		# Stuff packet with the function arguments according to the packet_type ID
		command_id = self.cmd_names_dict[cmd_info["function_name"]]
		# set_vlv()
		if (command_id == 8):
			# vlv_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 24) & 0xFF)
			# state
			packet.append((int(cmd_info["args"][1]*1) >> 0) & 0xFF)
		# send_telem_short()
		elif (command_id == 9):
			# board_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
		# send_telem_all()
		elif (command_id == 10):
			# board_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
		# set_stepper_period()
		elif (command_id == 11):
			# stepper_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# period
			packet.append((int(cmd_info["args"][1]*1) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1) >> 8) & 0xFF)
		# set_stepper_direction()
		elif (command_id == 12):
			# stepper_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# direction
			packet.append((int(cmd_info["args"][1]*1) >> 0) & 0xFF)
		# set_kp()
		elif (command_id == 13):
			# motor_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# gain
			packet.append((int(cmd_info["args"][1]*100) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 24) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 32) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 40) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 48) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 56) & 0xFF)
		# set_ki()
		elif (command_id == 14):
			# motor_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# gain
			packet.append((int(cmd_info["args"][1]*100) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 24) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 32) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 40) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 48) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 56) & 0xFF)
		# set_kd()
		elif (command_id == 15):
			# motor_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# gain
			packet.append((int(cmd_info["args"][1]*100) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 24) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 32) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 40) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 48) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 56) & 0xFF)
		# set_control_calc_period()
		elif (command_id == 16):
			# period
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
		# set_state()
		elif (command_id == 17):
			# next_state
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
		# move_stepper_degrees()
		elif (command_id == 18):
			# motor_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# deg
			packet.append((int(cmd_info["args"][1]*1) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1) >> 8) & 0xFF)
		# download_flash()
		elif (command_id == 19):
			pass  # No function arguments
		# wipe_flash()
		elif (command_id == 20):
			pass  # No function arguments
		# start_logging()
		elif (command_id == 21):
			pass  # No function arguments
		# stop_logging()
		elif (command_id == 22):
			pass  # No function arguments
		# set_stepper_pos()
		elif (command_id == 23):
			# motor_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# position
			packet.append((int(cmd_info["args"][1]*100) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][1]*100) >> 24) & 0xFF)
		# set_stepper_zero()
		elif (command_id == 24):
			# motor_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
		# set_control_target_pressure()
		elif (command_id == 25):
			# tank_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# target_pressure
			packet.append((int(cmd_info["args"][1]*1000) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 24) & 0xFF)
		# ambientize_pressure_transducers()
		elif (command_id == 26):
			pass  # No function arguments
		# set_low_toggle_percent()
		elif (command_id == 27):
			# tank_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# lower_threshold_pct
			packet.append((int(cmd_info["args"][1]*1000) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 24) & 0xFF)
		# set_high_toggle_percent()
		elif (command_id == 28):
			# tank_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# upper_threshold_pct
			packet.append((int(cmd_info["args"][1]*1000) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1000) >> 24) & 0xFF)
		# set_control_loop_duration()
		elif (command_id == 29):
			# duration
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 24) & 0xFF)
		# set_stepper_speed()
		elif (command_id == 30):
			# motor_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# target_speed
			packet.append((int(cmd_info["args"][1]*1) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][1]*1) >> 8) & 0xFF)
		# set_telem()
		elif (command_id == 31):
			# state
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
		# set_presstank_status()
		elif (command_id == 32):
			# tank_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# state
			packet.append((int(cmd_info["args"][1]*1) >> 0) & 0xFF)
		# ambientize_pot()
		elif (command_id == 33):
			# pot_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
		# led_write()
		elif (command_id == 34):
			# led_num
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			# state
			packet.append((int(cmd_info["args"][1]*1) >> 0) & 0xFF)
		# tare_load_cells()
		elif (command_id == 35):
			pass  # No function arguments
		# set_system_clock()
		elif (command_id == 36):
			# system_time
			packet.append((int(cmd_info["args"][0]*1) >> 0) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 8) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 16) & 0xFF)
			packet.append((int(cmd_info["args"][0]*1) >> 24) & 0xFF)

		# Encode the packet with COBS
		stuff_array(packet)

		# Write the bytes to serial
		ser.write(bytes(packet))

"""
Takes in a byte packet and return a COBS encoded version
Note: this was copied directly from the EC3 gui code
@params
	arr (integer array)  - Byte packet to be COBS encoded
	separator (integer)  - Packet delimiter. Should be using 0, but has the option to use any number
"""
def stuff_array(arr, separator=0):
	arr.append(0)
	arr.insert(0, 0)
	first_sep = 1
	for x in arr[1:]:
		if x == separator:
			break
		first_sep += 1
	index = 1
	while(index < len(arr)-1):
		if(arr[index] == separator):
			offset = 1
			while(arr[index+offset] != separator):
				offset += 1
			arr[index] = offset
			index += offset
		else:
			index += 1
	arr[0] = first_sep
	return arr

