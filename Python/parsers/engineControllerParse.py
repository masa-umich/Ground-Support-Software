### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### telemParse.py
### Autogenerated by firmware-libraries/SerialComms/python/telem_file_generator.py on Tue Aug  3 23:38:11 2021

import time
import struct

class EngineController:

	def __init__(self):
		self.packet_byte_size = 253
		self.num_items = 107
		
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
		self.items[8] = 'STATE' 
		self.items[9] = 'e_batt' 
		self.items[10] = 'i_batt' 
		self.items[11] = 'valve_states' 
		self.items[12] = 'e3v' 
		self.items[13] = 'e5v' 
		self.items[14] = 'i5v' 
		self.items[15] = 'i3v' 
		self.items[16] = 'status_flags' 
		self.items[17] = 'pressure[0]' 
		self.items[18] = 'pressure[1]' 
		self.items[19] = 'pressure[2]' 
		self.items[20] = 'pressure[3]' 
		self.items[21] = 'pressure[4]' 
		self.items[22] = 'pressure[5]' 
		self.items[23] = 'pressure[6]' 
		self.items[24] = 'pressure[7]' 
		self.items[25] = 'pressure[8]' 
		self.items[26] = 'pressure[9]' 
		self.items[27] = 'pressure[10]' 
		self.items[28] = 'pressure[11]' 
		self.items[29] = 'pressure[12]' 
		self.items[30] = 'pressure[13]' 
		self.items[31] = 'pressure[14]' 
		self.items[32] = 'pressure[15]' 
		self.items[33] = 'pressure[16]' 
		self.items[34] = 'pressure[17]' 
		self.items[35] = 'pressure[18]' 
		self.items[36] = 'pressure[19]' 
		self.items[37] = 'vlv0.e' 
		self.items[38] = 'vlv1.e' 
		self.items[39] = 'vlv2.e' 
		self.items[40] = 'vlv3.e' 
		self.items[41] = 'vlv4.e' 
		self.items[42] = 'vlv5.e' 
		self.items[43] = 'vlv6.e' 
		self.items[44] = 'vlv7.e' 
		self.items[45] = 'vlv8.e' 
		self.items[46] = 'vlv9.e' 
		self.items[47] = 'vlv10.e' 
		self.items[48] = 'vlv11.e' 
		self.items[49] = 'vlv12.e' 
		self.items[50] = 'vlv13.e' 
		self.items[51] = 'tc[0]' 
		self.items[52] = 'tc[1]' 
		self.items[53] = 'tc[2]' 
		self.items[54] = 'tc[3]' 
		self.items[55] = 'tc[4]' 
		self.items[56] = 'tc[5]' 
		self.items[57] = 'tc[6]' 
		self.items[58] = 'tc[7]' 
		self.items[59] = 'tc[8]' 
		self.items[60] = 'tc[9]' 
		self.items[61] = 'tc[10]' 
		self.items[62] = 'tc[11]' 
		self.items[63] = 'tc[12]' 
		self.items[64] = 'mtr0.pos' 
		self.items[65] = 'mtr1.pos' 
		self.items[66] = 'mtr0.vel' 
		self.items[67] = 'mtr1.vel' 
		self.items[68] = 'mtr0.set' 
		self.items[69] = 'mtr1.set' 
		self.items[70] = 'mtr0.kp' 
		self.items[71] = 'mtr1.kp' 
		self.items[72] = 'mtr0.ki' 
		self.items[73] = 'mtr1.ki' 
		self.items[74] = 'mtr0.kd' 
		self.items[75] = 'mtr1.kd' 
		self.items[76] = 'mtr0.kp_err' 
		self.items[77] = 'mtr1.kp_err' 
		self.items[78] = 'mtr0.ki_err' 
		self.items[79] = 'mtr1.ki_err' 
		self.items[80] = 'mtr0.kd_err' 
		self.items[81] = 'mtr1.kd_err' 
		self.items[82] = 'tnk0.target_pres' 
		self.items[83] = 'tnk1.target_pres' 
		self.items[84] = 'tnk0.high_pres' 
		self.items[85] = 'tnk1.high_pres' 
		self.items[86] = 'tnk0.low_pres' 
		self.items[87] = 'tnk1.low_pres' 
		self.items[88] = 'pot0.e' 
		self.items[89] = 'pot1.e' 
		self.items[90] = 'lox_ctrl_pres' 
		self.items[91] = 'fuel_ctrl_pres' 
		self.items[92] = 'copv_ctrl_pres' 
		self.items[93] = 'tnk0.en' 
		self.items[94] = 'tnk1.en' 
		self.items[95] = 'test_duration' 
		self.items[96] = 'ignitor_on_delay' 
		self.items[97] = 'ignitor_high_duration' 
		self.items[98] = 'fuel_mpv_delay' 
		self.items[99] = 'nozzle_film_cooling_delay' 
		self.items[100] = 'pid_delay' 
		self.items[101] = 'deg_corr_factor' 
		self.items[102] = 'state_rem_duration' 
		self.items[103] = 'telem_rate' 
		self.items[104] = 'adc_rate' 
		self.items[105] = 'flash_mem' 
		self.items[106] = 'LOGGING_ACTIVE' 

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
		self.units[self.items[10]] = "Amps"
		self.units[self.items[11]] = "ul"
		self.units[self.items[12]] = "Volts"
		self.units[self.items[13]] = "Volts"
		self.units[self.items[14]] = "Amps"
		self.units[self.items[15]] = "Amps"
		self.units[self.items[16]] = "ul"
		self.units[self.items[17]] = "psi"
		self.units[self.items[18]] = "psi"
		self.units[self.items[19]] = "psi"
		self.units[self.items[20]] = "psi"
		self.units[self.items[21]] = "psi"
		self.units[self.items[22]] = "psi"
		self.units[self.items[23]] = "psi"
		self.units[self.items[24]] = "psi"
		self.units[self.items[25]] = "psi"
		self.units[self.items[26]] = "psi"
		self.units[self.items[27]] = "psi"
		self.units[self.items[28]] = "psi"
		self.units[self.items[29]] = "psi"
		self.units[self.items[30]] = "psi"
		self.units[self.items[31]] = "psi"
		self.units[self.items[32]] = "psi"
		self.units[self.items[33]] = "psi"
		self.units[self.items[34]] = "psi"
		self.units[self.items[35]] = "psi"
		self.units[self.items[36]] = "psi"
		self.units[self.items[37]] = "Volts"
		self.units[self.items[38]] = "Volts"
		self.units[self.items[39]] = "Volts"
		self.units[self.items[40]] = "Volts"
		self.units[self.items[41]] = "Volts"
		self.units[self.items[42]] = "Volts"
		self.units[self.items[43]] = "Volts"
		self.units[self.items[44]] = "Volts"
		self.units[self.items[45]] = "Volts"
		self.units[self.items[46]] = "Volts"
		self.units[self.items[47]] = "Volts"
		self.units[self.items[48]] = "Volts"
		self.units[self.items[49]] = "Volts"
		self.units[self.items[50]] = "Volts"
		self.units[self.items[51]] = "K"
		self.units[self.items[52]] = "K"
		self.units[self.items[53]] = "K"
		self.units[self.items[54]] = "K"
		self.units[self.items[55]] = "K"
		self.units[self.items[56]] = "K"
		self.units[self.items[57]] = "K"
		self.units[self.items[58]] = "K"
		self.units[self.items[59]] = "K"
		self.units[self.items[60]] = "K"
		self.units[self.items[61]] = "K"
		self.units[self.items[62]] = "K"
		self.units[self.items[63]] = "K"
		self.units[self.items[64]] = "deg"
		self.units[self.items[65]] = "deg"
		self.units[self.items[66]] = "step/s"
		self.units[self.items[67]] = "step/s"
		self.units[self.items[68]] = "deg"
		self.units[self.items[69]] = "deg"
		self.units[self.items[70]] = "ul"
		self.units[self.items[71]] = "ul"
		self.units[self.items[72]] = "ul"
		self.units[self.items[73]] = "ul"
		self.units[self.items[74]] = "ul"
		self.units[self.items[75]] = "ul"
		self.units[self.items[76]] = "ul"
		self.units[self.items[77]] = "ul"
		self.units[self.items[78]] = "ul"
		self.units[self.items[79]] = "ul"
		self.units[self.items[80]] = "ul"
		self.units[self.items[81]] = "ul"
		self.units[self.items[82]] = "psi"
		self.units[self.items[83]] = "psi"
		self.units[self.items[84]] = "psi"
		self.units[self.items[85]] = "psi"
		self.units[self.items[86]] = "psi"
		self.units[self.items[87]] = "psi"
		self.units[self.items[88]] = "deg"
		self.units[self.items[89]] = "deg"
		self.units[self.items[90]] = "psi"
		self.units[self.items[91]] = "psi"
		self.units[self.items[92]] = "psi"
		self.units[self.items[93]] = "ul"
		self.units[self.items[94]] = "ul"
		self.units[self.items[95]] = "ms"
		self.units[self.items[96]] = "ms"
		self.units[self.items[97]] = "ms"
		self.units[self.items[98]] = "ms"
		self.units[self.items[99]] = "ms"
		self.units[self.items[100]] = "ms"
		self.units[self.items[101]] = "ul"
		self.units[self.items[102]] = "ms"
		self.units[self.items[103]] = "Hz"
		self.units[self.items[104]] = "Hz"
		self.units[self.items[105]] = "bytes"
		self.units[self.items[106]] = "ul"

	def parse_packet(self, packet):
		self.dict[self.items[0]] = int((float(struct.unpack("<B", packet[0:1])[0]))/1)
		self.dict[self.items[1]] = int((float(struct.unpack("<B", packet[1:2])[0]))/1)
		self.dict[self.items[2]] = int((float(struct.unpack("<B", packet[2:3])[0]))/1)
		self.dict[self.items[3]] = int((float(struct.unpack("<B", packet[3:4])[0]))/1)
		self.dict[self.items[4]] = int((float(struct.unpack("<B", packet[4:5])[0]))/1)
		self.dict[self.items[5]] = int((float(struct.unpack("<B", packet[5:6])[0]))/1)
		self.dict[self.items[6]] = int((float(struct.unpack("<H", packet[6:8])[0]))/1)
		self.dict[self.items[7]] = int((float(struct.unpack("<I", packet[8:12])[0]))/1)
		self.dict[self.items[8]] = int((float(struct.unpack("<B", packet[12:13])[0]))/1)
		self.dict[self.items[9]] = float((float(struct.unpack("<h", packet[13:15])[0]))/100)
		self.dict[self.items[10]] = float((float(struct.unpack("<h", packet[15:17])[0]))/100)
		self.dict[self.items[11]] = int((float(struct.unpack("<I", packet[17:21])[0]))/1)
		self.dict[self.items[12]] = float((float(struct.unpack("<h", packet[21:23])[0]))/100)
		self.dict[self.items[13]] = float((float(struct.unpack("<h", packet[23:25])[0]))/100)
		self.dict[self.items[14]] = float((float(struct.unpack("<B", packet[25:26])[0]))/100)
		self.dict[self.items[15]] = float((float(struct.unpack("<B", packet[26:27])[0]))/100)
		self.dict[self.items[16]] = int((float(struct.unpack("<I", packet[27:31])[0]))/1)
		self.dict[self.items[17]] = float((float(struct.unpack("<i", packet[31:35])[0]))/10)
		self.dict[self.items[18]] = float((float(struct.unpack("<i", packet[35:39])[0]))/10)
		self.dict[self.items[19]] = float((float(struct.unpack("<i", packet[39:43])[0]))/10)
		self.dict[self.items[20]] = float((float(struct.unpack("<i", packet[43:47])[0]))/10)
		self.dict[self.items[21]] = float((float(struct.unpack("<i", packet[47:51])[0]))/10)
		self.dict[self.items[22]] = float((float(struct.unpack("<i", packet[51:55])[0]))/10)
		self.dict[self.items[23]] = float((float(struct.unpack("<i", packet[55:59])[0]))/10)
		self.dict[self.items[24]] = float((float(struct.unpack("<i", packet[59:63])[0]))/10)
		self.dict[self.items[25]] = float((float(struct.unpack("<i", packet[63:67])[0]))/10)
		self.dict[self.items[26]] = float((float(struct.unpack("<i", packet[67:71])[0]))/10)
		self.dict[self.items[27]] = float((float(struct.unpack("<i", packet[71:75])[0]))/10)
		self.dict[self.items[28]] = float((float(struct.unpack("<i", packet[75:79])[0]))/10)
		self.dict[self.items[29]] = float((float(struct.unpack("<i", packet[79:83])[0]))/10)
		self.dict[self.items[30]] = float((float(struct.unpack("<i", packet[83:87])[0]))/10)
		self.dict[self.items[31]] = float((float(struct.unpack("<i", packet[87:91])[0]))/10)
		self.dict[self.items[32]] = float((float(struct.unpack("<i", packet[91:95])[0]))/10)
		self.dict[self.items[33]] = float((float(struct.unpack("<i", packet[95:99])[0]))/10)
		self.dict[self.items[34]] = float((float(struct.unpack("<i", packet[99:103])[0]))/10)
		self.dict[self.items[35]] = float((float(struct.unpack("<i", packet[103:107])[0]))/10)
		self.dict[self.items[36]] = float((float(struct.unpack("<i", packet[107:111])[0]))/10)
		self.dict[self.items[37]] = float((float(struct.unpack("<B", packet[111:112])[0]))/10)
		self.dict[self.items[38]] = float((float(struct.unpack("<B", packet[112:113])[0]))/10)
		self.dict[self.items[39]] = float((float(struct.unpack("<B", packet[113:114])[0]))/10)
		self.dict[self.items[40]] = float((float(struct.unpack("<B", packet[114:115])[0]))/10)
		self.dict[self.items[41]] = float((float(struct.unpack("<B", packet[115:116])[0]))/10)
		self.dict[self.items[42]] = float((float(struct.unpack("<B", packet[116:117])[0]))/10)
		self.dict[self.items[43]] = float((float(struct.unpack("<B", packet[117:118])[0]))/10)
		self.dict[self.items[44]] = float((float(struct.unpack("<B", packet[118:119])[0]))/10)
		self.dict[self.items[45]] = float((float(struct.unpack("<B", packet[119:120])[0]))/10)
		self.dict[self.items[46]] = float((float(struct.unpack("<B", packet[120:121])[0]))/10)
		self.dict[self.items[47]] = float((float(struct.unpack("<B", packet[121:122])[0]))/10)
		self.dict[self.items[48]] = float((float(struct.unpack("<B", packet[122:123])[0]))/10)
		self.dict[self.items[49]] = float((float(struct.unpack("<B", packet[123:124])[0]))/10)
		self.dict[self.items[50]] = float((float(struct.unpack("<B", packet[124:125])[0]))/10)
		self.dict[self.items[51]] = float((float(struct.unpack("<H", packet[125:127])[0]))/100)
		self.dict[self.items[52]] = float((float(struct.unpack("<H", packet[127:129])[0]))/100)
		self.dict[self.items[53]] = float((float(struct.unpack("<H", packet[129:131])[0]))/100)
		self.dict[self.items[54]] = float((float(struct.unpack("<H", packet[131:133])[0]))/100)
		self.dict[self.items[55]] = float((float(struct.unpack("<H", packet[133:135])[0]))/100)
		self.dict[self.items[56]] = float((float(struct.unpack("<H", packet[135:137])[0]))/100)
		self.dict[self.items[57]] = float((float(struct.unpack("<H", packet[137:139])[0]))/100)
		self.dict[self.items[58]] = float((float(struct.unpack("<H", packet[139:141])[0]))/100)
		self.dict[self.items[59]] = float((float(struct.unpack("<H", packet[141:143])[0]))/100)
		self.dict[self.items[60]] = float((float(struct.unpack("<H", packet[143:145])[0]))/100)
		self.dict[self.items[61]] = float((float(struct.unpack("<H", packet[145:147])[0]))/100)
		self.dict[self.items[62]] = float((float(struct.unpack("<H", packet[147:149])[0]))/100)
		self.dict[self.items[63]] = float((float(struct.unpack("<H", packet[149:151])[0]))/100)
		self.dict[self.items[64]] = float((float(struct.unpack("<h", packet[151:153])[0]))/10)
		self.dict[self.items[65]] = float((float(struct.unpack("<h", packet[153:155])[0]))/10)
		self.dict[self.items[66]] = int((float(struct.unpack("<h", packet[155:157])[0]))/1)
		self.dict[self.items[67]] = int((float(struct.unpack("<h", packet[157:159])[0]))/1)
		self.dict[self.items[68]] = float((float(struct.unpack("<h", packet[159:161])[0]))/10)
		self.dict[self.items[69]] = float((float(struct.unpack("<h", packet[161:163])[0]))/10)
		self.dict[self.items[70]] = float((float(struct.unpack("<H", packet[163:165])[0]))/100)
		self.dict[self.items[71]] = float((float(struct.unpack("<H", packet[165:167])[0]))/100)
		self.dict[self.items[72]] = float((float(struct.unpack("<H", packet[167:169])[0]))/100)
		self.dict[self.items[73]] = float((float(struct.unpack("<H", packet[169:171])[0]))/100)
		self.dict[self.items[74]] = float((float(struct.unpack("<H", packet[171:173])[0]))/100)
		self.dict[self.items[75]] = float((float(struct.unpack("<H", packet[173:175])[0]))/100)
		self.dict[self.items[76]] = float((float(struct.unpack("<h", packet[175:177])[0]))/10)
		self.dict[self.items[77]] = float((float(struct.unpack("<h", packet[177:179])[0]))/10)
		self.dict[self.items[78]] = float((float(struct.unpack("<h", packet[179:181])[0]))/10)
		self.dict[self.items[79]] = float((float(struct.unpack("<h", packet[181:183])[0]))/10)
		self.dict[self.items[80]] = float((float(struct.unpack("<h", packet[183:185])[0]))/10)
		self.dict[self.items[81]] = float((float(struct.unpack("<h", packet[185:187])[0]))/10)
		self.dict[self.items[82]] = float((float(struct.unpack("<i", packet[187:191])[0]))/100)
		self.dict[self.items[83]] = float((float(struct.unpack("<i", packet[191:195])[0]))/100)
		self.dict[self.items[84]] = float((float(struct.unpack("<h", packet[195:197])[0]))/10)
		self.dict[self.items[85]] = float((float(struct.unpack("<h", packet[197:199])[0]))/10)
		self.dict[self.items[86]] = float((float(struct.unpack("<h", packet[199:201])[0]))/10)
		self.dict[self.items[87]] = float((float(struct.unpack("<h", packet[201:203])[0]))/10)
		self.dict[self.items[88]] = float((float(struct.unpack("<i", packet[203:207])[0]))/10)
		self.dict[self.items[89]] = float((float(struct.unpack("<i", packet[207:211])[0]))/10)
		self.dict[self.items[90]] = float((float(struct.unpack("<i", packet[211:215])[0]))/10)
		self.dict[self.items[91]] = float((float(struct.unpack("<i", packet[215:219])[0]))/10)
		self.dict[self.items[92]] = float((float(struct.unpack("<i", packet[219:223])[0]))/10)
		self.dict[self.items[93]] = int((float(struct.unpack("<B", packet[223:224])[0]))/1)
		self.dict[self.items[94]] = int((float(struct.unpack("<B", packet[224:225])[0]))/1)
		self.dict[self.items[95]] = int((float(struct.unpack("<I", packet[225:229])[0]))/1)
		self.dict[self.items[96]] = int((float(struct.unpack("<H", packet[229:231])[0]))/1)
		self.dict[self.items[97]] = int((float(struct.unpack("<H", packet[231:233])[0]))/1)
		self.dict[self.items[98]] = int((float(struct.unpack("<B", packet[233:234])[0]))/1)
		self.dict[self.items[99]] = int((float(struct.unpack("<H", packet[234:236])[0]))/1)
		self.dict[self.items[100]] = int((float(struct.unpack("<H", packet[236:238])[0]))/1)
		self.dict[self.items[101]] = float((float(struct.unpack("<i", packet[238:242])[0]))/10000)
		self.dict[self.items[102]] = int((float(struct.unpack("<i", packet[242:246])[0]))/1)
		self.dict[self.items[103]] = int((float(struct.unpack("<B", packet[246:247])[0]))/1)
		self.dict[self.items[104]] = int((float(struct.unpack("<B", packet[247:248])[0]))/1)
		self.dict[self.items[105]] = int((float(struct.unpack("<I", packet[248:252])[0]))/1)
		self.dict[self.items[106]] = int((float(struct.unpack("<B", packet[252:253])[0]))/1)
