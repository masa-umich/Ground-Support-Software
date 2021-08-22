### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### telemParse.py
### Autogenerated by firmware-libraries/SerialComms/python/telem_file_generator.py on Sun Aug 22 15:40:40 2021

import time
import struct

class PressurizationController:

	def __init__(self):
		self.packet_byte_size = 213
		self.num_items = 104
		
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
		self.items[16] = 'last_command_id' 
		self.items[17] = 'status_flags' 
		self.items[18] = 'pressure[0]' 
		self.items[19] = 'pressure[1]' 
		self.items[20] = 'pressure[2]' 
		self.items[21] = 'pressure[3]' 
		self.items[22] = 'pressure[4]' 
		self.items[23] = 'pressure[5]' 
		self.items[24] = 'vlv0.i' 
		self.items[25] = 'vlv1.i' 
		self.items[26] = 'vlv2.i' 
		self.items[27] = 'vlv3.i' 
		self.items[28] = 'vlv4.i' 
		self.items[29] = 'vlv5.i' 
		self.items[30] = 'vlv6.i' 
		self.items[31] = 'vlv7.i' 
		self.items[32] = 'vlv8.i' 
		self.items[33] = 'vlv0.e' 
		self.items[34] = 'vlv1.e' 
		self.items[35] = 'vlv2.e' 
		self.items[36] = 'vlv3.e' 
		self.items[37] = 'vlv4.e' 
		self.items[38] = 'vlv5.e' 
		self.items[39] = 'vlv6.e' 
		self.items[40] = 'vlv7.e' 
		self.items[41] = 'vlv8.e' 
		self.items[42] = 'tc[0]' 
		self.items[43] = 'tc[1]' 
		self.items[44] = 'tc[2]' 
		self.items[45] = 'tc[3]' 
		self.items[46] = 'tc[4]' 
		self.items[47] = 'mtr0.pos' 
		self.items[48] = 'mtr1.pos' 
		self.items[49] = 'mtr0.vel' 
		self.items[50] = 'mtr1.vel' 
		self.items[51] = 'mtr0.ia' 
		self.items[52] = 'mtr0.ib' 
		self.items[53] = 'mtr1.ia' 
		self.items[54] = 'mtr1.ib' 
		self.items[55] = 'i_mtr[0]' 
		self.items[56] = 'i_mtr[1]' 
		self.items[57] = 'mtr0.set' 
		self.items[58] = 'mtr1.set' 
		self.items[59] = 'mtr0.p' 
		self.items[60] = 'mtr1.p' 
		self.items[61] = 'mtr0.i' 
		self.items[62] = 'mtr1.i' 
		self.items[63] = 'mtr0.d' 
		self.items[64] = 'mtr1.d' 
		self.items[65] = 'mtr0.kp_err' 
		self.items[66] = 'mtr1.kp_err' 
		self.items[67] = 'mtr0.ki_err' 
		self.items[68] = 'mtr1.ki_err' 
		self.items[69] = 'mtr0.kd_err' 
		self.items[70] = 'mtr1.kd_err' 
		self.items[71] = 'tnk0.tp' 
		self.items[72] = 'tnk1.tp' 
		self.items[73] = 'tnk0.hp' 
		self.items[74] = 'tnk1.hp' 
		self.items[75] = 'tnk0.lp' 
		self.items[76] = 'tnk1.lp' 
		self.items[77] = 'mtr0.pot' 
		self.items[78] = 'mtr1.pot' 
		self.items[79] = 'lox_ctrl_pres' 
		self.items[80] = 'fuel_ctrl_pres' 
		self.items[81] = 'copv_ctrl_pres' 
		self.items[82] = 'tnk0.en' 
		self.items[83] = 'tnk1.en' 
		self.items[84] = 'test_duration' 
		self.items[85] = 'ignitor_on_delay' 
		self.items[86] = 'ignitor_high_duration' 
		self.items[87] = 'fuel_mpv_delay' 
		self.items[88] = 'nozzle_film_cooling_delay' 
		self.items[89] = 'pid_delay' 
		self.items[90] = 'deg_corr_factor' 
		self.items[91] = 'state_rem_duration' 
		self.items[92] = 'telem_rate' 
		self.items[93] = 'adc_rate' 
		self.items[94] = 'flash_mem' 
		self.items[95] = 'LOGGING_ACTIVE' 
		self.items[96] = 'enable_auto_aborts' 
		self.items[97] = 'ignitor_break_count' 
		self.items[98] = 'chamber_pres_low_count' 
		self.items[99] = 'chamber_pres_high_count' 
		self.items[100] = 'tnk0.tpc.active' 
		self.items[101] = 'tnk1.tpc.active' 
		self.items[102] = 'fuel_vent_signal' 
		self.items[103] = 'fuel_vent_enable' 

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
		self.units[self.items[17]] = "ul"
		self.units[self.items[18]] = "psi"
		self.units[self.items[19]] = "psi"
		self.units[self.items[20]] = "psi"
		self.units[self.items[21]] = "psi"
		self.units[self.items[22]] = "psi"
		self.units[self.items[23]] = "psi"
		self.units[self.items[24]] = "Amps"
		self.units[self.items[25]] = "Amps"
		self.units[self.items[26]] = "Amps"
		self.units[self.items[27]] = "Amps"
		self.units[self.items[28]] = "Amps"
		self.units[self.items[29]] = "Amps"
		self.units[self.items[30]] = "Amps"
		self.units[self.items[31]] = "Amps"
		self.units[self.items[32]] = "Amps"
		self.units[self.items[33]] = "Volts"
		self.units[self.items[34]] = "Volts"
		self.units[self.items[35]] = "Volts"
		self.units[self.items[36]] = "Volts"
		self.units[self.items[37]] = "Volts"
		self.units[self.items[38]] = "Volts"
		self.units[self.items[39]] = "Volts"
		self.units[self.items[40]] = "Volts"
		self.units[self.items[41]] = "Volts"
		self.units[self.items[42]] = "K"
		self.units[self.items[43]] = "K"
		self.units[self.items[44]] = "K"
		self.units[self.items[45]] = "K"
		self.units[self.items[46]] = "K"
		self.units[self.items[47]] = "deg"
		self.units[self.items[48]] = "deg"
		self.units[self.items[49]] = "step/s"
		self.units[self.items[50]] = "step/s"
		self.units[self.items[51]] = "Amps"
		self.units[self.items[52]] = "Amps"
		self.units[self.items[53]] = "Amps"
		self.units[self.items[54]] = "Amps"
		self.units[self.items[55]] = "Amps"
		self.units[self.items[56]] = "Amps"
		self.units[self.items[57]] = "deg"
		self.units[self.items[58]] = "deg"
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
		self.units[self.items[70]] = "ul"
		self.units[self.items[71]] = "psi"
		self.units[self.items[72]] = "psi"
		self.units[self.items[73]] = "psi"
		self.units[self.items[74]] = "psi"
		self.units[self.items[75]] = "psi"
		self.units[self.items[76]] = "psi"
		self.units[self.items[77]] = "deg"
		self.units[self.items[78]] = "deg"
		self.units[self.items[79]] = "psi"
		self.units[self.items[80]] = "psi"
		self.units[self.items[81]] = "psi"
		self.units[self.items[82]] = "ul"
		self.units[self.items[83]] = "ul"
		self.units[self.items[84]] = "ms"
		self.units[self.items[85]] = "ms"
		self.units[self.items[86]] = "ms"
		self.units[self.items[87]] = "ms"
		self.units[self.items[88]] = "ms"
		self.units[self.items[89]] = "ms"
		self.units[self.items[90]] = "ul"
		self.units[self.items[91]] = "ms"
		self.units[self.items[92]] = "Hz"
		self.units[self.items[93]] = "Hz"
		self.units[self.items[94]] = "bytes"
		self.units[self.items[95]] = "ul"
		self.units[self.items[96]] = "ul"
		self.units[self.items[97]] = "counts"
		self.units[self.items[98]] = "counts"
		self.units[self.items[99]] = "counts"
		self.units[self.items[100]] = "ul"
		self.units[self.items[101]] = "ul"
		self.units[self.items[102]] = "ul"
		self.units[self.items[103]] = "ul"

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
		self.dict[self.items[16]] = float((float(struct.unpack("<B", packet[27:28])[0]))/1)
		self.dict[self.items[17]] = int((float(struct.unpack("<I", packet[28:32])[0]))/1)
		self.dict[self.items[18]] = float((float(struct.unpack("<i", packet[32:36])[0]))/10)
		self.dict[self.items[19]] = float((float(struct.unpack("<i", packet[36:40])[0]))/10)
		self.dict[self.items[20]] = float((float(struct.unpack("<i", packet[40:44])[0]))/10)
		self.dict[self.items[21]] = float((float(struct.unpack("<i", packet[44:48])[0]))/10)
		self.dict[self.items[22]] = float((float(struct.unpack("<i", packet[48:52])[0]))/10)
		self.dict[self.items[23]] = float((float(struct.unpack("<i", packet[52:56])[0]))/10)
		self.dict[self.items[24]] = float((float(struct.unpack("<B", packet[56:57])[0]))/10)
		self.dict[self.items[25]] = float((float(struct.unpack("<B", packet[57:58])[0]))/10)
		self.dict[self.items[26]] = float((float(struct.unpack("<B", packet[58:59])[0]))/10)
		self.dict[self.items[27]] = float((float(struct.unpack("<B", packet[59:60])[0]))/10)
		self.dict[self.items[28]] = float((float(struct.unpack("<B", packet[60:61])[0]))/10)
		self.dict[self.items[29]] = float((float(struct.unpack("<B", packet[61:62])[0]))/10)
		self.dict[self.items[30]] = float((float(struct.unpack("<B", packet[62:63])[0]))/10)
		self.dict[self.items[31]] = float((float(struct.unpack("<B", packet[63:64])[0]))/10)
		self.dict[self.items[32]] = float((float(struct.unpack("<B", packet[64:65])[0]))/10)
		self.dict[self.items[33]] = float((float(struct.unpack("<B", packet[65:66])[0]))/10)
		self.dict[self.items[34]] = float((float(struct.unpack("<B", packet[66:67])[0]))/10)
		self.dict[self.items[35]] = float((float(struct.unpack("<B", packet[67:68])[0]))/10)
		self.dict[self.items[36]] = float((float(struct.unpack("<B", packet[68:69])[0]))/10)
		self.dict[self.items[37]] = float((float(struct.unpack("<B", packet[69:70])[0]))/10)
		self.dict[self.items[38]] = float((float(struct.unpack("<B", packet[70:71])[0]))/10)
		self.dict[self.items[39]] = float((float(struct.unpack("<B", packet[71:72])[0]))/10)
		self.dict[self.items[40]] = float((float(struct.unpack("<B", packet[72:73])[0]))/10)
		self.dict[self.items[41]] = float((float(struct.unpack("<B", packet[73:74])[0]))/10)
		self.dict[self.items[42]] = float((float(struct.unpack("<H", packet[74:76])[0]))/100)
		self.dict[self.items[43]] = float((float(struct.unpack("<H", packet[76:78])[0]))/100)
		self.dict[self.items[44]] = float((float(struct.unpack("<H", packet[78:80])[0]))/100)
		self.dict[self.items[45]] = float((float(struct.unpack("<H", packet[80:82])[0]))/100)
		self.dict[self.items[46]] = float((float(struct.unpack("<H", packet[82:84])[0]))/100)
		self.dict[self.items[47]] = float((float(struct.unpack("<h", packet[84:86])[0]))/10)
		self.dict[self.items[48]] = float((float(struct.unpack("<h", packet[86:88])[0]))/10)
		self.dict[self.items[49]] = int((float(struct.unpack("<h", packet[88:90])[0]))/1)
		self.dict[self.items[50]] = int((float(struct.unpack("<h", packet[90:92])[0]))/1)
		self.dict[self.items[51]] = float((float(struct.unpack("<H", packet[92:94])[0]))/100)
		self.dict[self.items[52]] = float((float(struct.unpack("<H", packet[94:96])[0]))/100)
		self.dict[self.items[53]] = float((float(struct.unpack("<H", packet[96:98])[0]))/100)
		self.dict[self.items[54]] = float((float(struct.unpack("<H", packet[98:100])[0]))/100)
		self.dict[self.items[55]] = float((float(struct.unpack("<H", packet[100:102])[0]))/100)
		self.dict[self.items[56]] = float((float(struct.unpack("<H", packet[102:104])[0]))/100)
		self.dict[self.items[57]] = float((float(struct.unpack("<i", packet[104:108])[0]))/100)
		self.dict[self.items[58]] = float((float(struct.unpack("<i", packet[108:112])[0]))/100)
		self.dict[self.items[59]] = float((float(struct.unpack("<H", packet[112:114])[0]))/100)
		self.dict[self.items[60]] = float((float(struct.unpack("<H", packet[114:116])[0]))/100)
		self.dict[self.items[61]] = float((float(struct.unpack("<H", packet[116:118])[0]))/100)
		self.dict[self.items[62]] = float((float(struct.unpack("<H", packet[118:120])[0]))/100)
		self.dict[self.items[63]] = float((float(struct.unpack("<H", packet[120:122])[0]))/100)
		self.dict[self.items[64]] = float((float(struct.unpack("<H", packet[122:124])[0]))/100)
		self.dict[self.items[65]] = float((float(struct.unpack("<h", packet[124:126])[0]))/10)
		self.dict[self.items[66]] = float((float(struct.unpack("<h", packet[126:128])[0]))/10)
		self.dict[self.items[67]] = float((float(struct.unpack("<h", packet[128:130])[0]))/10)
		self.dict[self.items[68]] = float((float(struct.unpack("<h", packet[130:132])[0]))/10)
		self.dict[self.items[69]] = float((float(struct.unpack("<h", packet[132:134])[0]))/10)
		self.dict[self.items[70]] = float((float(struct.unpack("<h", packet[134:136])[0]))/10)
		self.dict[self.items[71]] = float((float(struct.unpack("<i", packet[136:140])[0]))/100)
		self.dict[self.items[72]] = float((float(struct.unpack("<i", packet[140:144])[0]))/100)
		self.dict[self.items[73]] = float((float(struct.unpack("<h", packet[144:146])[0]))/10)
		self.dict[self.items[74]] = float((float(struct.unpack("<h", packet[146:148])[0]))/10)
		self.dict[self.items[75]] = float((float(struct.unpack("<h", packet[148:150])[0]))/10)
		self.dict[self.items[76]] = float((float(struct.unpack("<h", packet[150:152])[0]))/10)
		self.dict[self.items[77]] = float((float(struct.unpack("<i", packet[152:156])[0]))/10)
		self.dict[self.items[78]] = float((float(struct.unpack("<i", packet[156:160])[0]))/10)
		self.dict[self.items[79]] = float((float(struct.unpack("<i", packet[160:164])[0]))/10)
		self.dict[self.items[80]] = float((float(struct.unpack("<i", packet[164:168])[0]))/10)
		self.dict[self.items[81]] = float((float(struct.unpack("<i", packet[168:172])[0]))/10)
		self.dict[self.items[82]] = int((float(struct.unpack("<B", packet[172:173])[0]))/1)
		self.dict[self.items[83]] = int((float(struct.unpack("<B", packet[173:174])[0]))/1)
		self.dict[self.items[84]] = int((float(struct.unpack("<I", packet[174:178])[0]))/1)
		self.dict[self.items[85]] = int((float(struct.unpack("<H", packet[178:180])[0]))/1)
		self.dict[self.items[86]] = int((float(struct.unpack("<H", packet[180:182])[0]))/1)
		self.dict[self.items[87]] = int((float(struct.unpack("<B", packet[182:183])[0]))/1)
		self.dict[self.items[88]] = int((float(struct.unpack("<H", packet[183:185])[0]))/1)
		self.dict[self.items[89]] = int((float(struct.unpack("<H", packet[185:187])[0]))/1)
		self.dict[self.items[90]] = float((float(struct.unpack("<i", packet[187:191])[0]))/10000)
		self.dict[self.items[91]] = int((float(struct.unpack("<i", packet[191:195])[0]))/1)
		self.dict[self.items[92]] = int((float(struct.unpack("<B", packet[195:196])[0]))/1)
		self.dict[self.items[93]] = int((float(struct.unpack("<B", packet[196:197])[0]))/1)
		self.dict[self.items[94]] = int((float(struct.unpack("<I", packet[197:201])[0]))/1)
		self.dict[self.items[95]] = int((float(struct.unpack("<B", packet[201:202])[0]))/1)
		self.dict[self.items[96]] = int((float(struct.unpack("<B", packet[202:203])[0]))/1)
		self.dict[self.items[97]] = int((float(struct.unpack("<H", packet[203:205])[0]))/1)
		self.dict[self.items[98]] = int((float(struct.unpack("<H", packet[205:207])[0]))/1)
		self.dict[self.items[99]] = int((float(struct.unpack("<H", packet[207:209])[0]))/1)
		self.dict[self.items[100]] = int((float(struct.unpack("<B", packet[209:210])[0]))/1)
		self.dict[self.items[101]] = int((float(struct.unpack("<B", packet[210:211])[0]))/1)
		self.dict[self.items[102]] = int((float(struct.unpack("<B", packet[211:212])[0]))/1)
		self.dict[self.items[103]] = int((float(struct.unpack("<B", packet[212:213])[0]))/1)
