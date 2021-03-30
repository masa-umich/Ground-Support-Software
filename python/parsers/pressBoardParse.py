### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### telemParse.py
### Autogenerated by firmware-libraries/SerialComms/python/telem_file_generator.py on Fri Mar 12 12:20:51 2021

import time
import struct

class PressurizationController:

	def __init__(self):
		self.packet_byte_size = 192
		self.num_items = 88
		
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
		self.items[9] = 'pressure[0]' 
		self.items[10] = 'pressure[1]' 
		self.items[11] = 'pressure[2]' 
		self.items[12] = 'pressure[3]' 
		self.items[13] = 'pressure[4]' 
		self.items[14] = 'pressure[5]' 
		self.items[15] = 'e_batt' 
		self.items[16] = 'i_batt' 
		self.items[17] = 'STATE' 
		self.items[18] = 'vlv0.i' 
		self.items[19] = 'vlv1.i' 
		self.items[20] = 'vlv2.i' 
		self.items[21] = 'vlv3.i' 
		self.items[22] = 'vlv4.i' 
		self.items[23] = 'vlv5.i' 
		self.items[24] = 'vlv6.i' 
		self.items[25] = 'vlv7.i' 
		self.items[26] = 'vlv8.i' 
		self.items[27] = 'vlv0.e' 
		self.items[28] = 'vlv1.e' 
		self.items[29] = 'vlv2.e' 
		self.items[30] = 'vlv3.e' 
		self.items[31] = 'vlv4.e' 
		self.items[32] = 'vlv5.e' 
		self.items[33] = 'vlv6.e' 
		self.items[34] = 'vlv7.e' 
		self.items[35] = 'vlv8.e' 
		self.items[36] = 'e3v' 
		self.items[37] = 'e5v' 
		self.items[38] = 'i5v' 
		self.items[39] = 'i3v' 
		self.items[40] = 'last_command_id' 
		self.items[41] = 'tc[0]' 
		self.items[42] = 'tc[1]' 
		self.items[43] = 'tc[2]' 
		self.items[44] = 'tc[3]' 
		self.items[45] = 'tc[4]' 
		self.items[46] = 'mtr0.ia' 
		self.items[47] = 'mtr0.ib' 
		self.items[48] = 'mtr1.ia' 
		self.items[49] = 'mtr1.ib' 
		self.items[50] = 'i_mtr[0]' 
		self.items[51] = 'i_mtr[1]' 
		self.items[52] = 'mtr0.pos' 
		self.items[53] = 'mtr1.pos' 
		self.items[54] = 'mtr0.vel' 
		self.items[55] = 'mtr1.vel' 
		self.items[56] = 'mtr0.set' 
		self.items[57] = 'mtr1.set' 
		self.items[58] = 'mtr0.i' 
		self.items[59] = 'mtr1.i' 
		self.items[60] = 'mtr0.d' 
		self.items[61] = 'mtr1.d' 
		self.items[62] = 'mtr0.p' 
		self.items[63] = 'mtr1.p' 
		self.items[64] = 'mtr0.kp_err' 
		self.items[65] = 'mtr1.kp_err' 
		self.items[66] = 'mtr0.ki_err' 
		self.items[67] = 'mtr1.ki_err' 
		self.items[68] = 'mtr0.kd_err' 
		self.items[69] = 'mtr1.kd_err' 
		self.items[70] = 'tnk0.tp' 
		self.items[71] = 'tnk1.tp' 
		self.items[72] = 'tnk0.hp' 
		self.items[73] = 'tnk1.hp' 
		self.items[74] = 'tnk0.lp' 
		self.items[75] = 'tnk1.lp' 
		self.items[76] = 'mtr0.pot' 
		self.items[77] = 'mtr1.pot' 
		self.items[78] = 'epot[2]' 
		self.items[79] = 'epot[3]' 
		self.items[80] = 'tnk0.en' 
		self.items[81] = 'tnk1.en' 
		self.items[82] = 'test_duration' 
		self.items[83] = 'micros' 
		self.items[84] = 'telem_rate' 
		self.items[85] = 'adc_rate' 
		self.items[86] = 'flash_mem' 
		self.items[87] = 'own_board_addr' 

		self.units[self.items[0]] = "ul"
		self.units[self.items[1]] = "ul"
		self.units[self.items[2]] = "ul"
		self.units[self.items[3]] = "ul"
		self.units[self.items[4]] = "ul"
		self.units[self.items[5]] = "ul"
		self.units[self.items[6]] = "ul"
		self.units[self.items[7]] = "ul"
		self.units[self.items[8]] = "ul"
		self.units[self.items[9]] = "psi"
		self.units[self.items[10]] = "psi"
		self.units[self.items[11]] = "psi"
		self.units[self.items[12]] = "psi"
		self.units[self.items[13]] = "psi"
		self.units[self.items[14]] = "psi"
		self.units[self.items[15]] = "Volts"
		self.units[self.items[16]] = "Amps"
		self.units[self.items[17]] = "ul"
		self.units[self.items[18]] = "Amps"
		self.units[self.items[19]] = "Amps"
		self.units[self.items[20]] = "Amps"
		self.units[self.items[21]] = "Amps"
		self.units[self.items[22]] = "Amps"
		self.units[self.items[23]] = "Amps"
		self.units[self.items[24]] = "Amps"
		self.units[self.items[25]] = "Amps"
		self.units[self.items[26]] = "Amps"
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
		self.units[self.items[37]] = "Volts"
		self.units[self.items[38]] = "Amps"
		self.units[self.items[39]] = "Amps"
		self.units[self.items[40]] = "ul"
		self.units[self.items[41]] = "K"
		self.units[self.items[42]] = "K"
		self.units[self.items[43]] = "K"
		self.units[self.items[44]] = "K"
		self.units[self.items[45]] = "K"
		self.units[self.items[46]] = "Amps"
		self.units[self.items[47]] = "Amps"
		self.units[self.items[48]] = "Amps"
		self.units[self.items[49]] = "Amps"
		self.units[self.items[50]] = "Amps"
		self.units[self.items[51]] = "Amps"
		self.units[self.items[52]] = "deg"
		self.units[self.items[53]] = "deg"
		self.units[self.items[54]] = "step/s"
		self.units[self.items[55]] = "step/s"
		self.units[self.items[56]] = "deg"
		self.units[self.items[57]] = "deg"
		self.units[self.items[58]] = "ul"
		self.units[self.items[59]] = "ul"
		self.units[self.items[60]] = "ul"
		self.units[self.items[61]] = "ul"
		self.units[self.items[62]] = "ul"
		self.units[self.items[63]] = "ul"
		self.units[self.items[64]] = "ul"
		self.units[self.items[65]] = "ul"
		self.units[self.items[66]] = "ul"
		self.units[self.items[67]] = "ul"
		self.units[self.items[68]] = "ul"
		self.units[self.items[69]] = "ul"
		self.units[self.items[70]] = "psi"
		self.units[self.items[71]] = "psi"
		self.units[self.items[72]] = "psi"
		self.units[self.items[73]] = "psi"
		self.units[self.items[74]] = "psi"
		self.units[self.items[75]] = "psi"
		self.units[self.items[76]] = "deg"
		self.units[self.items[77]] = "deg"
		self.units[self.items[78]] = "deg"
		self.units[self.items[79]] = "deg"
		self.units[self.items[80]] = "ul"
		self.units[self.items[81]] = "ul"
		self.units[self.items[82]] = "ms"
		self.units[self.items[83]] = "us"
		self.units[self.items[84]] = "Hz"
		self.units[self.items[85]] = "Hz"
		self.units[self.items[86]] = "bytes"
		self.units[self.items[87]] = "ul"

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
		self.dict[self.items[9]] = float((float(struct.unpack("<h", packet[16:18])[0]))/10)
		self.dict[self.items[10]] = float((float(struct.unpack("<h", packet[18:20])[0]))/10)
		self.dict[self.items[11]] = float((float(struct.unpack("<h", packet[20:22])[0]))/10)
		self.dict[self.items[12]] = float((float(struct.unpack("<h", packet[22:24])[0]))/10)
		self.dict[self.items[13]] = float((float(struct.unpack("<h", packet[24:26])[0]))/10)
		self.dict[self.items[14]] = float((float(struct.unpack("<h", packet[26:28])[0]))/10)
		self.dict[self.items[15]] = float((float(struct.unpack("<h", packet[28:30])[0]))/100)
		self.dict[self.items[16]] = float((float(struct.unpack("<h", packet[30:32])[0]))/100)
		self.dict[self.items[17]] = int((float(struct.unpack("<B", packet[32:33])[0]))/1)
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
		self.dict[self.items[35]] = float((float(struct.unpack("<B", packet[50:51])[0]))/10)
		self.dict[self.items[36]] = float((float(struct.unpack("<i", packet[51:55])[0]))/100)
		self.dict[self.items[37]] = float((float(struct.unpack("<i", packet[55:59])[0]))/100)
		self.dict[self.items[38]] = float((float(struct.unpack("<B", packet[59:60])[0]))/100)
		self.dict[self.items[39]] = float((float(struct.unpack("<B", packet[60:61])[0]))/100)
		self.dict[self.items[40]] = float((float(struct.unpack("<H", packet[61:63])[0]))/1)
		self.dict[self.items[41]] = float((float(struct.unpack("<H", packet[63:65])[0]))/100)
		self.dict[self.items[42]] = float((float(struct.unpack("<H", packet[65:67])[0]))/100)
		self.dict[self.items[43]] = float((float(struct.unpack("<H", packet[67:69])[0]))/100)
		self.dict[self.items[44]] = float((float(struct.unpack("<H", packet[69:71])[0]))/100)
		self.dict[self.items[45]] = float((float(struct.unpack("<H", packet[71:73])[0]))/100)
		self.dict[self.items[46]] = float((float(struct.unpack("<H", packet[73:75])[0]))/100)
		self.dict[self.items[47]] = float((float(struct.unpack("<H", packet[75:77])[0]))/100)
		self.dict[self.items[48]] = float((float(struct.unpack("<H", packet[77:79])[0]))/100)
		self.dict[self.items[49]] = float((float(struct.unpack("<H", packet[79:81])[0]))/100)
		self.dict[self.items[50]] = float((float(struct.unpack("<H", packet[81:83])[0]))/100)
		self.dict[self.items[51]] = float((float(struct.unpack("<H", packet[83:85])[0]))/100)
		self.dict[self.items[52]] = float((float(struct.unpack("<h", packet[85:87])[0]))/10)
		self.dict[self.items[53]] = float((float(struct.unpack("<h", packet[87:89])[0]))/10)
		self.dict[self.items[54]] = int((float(struct.unpack("<h", packet[89:91])[0]))/1)
		self.dict[self.items[55]] = int((float(struct.unpack("<h", packet[91:93])[0]))/1)
		self.dict[self.items[56]] = float((float(struct.unpack("<i", packet[93:97])[0]))/100)
		self.dict[self.items[57]] = float((float(struct.unpack("<i", packet[97:101])[0]))/100)
		self.dict[self.items[58]] = float((float(struct.unpack("<H", packet[101:103])[0]))/10)
		self.dict[self.items[59]] = float((float(struct.unpack("<H", packet[103:105])[0]))/10)
		self.dict[self.items[60]] = float((float(struct.unpack("<H", packet[105:107])[0]))/10)
		self.dict[self.items[61]] = float((float(struct.unpack("<H", packet[107:109])[0]))/10)
		self.dict[self.items[62]] = float((float(struct.unpack("<H", packet[109:111])[0]))/10)
		self.dict[self.items[63]] = float((float(struct.unpack("<H", packet[111:113])[0]))/10)
		self.dict[self.items[64]] = float((float(struct.unpack("<h", packet[113:115])[0]))/10)
		self.dict[self.items[65]] = float((float(struct.unpack("<h", packet[115:117])[0]))/10)
		self.dict[self.items[66]] = float((float(struct.unpack("<h", packet[117:119])[0]))/10)
		self.dict[self.items[67]] = float((float(struct.unpack("<h", packet[119:121])[0]))/10)
		self.dict[self.items[68]] = float((float(struct.unpack("<h", packet[121:123])[0]))/10)
		self.dict[self.items[69]] = float((float(struct.unpack("<h", packet[123:125])[0]))/10)
		self.dict[self.items[70]] = float((float(struct.unpack("<i", packet[125:129])[0]))/100)
		self.dict[self.items[71]] = float((float(struct.unpack("<i", packet[129:133])[0]))/100)
		self.dict[self.items[72]] = float((float(struct.unpack("<i", packet[133:137])[0]))/100)
		self.dict[self.items[73]] = float((float(struct.unpack("<i", packet[137:141])[0]))/100)
		self.dict[self.items[74]] = float((float(struct.unpack("<i", packet[141:145])[0]))/100)
		self.dict[self.items[75]] = float((float(struct.unpack("<i", packet[145:149])[0]))/100)
		self.dict[self.items[76]] = float((float(struct.unpack("<i", packet[149:153])[0]))/10)
		self.dict[self.items[77]] = float((float(struct.unpack("<i", packet[153:157])[0]))/10)
		self.dict[self.items[78]] = float((float(struct.unpack("<i", packet[157:161])[0]))/10)
		self.dict[self.items[79]] = float((float(struct.unpack("<i", packet[161:165])[0]))/10)
		self.dict[self.items[80]] = int((float(struct.unpack("<B", packet[165:166])[0]))/1)
		self.dict[self.items[81]] = int((float(struct.unpack("<B", packet[166:167])[0]))/1)
		self.dict[self.items[82]] = int((float(struct.unpack("<I", packet[167:171])[0]))/1)
		self.dict[self.items[83]] = int((float(struct.unpack("<Q", packet[171:179])[0]))/1)
		self.dict[self.items[84]] = int((float(struct.unpack("<I", packet[179:183])[0]))/1)
		self.dict[self.items[85]] = int((float(struct.unpack("<I", packet[183:187])[0]))/1)
		self.dict[self.items[86]] = int((float(struct.unpack("<I", packet[187:191])[0]))/1)
		self.dict[self.items[87]] = int((float(struct.unpack("<B", packet[191:192])[0]))/1)