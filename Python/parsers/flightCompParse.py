### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### telemParse.py
### Autogenerated by firmware-libraries/SerialComms/python/telem_file_generator.py on Wed Mar  3 19:46:57 2021

import time
import struct

class FlightComputer:

	def __init__(self):
		self.packet_byte_size = 107
		self.num_items = 51
		
		self.dict = {}
		self.units = {}
		
		self.items = [''] * self.num_items
		self.items[0] = 'packet_type'
		self.items[1] = 'origin_addr'
		self.items[2] = 'target_addr'
		self.items[3] = 'priority'
		self.items[4] = 'num_packets'
		self.items[5] = 'do_cobbs'
		self.items[6] = 'checksum'
		self.items[7] = 'timestamp'
		self.items[8] = 'valve_states' 
		self.items[9] = 'e_batt' 
		self.items[10] = 'STATE' 
		self.items[11] = 'vlv0.e' 
		self.items[12] = 'vlv1.e' 
		self.items[13] = 'vlv2.e' 
		self.items[14] = 'vlv3.e' 
		self.items[15] = 'vlv4.e' 
		self.items[16] = 'vlv5.e' 
		self.items[17] = 'vlv6.e' 
		self.items[18] = 'e3v' 
		self.items[19] = 'last_command_id' 
		self.items[20] = 'elapsed_test_duration' 
		self.items[21] = 'micros' 
		self.items[22] = 'telem_rate' 
		self.items[23] = 'adc_rate' 
		self.items[24] = 'flash_mem' 
		self.items[25] = 'own_board_addr' 
		self.items[26] = 'baro.alt' 
		self.items[27] = 'gyro0.x' 
		self.items[28] = 'gyro1.x' 
		self.items[29] = 'gyro2.x' 
		self.items[30] = 'gyro3.x' 
		self.items[31] = 'gyro4.x' 
		self.items[32] = 'gyro5.x' 
		self.items[33] = 'gyro0.y' 
		self.items[34] = 'gyro1.y' 
		self.items[35] = 'gyro2.y' 
		self.items[36] = 'gyro3.y' 
		self.items[37] = 'gyro4.y' 
		self.items[38] = 'gyro5.y' 
		self.items[39] = 'gyro0.z' 
		self.items[40] = 'gyro1.z' 
		self.items[41] = 'gyro2.z' 
		self.items[42] = 'gyro3.z' 
		self.items[43] = 'gyro4.z' 
		self.items[44] = 'gyro5.z' 
		self.items[45] = 'accel.x' 
		self.items[46] = 'accel.y' 
		self.items[47] = 'accel.z' 
		self.items[48] = 'gyro.x.avg' 
		self.items[49] = 'gyro.y.avg' 
		self.items[50] = 'gyro.z.avg' 

		self.units[self.items[0]] = "ul"
		self.units[self.items[1]] = "ul"
		self.units[self.items[2]] = "ul"
		self.units[self.items[3]] = "ul"
		self.units[self.items[4]] = "ul"
		self.units[self.items[5]] = "ul"
		self.units[self.items[6]] = "ul"
		self.units[self.items[7]] = "ul"
		self.units[self.items[8]] = "ul"
		self.units[self.items[9]] = "Volts"
		self.units[self.items[10]] = "ul"
		self.units[self.items[11]] = "Volts"
		self.units[self.items[12]] = "Volts"
		self.units[self.items[13]] = "Volts"
		self.units[self.items[14]] = "Volts"
		self.units[self.items[15]] = "Volts"
		self.units[self.items[16]] = "Volts"
		self.units[self.items[17]] = "Volts"
		self.units[self.items[18]] = "Volts"
		self.units[self.items[19]] = "ul"
		self.units[self.items[20]] = "ms"
		self.units[self.items[21]] = "us"
		self.units[self.items[22]] = "Hz"
		self.units[self.items[23]] = "Hz"
		self.units[self.items[24]] = "bytes"
		self.units[self.items[25]] = "ul"
		self.units[self.items[26]] = "ft"
		self.units[self.items[27]] = "deg/s"
		self.units[self.items[28]] = "deg/s"
		self.units[self.items[29]] = "deg/s"
		self.units[self.items[30]] = "deg/s"
		self.units[self.items[31]] = "deg/s"
		self.units[self.items[32]] = "deg/s"
		self.units[self.items[33]] = "deg/s"
		self.units[self.items[34]] = "deg/s"
		self.units[self.items[35]] = "deg/s"
		self.units[self.items[36]] = "deg/s"
		self.units[self.items[37]] = "deg/s"
		self.units[self.items[38]] = "deg/s"
		self.units[self.items[39]] = "deg/s"
		self.units[self.items[40]] = "deg/s"
		self.units[self.items[41]] = "deg/s"
		self.units[self.items[42]] = "deg/s"
		self.units[self.items[43]] = "deg/s"
		self.units[self.items[44]] = "deg/s"
		self.units[self.items[45]] = "g"
		self.units[self.items[46]] = "g"
		self.units[self.items[47]] = "g"
		self.units[self.items[48]] = "deg/s"
		self.units[self.items[49]] = "deg/s"
		self.units[self.items[50]] = "deg/s"

	def parse_packet(self, packet):
		self.dict[self.items[0]] = int((float(struct.unpack("<B", packet[0:1])[0]))/1)
		self.dict[self.items[1]] = int((float(struct.unpack("<B", packet[1:2])[0]))/1)
		self.dict[self.items[2]] = int((float(struct.unpack("<B", packet[2:3])[0]))/1)
		self.dict[self.items[3]] = int((float(struct.unpack("<B", packet[3:4])[0]))/1)
		self.dict[self.items[4]] = int((float(struct.unpack("<B", packet[4:5])[0]))/1)
		self.dict[self.items[5]] = int((float(struct.unpack("<B", packet[5:6])[0]))/1)
		self.dict[self.items[6]] = int((float(struct.unpack("<H", packet[6:8])[0]))/1)
		self.dict[self.items[7]] = int((float(struct.unpack("<I", packet[8:12])[0]))/1)
		self.dict[self.items[8]] = int((float(struct.unpack("<I", packet[12:16])[0]))/1)
		self.dict[self.items[9]] = float((float(struct.unpack("<h", packet[16:18])[0]))/100)
		self.dict[self.items[10]] = int((float(struct.unpack("<B", packet[18:19])[0]))/1)
		self.dict[self.items[11]] = float((float(struct.unpack("<B", packet[19:20])[0]))/10)
		self.dict[self.items[12]] = float((float(struct.unpack("<B", packet[20:21])[0]))/10)
		self.dict[self.items[13]] = float((float(struct.unpack("<B", packet[21:22])[0]))/10)
		self.dict[self.items[14]] = float((float(struct.unpack("<B", packet[22:23])[0]))/10)
		self.dict[self.items[15]] = float((float(struct.unpack("<B", packet[23:24])[0]))/10)
		self.dict[self.items[16]] = float((float(struct.unpack("<B", packet[24:25])[0]))/10)
		self.dict[self.items[17]] = float((float(struct.unpack("<B", packet[25:26])[0]))/10)
		self.dict[self.items[18]] = float((float(struct.unpack("<i", packet[26:30])[0]))/100)
		self.dict[self.items[19]] = float((float(struct.unpack("<H", packet[30:32])[0]))/1)
		self.dict[self.items[20]] = int((float(struct.unpack("<I", packet[32:36])[0]))/1)
		self.dict[self.items[21]] = int((float(struct.unpack("<Q", packet[36:44])[0]))/1)
		self.dict[self.items[22]] = int((float(struct.unpack("<I", packet[44:48])[0]))/1)
		self.dict[self.items[23]] = int((float(struct.unpack("<I", packet[48:52])[0]))/1)
		self.dict[self.items[24]] = int((float(struct.unpack("<I", packet[52:56])[0]))/1)
		self.dict[self.items[25]] = int((float(struct.unpack("<B", packet[56:57])[0]))/1)
		self.dict[self.items[26]] = int((float(struct.unpack("<H", packet[57:59])[0]))/1)
		self.dict[self.items[27]] = float((float(struct.unpack("<h", packet[59:61])[0]))/10)
		self.dict[self.items[28]] = float((float(struct.unpack("<h", packet[61:63])[0]))/10)
		self.dict[self.items[29]] = float((float(struct.unpack("<h", packet[63:65])[0]))/10)
		self.dict[self.items[30]] = float((float(struct.unpack("<h", packet[65:67])[0]))/10)
		self.dict[self.items[31]] = float((float(struct.unpack("<h", packet[67:69])[0]))/10)
		self.dict[self.items[32]] = float((float(struct.unpack("<h", packet[69:71])[0]))/10)
		self.dict[self.items[33]] = float((float(struct.unpack("<h", packet[71:73])[0]))/10)
		self.dict[self.items[34]] = float((float(struct.unpack("<h", packet[73:75])[0]))/10)
		self.dict[self.items[35]] = float((float(struct.unpack("<h", packet[75:77])[0]))/10)
		self.dict[self.items[36]] = float((float(struct.unpack("<h", packet[77:79])[0]))/10)
		self.dict[self.items[37]] = float((float(struct.unpack("<h", packet[79:81])[0]))/10)
		self.dict[self.items[38]] = float((float(struct.unpack("<h", packet[81:83])[0]))/10)
		self.dict[self.items[39]] = float((float(struct.unpack("<h", packet[83:85])[0]))/10)
		self.dict[self.items[40]] = float((float(struct.unpack("<h", packet[85:87])[0]))/10)
		self.dict[self.items[41]] = float((float(struct.unpack("<h", packet[87:89])[0]))/10)
		self.dict[self.items[42]] = float((float(struct.unpack("<h", packet[89:91])[0]))/10)
		self.dict[self.items[43]] = float((float(struct.unpack("<h", packet[91:93])[0]))/10)
		self.dict[self.items[44]] = float((float(struct.unpack("<h", packet[93:95])[0]))/10)
		self.dict[self.items[45]] = float((float(struct.unpack("<h", packet[95:97])[0]))/100)
		self.dict[self.items[46]] = float((float(struct.unpack("<h", packet[97:99])[0]))/100)
		self.dict[self.items[47]] = float((float(struct.unpack("<h", packet[99:101])[0]))/100)
		self.dict[self.items[48]] = float((float(struct.unpack("<h", packet[101:103])[0]))/10)
		self.dict[self.items[49]] = float((float(struct.unpack("<h", packet[103:105])[0]))/10)
		self.dict[self.items[50]] = float((float(struct.unpack("<h", packet[105:107])[0]))/10)