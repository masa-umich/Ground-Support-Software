### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### telemParse.py
### Autogenerated by firmware-libraries/SerialComms/python/telem_file_generator.py on Sat Jan  9 21:34:22 2021

import time
import struct

class TelemParse:

	def __init__(self):
		self.csv_header = "Time (s),valve_states (ul),pressure[0] (counts),pressure[1] (counts),pressure[2] (counts),pressure[3] (counts),pressure[4] (counts),pressure[5] (counts),e_batt (Volts),i_batt (Amps),STATE (ul),vlv0.i (Amps),vlv1.i (Amps),vlv2.i (Amps),vlv3.i (Amps),vlv4.i (Amps),vlv5.i (Amps),vlv6.i (Amps),vlv7.i (Amps),vlv8.i (Amps),vlv0.e (Volts),vlv1.e (Volts),vlv2.e (Volts),vlv3.e (Volts),vlv4.e (Volts),vlv5.e (Volts),vlv6.e (Volts),vlv7.e (Volts),vlv8.e (Volts),e3v (Volts),e5v (Volts),i5v (amps),i3v (amps),last_command_id (ul),tc[0] (K),tc[1] (K),tc[2] (K),tc[3] (K),tc[4] (K),i_mtr_ab[0] (amps),i_mtr_ab[1] (amps),i_mtr_ab[2] (amps),i_mtr_ab[3] (amps),i_mtr[0] (amps),i_mtr[1] (amps),epot[0] (Volts),epot[1] (Volts),epot[2] (Volts),epot[3] (Volts),micros (us),telem_rate (ms),adc_rate (ms),own_board_addr (ul),\n"
		self.log_string = ""
		self.num_items = 59
		
		self.dict = {}
		self.units = {}
		
		self.items = [''] * self.num_items
		self.items[0] = 'packet_type'
		self.items[1] = 'target_addr'
		self.items[2] = 'priority'
		self.items[3] = 'num_packets'
		self.items[4] = 'do_cobbs'
		self.items[5] = 'checksum'
		self.items[6] = 'timestamp'
		self.items[7] = 'valve_states' 
		self.items[8] = 'pressure[0]' 
		self.items[9] = 'pressure[1]' 
		self.items[10] = 'pressure[2]' 
		self.items[11] = 'pressure[3]' 
		self.items[12] = 'pressure[4]' 
		self.items[13] = 'pressure[5]' 
		self.items[14] = 'e_batt' 
		self.items[15] = 'i_batt' 
		self.items[16] = 'STATE' 
		self.items[17] = 'vlv0.i' 
		self.items[18] = 'vlv1.i' 
		self.items[19] = 'vlv2.i' 
		self.items[20] = 'vlv3.i' 
		self.items[21] = 'vlv4.i' 
		self.items[22] = 'vlv5.i' 
		self.items[23] = 'vlv6.i' 
		self.items[24] = 'vlv7.i' 
		self.items[25] = 'vlv8.i' 
		self.items[26] = 'vlv0.e' 
		self.items[27] = 'vlv1.e' 
		self.items[28] = 'vlv2.e' 
		self.items[29] = 'vlv3.e' 
		self.items[30] = 'vlv4.e' 
		self.items[31] = 'vlv5.e' 
		self.items[32] = 'vlv6.e' 
		self.items[33] = 'vlv7.e' 
		self.items[34] = 'vlv8.e' 
		self.items[35] = 'e3v' 
		self.items[36] = 'e5v' 
		self.items[37] = 'i5v' 
		self.items[38] = 'i3v' 
		self.items[39] = 'last_command_id' 
		self.items[40] = 'tc[0]' 
		self.items[41] = 'tc[1]' 
		self.items[42] = 'tc[2]' 
		self.items[43] = 'tc[3]' 
		self.items[44] = 'tc[4]' 
		self.items[45] = 'i_mtr_ab[0]' 
		self.items[46] = 'i_mtr_ab[1]' 
		self.items[47] = 'i_mtr_ab[2]' 
		self.items[48] = 'i_mtr_ab[3]' 
		self.items[49] = 'i_mtr[0]' 
		self.items[50] = 'i_mtr[1]' 
		self.items[51] = 'epot[0]' 
		self.items[52] = 'epot[1]' 
		self.items[53] = 'epot[2]' 
		self.items[54] = 'epot[3]' 
		self.items[55] = 'micros' 
		self.items[56] = 'telem_rate' 
		self.items[57] = 'adc_rate' 
		self.items[58] = 'own_board_addr' 
		self.units[self.items[7]] = "ul"
		self.units[self.items[8]] = "counts"
		self.units[self.items[9]] = "counts"
		self.units[self.items[10]] = "counts"
		self.units[self.items[11]] = "counts"
		self.units[self.items[12]] = "counts"
		self.units[self.items[13]] = "counts"
		self.units[self.items[14]] = "Volts"
		self.units[self.items[15]] = "Amps"
		self.units[self.items[16]] = "ul"
		self.units[self.items[17]] = "Amps"
		self.units[self.items[18]] = "Amps"
		self.units[self.items[19]] = "Amps"
		self.units[self.items[20]] = "Amps"
		self.units[self.items[21]] = "Amps"
		self.units[self.items[22]] = "Amps"
		self.units[self.items[23]] = "Amps"
		self.units[self.items[24]] = "Amps"
		self.units[self.items[25]] = "Amps"
		self.units[self.items[26]] = "Volts"
		self.units[self.items[27]] = "Volts"
		self.units[self.items[28]] = "Volts"
		self.units[self.items[29]] = "Volts"
		self.units[self.items[30]] = "Volts"
		self.units[self.items[31]] = "Volts"
		self.units[self.items[32]] = "Volts"
		self.units[self.items[33]] = "Volts"
		self.units[self.items[34]] = "Volts"
		self.units[self.items[35]] = "Volts"
		self.units[self.items[36]] = "Volts"
		self.units[self.items[37]] = "amps"
		self.units[self.items[38]] = "amps"
		self.units[self.items[39]] = "ul"
		self.units[self.items[40]] = "K"
		self.units[self.items[41]] = "K"
		self.units[self.items[42]] = "K"
		self.units[self.items[43]] = "K"
		self.units[self.items[44]] = "K"
		self.units[self.items[45]] = "amps"
		self.units[self.items[46]] = "amps"
		self.units[self.items[47]] = "amps"
		self.units[self.items[48]] = "amps"
		self.units[self.items[49]] = "amps"
		self.units[self.items[50]] = "amps"
		self.units[self.items[51]] = "Volts"
		self.units[self.items[52]] = "Volts"
		self.units[self.items[53]] = "Volts"
		self.units[self.items[54]] = "Volts"
		self.units[self.items[55]] = "us"
		self.units[self.items[56]] = "ms"
		self.units[self.items[57]] = "ms"
		self.units[self.items[58]] = "ul"

	def parse_packet(self, packet):
		self.dict[self.items[0]] = int((float(struct.unpack("<B", packet[0:1])[0]))/1)
		self.dict[self.items[1]] = int((float(struct.unpack("<B", packet[1:2])[0]))/1)
		self.dict[self.items[2]] = int((float(struct.unpack("<B", packet[2:3])[0]))/1)
		self.dict[self.items[3]] = int((float(struct.unpack("<B", packet[3:4])[0]))/1)
		self.dict[self.items[4]] = int((float(struct.unpack("<B", packet[4:5])[0]))/1)
		self.dict[self.items[5]] = int((float(struct.unpack("<H", packet[5:7])[0]))/1)
		self.dict[self.items[6]] = int((float(struct.unpack("<I", packet[7:11])[0]))/1)
		self.dict[self.items[7]] = int((float(struct.unpack("<I", packet[11:15])[0]))/1)
		self.dict[self.items[8]] = float((float(struct.unpack("<h", packet[15:17])[0]))/1)
		self.dict[self.items[9]] = float((float(struct.unpack("<h", packet[17:19])[0]))/1)
		self.dict[self.items[10]] = float((float(struct.unpack("<h", packet[19:21])[0]))/1)
		self.dict[self.items[11]] = float((float(struct.unpack("<h", packet[21:23])[0]))/1)
		self.dict[self.items[12]] = float((float(struct.unpack("<h", packet[23:25])[0]))/1)
		self.dict[self.items[13]] = float((float(struct.unpack("<h", packet[25:27])[0]))/1)
		self.dict[self.items[14]] = float((float(struct.unpack("<h", packet[27:29])[0]))/1000)
		self.dict[self.items[15]] = int((float(struct.unpack("<h", packet[29:31])[0]))/100)
		self.dict[self.items[16]] = int((float(struct.unpack("<B", packet[31:32])[0]))/1)
		self.dict[self.items[17]] = float((float(struct.unpack("<B", packet[32:33])[0]))/10)
		self.dict[self.items[18]] = float((float(struct.unpack("<B", packet[33:34])[0]))/10)
		self.dict[self.items[19]] = float((float(struct.unpack("<B", packet[34:35])[0]))/10)
		self.dict[self.items[20]] = float((float(struct.unpack("<B", packet[35:36])[0]))/10)
		self.dict[self.items[21]] = float((float(struct.unpack("<B", packet[36:37])[0]))/10)
		self.dict[self.items[22]] = float((float(struct.unpack("<B", packet[37:38])[0]))/10)
		self.dict[self.items[23]] = float((float(struct.unpack("<B", packet[38:39])[0]))/10)
		self.dict[self.items[24]] = float((float(struct.unpack("<B", packet[39:40])[0]))/10)
		self.dict[self.items[25]] = float((float(struct.unpack("<B", packet[40:41])[0]))/10)
		self.dict[self.items[26]] = float((float(struct.unpack("<B", packet[41:42])[0]))/10)
		self.dict[self.items[27]] = float((float(struct.unpack("<B", packet[42:43])[0]))/10)
		self.dict[self.items[28]] = float((float(struct.unpack("<B", packet[43:44])[0]))/10)
		self.dict[self.items[29]] = float((float(struct.unpack("<B", packet[44:45])[0]))/10)
		self.dict[self.items[30]] = float((float(struct.unpack("<B", packet[45:46])[0]))/10)
		self.dict[self.items[31]] = float((float(struct.unpack("<B", packet[46:47])[0]))/10)
		self.dict[self.items[32]] = float((float(struct.unpack("<B", packet[47:48])[0]))/10)
		self.dict[self.items[33]] = float((float(struct.unpack("<B", packet[48:49])[0]))/10)
		self.dict[self.items[34]] = float((float(struct.unpack("<B", packet[49:50])[0]))/10)
		self.dict[self.items[35]] = float((float(struct.unpack("<i", packet[50:54])[0]))/100)
		self.dict[self.items[36]] = float((float(struct.unpack("<i", packet[54:58])[0]))/100)
		self.dict[self.items[37]] = float((float(struct.unpack("<B", packet[58:59])[0]))/100)
		self.dict[self.items[38]] = float((float(struct.unpack("<B", packet[59:60])[0]))/100)
		self.dict[self.items[39]] = float((float(struct.unpack("<H", packet[60:62])[0]))/100)
		self.dict[self.items[40]] = float((float(struct.unpack("<H", packet[62:64])[0]))/100)
		self.dict[self.items[41]] = float((float(struct.unpack("<H", packet[64:66])[0]))/100)
		self.dict[self.items[42]] = float((float(struct.unpack("<H", packet[66:68])[0]))/100)
		self.dict[self.items[43]] = float((float(struct.unpack("<H", packet[68:70])[0]))/100)
		self.dict[self.items[44]] = float((float(struct.unpack("<H", packet[70:72])[0]))/100)
		self.dict[self.items[45]] = float((float(struct.unpack("<H", packet[72:74])[0]))/100)
		self.dict[self.items[46]] = float((float(struct.unpack("<H", packet[74:76])[0]))/100)
		self.dict[self.items[47]] = float((float(struct.unpack("<H", packet[76:78])[0]))/100)
		self.dict[self.items[48]] = float((float(struct.unpack("<H", packet[78:80])[0]))/100)
		self.dict[self.items[49]] = float((float(struct.unpack("<H", packet[80:82])[0]))/100)
		self.dict[self.items[50]] = float((float(struct.unpack("<H", packet[82:84])[0]))/100)
		self.dict[self.items[51]] = float((float(struct.unpack("<H", packet[84:86])[0]))/1000)
		self.dict[self.items[52]] = float((float(struct.unpack("<H", packet[86:88])[0]))/1000)
		self.dict[self.items[53]] = float((float(struct.unpack("<H", packet[88:90])[0]))/1000)
		self.dict[self.items[54]] = float((float(struct.unpack("<H", packet[90:92])[0]))/1000)
		self.dict[self.items[55]] = int((float(struct.unpack("<Q", packet[92:100])[0]))/1)
		self.dict[self.items[56]] = int((float(struct.unpack("<I", packet[100:104])[0]))/1)
		self.dict[self.items[57]] = int((float(struct.unpack("<I", packet[104:108])[0]))/1)
		self.dict[self.items[58]] = int((float(struct.unpack("<B", packet[108:109])[0]))/1)
		self.log_string = str(time.clock()) + ',' + str(self.dict[self.items[7]]) + ',' + str(self.dict[self.items[8]]) + ',' + str(self.dict[self.items[9]]) + ',' + str(self.dict[self.items[10]]) + ',' + str(self.dict[self.items[11]]) + ',' + str(self.dict[self.items[12]]) + ',' + str(self.dict[self.items[13]]) + ',' + str(self.dict[self.items[14]]) + ',' + str(self.dict[self.items[15]]) + ',' + str(self.dict[self.items[16]]) + ',' + str(self.dict[self.items[17]]) + ',' + str(self.dict[self.items[18]]) + ',' + str(self.dict[self.items[19]]) + ',' + str(self.dict[self.items[20]]) + ',' + str(self.dict[self.items[21]]) + ',' + str(self.dict[self.items[22]]) + ',' + str(self.dict[self.items[23]]) + ',' + str(self.dict[self.items[24]]) + ',' + str(self.dict[self.items[25]]) + ',' + str(self.dict[self.items[26]]) + ',' + str(self.dict[self.items[27]]) + ',' + str(self.dict[self.items[28]]) + ',' + str(self.dict[self.items[29]]) + ',' + str(self.dict[self.items[30]]) + ',' + str(self.dict[self.items[31]]) + ',' + str(self.dict[self.items[32]]) + ',' + str(self.dict[self.items[33]]) + ',' + str(self.dict[self.items[34]]) + ',' + str(self.dict[self.items[35]]) + ',' + str(self.dict[self.items[36]]) + ',' + str(self.dict[self.items[37]]) + ',' + str(self.dict[self.items[38]]) + ',' + str(self.dict[self.items[39]]) + ',' + str(self.dict[self.items[40]]) + ',' + str(self.dict[self.items[41]]) + ',' + str(self.dict[self.items[42]]) + ',' + str(self.dict[self.items[43]]) + ',' + str(self.dict[self.items[44]]) + ',' + str(self.dict[self.items[45]]) + ',' + str(self.dict[self.items[46]]) + ',' + str(self.dict[self.items[47]]) + ',' + str(self.dict[self.items[48]]) + ',' + str(self.dict[self.items[49]]) + ',' + str(self.dict[self.items[50]]) + ',' + str(self.dict[self.items[51]]) + ',' + str(self.dict[self.items[52]]) + ',' + str(self.dict[self.items[53]]) + ',' + str(self.dict[self.items[54]]) + ',' + str(self.dict[self.items[55]]) + ',' + str(self.dict[self.items[56]]) + ',' + str(self.dict[self.items[57]]) + ',' + str(self.dict[self.items[58]]) + ','