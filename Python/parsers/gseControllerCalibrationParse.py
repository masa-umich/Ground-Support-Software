### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### calibrationParse.py
### Autogenerated by firmware-libraries/SerialComms/python/calibration_file_generator.py on Sun Aug 22 17:18:43 2021

import time
import struct

class GSEControllerCalibrations:

	def __init__(self):
		self.packet_byte_size = 144
		self.num_items = 52
		
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
		self.items[8] = 'pt_cal_slope[0]' 
		self.items[9] = 'pt_cal_slope[1]' 
		self.items[10] = 'pt_cal_slope[2]' 
		self.items[11] = 'pt_cal_slope[3]' 
		self.items[12] = 'pt_cal_slope[4]' 
		self.items[13] = 'pt_cal_slope[5]' 
		self.items[14] = 'pt_cal_slope[6]' 
		self.items[15] = 'pt_cal_slope[7]' 
		self.items[16] = 'pt_cal_slope[8]' 
		self.items[17] = 'pt_cal_slope[9]' 
		self.items[18] = 'pt_cal_slope[10]' 
		self.items[19] = 'pt_cal_slope[11]' 
		self.items[20] = 'pt_cal_slope[12]' 
		self.items[21] = 'pt_cal_slope[13]' 
		self.items[22] = 'pt_cal_slope[14]' 
		self.items[23] = 'pt_cal_slope[15]' 
		self.items[24] = 'pt_cal_slope[16]' 
		self.items[25] = 'pt_cal_slope[17]' 
		self.items[26] = 'pt_cal_slope[18]' 
		self.items[27] = 'pt_cal_slope[19]' 
		self.items[28] = 'pt_cal_slope[20]' 
		self.items[29] = 'pt_cal_slope[21]' 
		self.items[30] = 'pt_cal_offset[0]' 
		self.items[31] = 'pt_cal_offset[1]' 
		self.items[32] = 'pt_cal_offset[2]' 
		self.items[33] = 'pt_cal_offset[3]' 
		self.items[34] = 'pt_cal_offset[4]' 
		self.items[35] = 'pt_cal_offset[5]' 
		self.items[36] = 'pt_cal_offset[6]' 
		self.items[37] = 'pt_cal_offset[7]' 
		self.items[38] = 'pt_cal_offset[8]' 
		self.items[39] = 'pt_cal_offset[9]' 
		self.items[40] = 'pt_cal_offset[10]' 
		self.items[41] = 'pt_cal_offset[11]' 
		self.items[42] = 'pt_cal_offset[12]' 
		self.items[43] = 'pt_cal_offset[13]' 
		self.items[44] = 'pt_cal_offset[14]' 
		self.items[45] = 'pt_cal_offset[15]' 
		self.items[46] = 'pt_cal_offset[16]' 
		self.items[47] = 'pt_cal_offset[17]' 
		self.items[48] = 'pt_cal_offset[18]' 
		self.items[49] = 'pt_cal_offset[19]' 
		self.items[50] = 'pt_cal_offset[20]' 
		self.items[51] = 'pt_cal_offset[21]' 

		self.units[self.items[0]] = "ul"
		self.units[self.items[1]] = "ul"
		self.units[self.items[2]] = "ul"
		self.units[self.items[3]] = "ul"
		self.units[self.items[4]] = "ul"
		self.units[self.items[5]] = "ul"
		self.units[self.items[6]] = "ul"
		self.units[self.items[7]] = "ul"
		self.units[self.items[8]] = "mV/psi"
		self.units[self.items[9]] = "mV/psi"
		self.units[self.items[10]] = "mV/psi"
		self.units[self.items[11]] = "mV/psi"
		self.units[self.items[12]] = "mV/psi"
		self.units[self.items[13]] = "mV/psi"
		self.units[self.items[14]] = "mV/psi"
		self.units[self.items[15]] = "mV/psi"
		self.units[self.items[16]] = "mV/psi"
		self.units[self.items[17]] = "mV/psi"
		self.units[self.items[18]] = "mV/psi"
		self.units[self.items[19]] = "mV/psi"
		self.units[self.items[20]] = "mV/psi"
		self.units[self.items[21]] = "mV/psi"
		self.units[self.items[22]] = "mV/psi"
		self.units[self.items[23]] = "mV/psi"
		self.units[self.items[24]] = "mV/psi"
		self.units[self.items[25]] = "mV/psi"
		self.units[self.items[26]] = "mV/psi"
		self.units[self.items[27]] = "mV/psi"
		self.units[self.items[28]] = "mV/psi"
		self.units[self.items[29]] = "mV/psi"
		self.units[self.items[30]] = "mV"
		self.units[self.items[31]] = "mV"
		self.units[self.items[32]] = "mV"
		self.units[self.items[33]] = "mV"
		self.units[self.items[34]] = "mV"
		self.units[self.items[35]] = "mV"
		self.units[self.items[36]] = "mV"
		self.units[self.items[37]] = "mV"
		self.units[self.items[38]] = "mV"
		self.units[self.items[39]] = "mV"
		self.units[self.items[40]] = "mV"
		self.units[self.items[41]] = "mV"
		self.units[self.items[42]] = "mV"
		self.units[self.items[43]] = "mV"
		self.units[self.items[44]] = "mV"
		self.units[self.items[45]] = "mV"
		self.units[self.items[46]] = "mV"
		self.units[self.items[47]] = "mV"
		self.units[self.items[48]] = "mV"
		self.units[self.items[49]] = "mV"
		self.units[self.items[50]] = "mV"
		self.units[self.items[51]] = "mV"

	def parse_packet(self, packet):
		self.dict[self.items[0]] = int((float(struct.unpack("<B", packet[0:1])[0]))/1)
		self.dict[self.items[1]] = int((float(struct.unpack("<B", packet[1:2])[0]))/1)
		self.dict[self.items[2]] = int((float(struct.unpack("<B", packet[2:3])[0]))/1)
		self.dict[self.items[3]] = int((float(struct.unpack("<B", packet[3:4])[0]))/1)
		self.dict[self.items[4]] = int((float(struct.unpack("<B", packet[4:5])[0]))/1)
		self.dict[self.items[5]] = int((float(struct.unpack("<B", packet[5:6])[0]))/1)
		self.dict[self.items[6]] = int((float(struct.unpack("<H", packet[6:8])[0]))/1)
		self.dict[self.items[7]] = int((float(struct.unpack("<I", packet[8:12])[0]))/1)
		self.dict[self.items[8]] = float((float(struct.unpack("<i", packet[12:16])[0]))/10000)
		self.dict[self.items[9]] = float((float(struct.unpack("<i", packet[16:20])[0]))/10000)
		self.dict[self.items[10]] = float((float(struct.unpack("<i", packet[20:24])[0]))/10000)
		self.dict[self.items[11]] = float((float(struct.unpack("<i", packet[24:28])[0]))/10000)
		self.dict[self.items[12]] = float((float(struct.unpack("<i", packet[28:32])[0]))/10000)
		self.dict[self.items[13]] = float((float(struct.unpack("<i", packet[32:36])[0]))/10000)
		self.dict[self.items[14]] = float((float(struct.unpack("<i", packet[36:40])[0]))/10000)
		self.dict[self.items[15]] = float((float(struct.unpack("<i", packet[40:44])[0]))/10000)
		self.dict[self.items[16]] = float((float(struct.unpack("<i", packet[44:48])[0]))/10000)
		self.dict[self.items[17]] = float((float(struct.unpack("<i", packet[48:52])[0]))/10000)
		self.dict[self.items[18]] = float((float(struct.unpack("<i", packet[52:56])[0]))/10000)
		self.dict[self.items[19]] = float((float(struct.unpack("<i", packet[56:60])[0]))/10000)
		self.dict[self.items[20]] = float((float(struct.unpack("<i", packet[60:64])[0]))/10000)
		self.dict[self.items[21]] = float((float(struct.unpack("<i", packet[64:68])[0]))/10000)
		self.dict[self.items[22]] = float((float(struct.unpack("<i", packet[68:72])[0]))/10000)
		self.dict[self.items[23]] = float((float(struct.unpack("<i", packet[72:76])[0]))/10000)
		self.dict[self.items[24]] = float((float(struct.unpack("<i", packet[76:80])[0]))/10000)
		self.dict[self.items[25]] = float((float(struct.unpack("<i", packet[80:84])[0]))/10000)
		self.dict[self.items[26]] = float((float(struct.unpack("<i", packet[84:88])[0]))/10000)
		self.dict[self.items[27]] = float((float(struct.unpack("<i", packet[88:92])[0]))/10000)
		self.dict[self.items[28]] = float((float(struct.unpack("<i", packet[92:96])[0]))/10000)
		self.dict[self.items[29]] = float((float(struct.unpack("<i", packet[96:100])[0]))/10000)
		self.dict[self.items[30]] = float((float(struct.unpack("<h", packet[100:102])[0]))/1)
		self.dict[self.items[31]] = float((float(struct.unpack("<h", packet[102:104])[0]))/1)
		self.dict[self.items[32]] = float((float(struct.unpack("<h", packet[104:106])[0]))/1)
		self.dict[self.items[33]] = float((float(struct.unpack("<h", packet[106:108])[0]))/1)
		self.dict[self.items[34]] = float((float(struct.unpack("<h", packet[108:110])[0]))/1)
		self.dict[self.items[35]] = float((float(struct.unpack("<h", packet[110:112])[0]))/1)
		self.dict[self.items[36]] = float((float(struct.unpack("<h", packet[112:114])[0]))/1)
		self.dict[self.items[37]] = float((float(struct.unpack("<h", packet[114:116])[0]))/1)
		self.dict[self.items[38]] = float((float(struct.unpack("<h", packet[116:118])[0]))/1)
		self.dict[self.items[39]] = float((float(struct.unpack("<h", packet[118:120])[0]))/1)
		self.dict[self.items[40]] = float((float(struct.unpack("<h", packet[120:122])[0]))/1)
		self.dict[self.items[41]] = float((float(struct.unpack("<h", packet[122:124])[0]))/1)
		self.dict[self.items[42]] = float((float(struct.unpack("<h", packet[124:126])[0]))/1)
		self.dict[self.items[43]] = float((float(struct.unpack("<h", packet[126:128])[0]))/1)
		self.dict[self.items[44]] = float((float(struct.unpack("<h", packet[128:130])[0]))/1)
		self.dict[self.items[45]] = float((float(struct.unpack("<h", packet[130:132])[0]))/1)
		self.dict[self.items[46]] = float((float(struct.unpack("<h", packet[132:134])[0]))/1)
		self.dict[self.items[47]] = float((float(struct.unpack("<h", packet[134:136])[0]))/1)
		self.dict[self.items[48]] = float((float(struct.unpack("<h", packet[136:138])[0]))/1)
		self.dict[self.items[49]] = float((float(struct.unpack("<h", packet[138:140])[0]))/1)
		self.dict[self.items[50]] = float((float(struct.unpack("<h", packet[140:142])[0]))/1)
		self.dict[self.items[51]] = float((float(struct.unpack("<h", packet[142:144])[0]))/1)
