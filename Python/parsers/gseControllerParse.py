### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### telemParse.py
### Autogenerated by firmware-libraries/SerialComms/python/telem_file_generator.py on Thu Apr  8 19:14:01 2021

import time
import struct

class GSEController:

	def __init__(self):
		self.packet_byte_size = 236
		self.num_items = 145
		
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
		self.items[15] = 'pressure[6]' 
		self.items[16] = 'pressure[7]' 
		self.items[17] = 'pressure[8]' 
		self.items[18] = 'pressure[9]' 
		self.items[19] = 'pressure[10]' 
		self.items[20] = 'pressure[11]' 
		self.items[21] = 'pressure[12]' 
		self.items[22] = 'pressure[13]' 
		self.items[23] = 'pressure[14]' 
		self.items[24] = 'pressure[15]' 
		self.items[25] = 'pressure[16]' 
		self.items[26] = 'pressure[17]' 
		self.items[27] = 'pressure[18]' 
		self.items[28] = 'pressure[19]' 
		self.items[29] = 'pressure[20]' 
		self.items[30] = 'pressure[21]' 
		self.items[31] = 'e_batt' 
		self.items[32] = 'ibus' 
		self.items[33] = 'STATE' 
		self.items[34] = 'load[0]' 
		self.items[35] = 'load[1]' 
		self.items[36] = 'load[2]' 
		self.items[37] = 'load[3]' 
		self.items[38] = 'load[4]' 
		self.items[39] = 'vlv0.i' 
		self.items[40] = 'vlv1.i' 
		self.items[41] = 'vlv2.i' 
		self.items[42] = 'vlv3.i' 
		self.items[43] = 'vlv4.i' 
		self.items[44] = 'vlv5.i' 
		self.items[45] = 'vlv6.i' 
		self.items[46] = 'vlv7.i' 
		self.items[47] = 'vlv8.i' 
		self.items[48] = 'ivlv[9]' 
		self.items[49] = 'ivlv[10]' 
		self.items[50] = 'ivlv[11]' 
		self.items[51] = 'ivlv[12]' 
		self.items[52] = 'ivlv[13]' 
		self.items[53] = 'ivlv[14]' 
		self.items[54] = 'ivlv[15]' 
		self.items[55] = 'ivlv[16]' 
		self.items[56] = 'ivlv[17]' 
		self.items[57] = 'ivlv[18]' 
		self.items[58] = 'ivlv[19]' 
		self.items[59] = 'ivlv[20]' 
		self.items[60] = 'ivlv[21]' 
		self.items[61] = 'ivlv[22]' 
		self.items[62] = 'ivlv[23]' 
		self.items[63] = 'ivlv[24]' 
		self.items[64] = 'ivlv[25]' 
		self.items[65] = 'ivlv[26]' 
		self.items[66] = 'ivlv[27]' 
		self.items[67] = 'ivlv[28]' 
		self.items[68] = 'ivlv[29]' 
		self.items[69] = 'ivlv[30]' 
		self.items[70] = 'ivlv[31]' 
		self.items[71] = 'vlv0.e' 
		self.items[72] = 'vlv1.e' 
		self.items[73] = 'vlv2.e' 
		self.items[74] = 'vlv3.e' 
		self.items[75] = 'vlv4.e' 
		self.items[76] = 'vlv5.e' 
		self.items[77] = 'vlv6.e' 
		self.items[78] = 'vlv7.e' 
		self.items[79] = 'vlv8.e' 
		self.items[80] = 'evlv[9]' 
		self.items[81] = 'evlv[10]' 
		self.items[82] = 'evlv[11]' 
		self.items[83] = 'evlv[12]' 
		self.items[84] = 'evlv[13]' 
		self.items[85] = 'evlv[14]' 
		self.items[86] = 'evlv[15]' 
		self.items[87] = 'evlv[16]' 
		self.items[88] = 'evlv[17]' 
		self.items[89] = 'evlv[18]' 
		self.items[90] = 'evlv[19]' 
		self.items[91] = 'evlv[20]' 
		self.items[92] = 'evlv[21]' 
		self.items[93] = 'evlv[22]' 
		self.items[94] = 'evlv[23]' 
		self.items[95] = 'evlv[24]' 
		self.items[96] = 'evlv[25]' 
		self.items[97] = 'evlv[26]' 
		self.items[98] = 'evlv[27]' 
		self.items[99] = 'evlv[28]' 
		self.items[100] = 'evlv[29]' 
		self.items[101] = 'evlv[30]' 
		self.items[102] = 'evlv[31]' 
		self.items[103] = 'e3v' 
		self.items[104] = 'e5v' 
		self.items[105] = 'e28v' 
		self.items[106] = 'i5v' 
		self.items[107] = 'i3v' 
		self.items[108] = 'last_command_id' 
		self.items[109] = 'tc[0]' 
		self.items[110] = 'tc[1]' 
		self.items[111] = 'tc[2]' 
		self.items[112] = 'tc[3]' 
		self.items[113] = 'tc[4]' 
		self.items[114] = 'tc[5]' 
		self.items[115] = 'tc[6]' 
		self.items[116] = 'tc[7]' 
		self.items[117] = 'tc[8]' 
		self.items[118] = 'tc[9]' 
		self.items[119] = 'tc[10]' 
		self.items[120] = 'tc[11]' 
		self.items[121] = 'tc[12]' 
		self.items[122] = 'tc[13]' 
		self.items[123] = 'tc[14]' 
		self.items[124] = 'tc[15]' 
		self.items[125] = 'rtd[0]' 
		self.items[126] = 'rtd[1]' 
		self.items[127] = 'rtd[2]' 
		self.items[128] = 'rtd[3]' 
		self.items[129] = 'rtd[4]' 
		self.items[130] = 'rtd[5]' 
		self.items[131] = 'rtd[6]' 
		self.items[132] = 'rtd[7]' 
		self.items[133] = 'elapsed_test_duration' 
		self.items[134] = 'micros' 
		self.items[135] = 'telem_rate' 
		self.items[136] = 'adc_rate' 
		self.items[137] = 'flash_mem' 
		self.items[138] = 'own_board_addr' 
		self.items[139] = 'last_packet_number' 
		self.items[140] = 'tbrd' 
		self.items[141] = 'tvlv' 
		self.items[142] = 'tmtr' 
		self.items[143] = 'LOGGING_ACTIVE' 
		self.items[144] = 'TELEM_ACTIVE' 

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
		self.units[self.items[15]] = "psi"
		self.units[self.items[16]] = "psi"
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
		self.units[self.items[31]] = "Volts"
		self.units[self.items[32]] = "Amps"
		self.units[self.items[33]] = "ul"
		self.units[self.items[34]] = "kg"
		self.units[self.items[35]] = "kg"
		self.units[self.items[36]] = "kg"
		self.units[self.items[37]] = "kg"
		self.units[self.items[38]] = "kg"
		self.units[self.items[39]] = "Amps"
		self.units[self.items[40]] = "Amps"
		self.units[self.items[41]] = "Amps"
		self.units[self.items[42]] = "Amps"
		self.units[self.items[43]] = "Amps"
		self.units[self.items[44]] = "Amps"
		self.units[self.items[45]] = "Amps"
		self.units[self.items[46]] = "Amps"
		self.units[self.items[47]] = "Amps"
		self.units[self.items[48]] = "Amps"
		self.units[self.items[49]] = "Amps"
		self.units[self.items[50]] = "Amps"
		self.units[self.items[51]] = "Amps"
		self.units[self.items[52]] = "Amps"
		self.units[self.items[53]] = "Amps"
		self.units[self.items[54]] = "Amps"
		self.units[self.items[55]] = "Amps"
		self.units[self.items[56]] = "Amps"
		self.units[self.items[57]] = "Amps"
		self.units[self.items[58]] = "Amps"
		self.units[self.items[59]] = "Amps"
		self.units[self.items[60]] = "Amps"
		self.units[self.items[61]] = "Amps"
		self.units[self.items[62]] = "Amps"
		self.units[self.items[63]] = "Amps"
		self.units[self.items[64]] = "Amps"
		self.units[self.items[65]] = "Amps"
		self.units[self.items[66]] = "Amps"
		self.units[self.items[67]] = "Amps"
		self.units[self.items[68]] = "Amps"
		self.units[self.items[69]] = "Amps"
		self.units[self.items[70]] = "Amps"
		self.units[self.items[71]] = "Volts"
		self.units[self.items[72]] = "Volts"
		self.units[self.items[73]] = "Volts"
		self.units[self.items[74]] = "Volts"
		self.units[self.items[75]] = "Volts"
		self.units[self.items[76]] = "Volts"
		self.units[self.items[77]] = "Volts"
		self.units[self.items[78]] = "Volts"
		self.units[self.items[79]] = "Volts"
		self.units[self.items[80]] = "Volts"
		self.units[self.items[81]] = "Volts"
		self.units[self.items[82]] = "Volts"
		self.units[self.items[83]] = "Volts"
		self.units[self.items[84]] = "Volts"
		self.units[self.items[85]] = "Volts"
		self.units[self.items[86]] = "Volts"
		self.units[self.items[87]] = "Volts"
		self.units[self.items[88]] = "Volts"
		self.units[self.items[89]] = "Volts"
		self.units[self.items[90]] = "Volts"
		self.units[self.items[91]] = "Volts"
		self.units[self.items[92]] = "Volts"
		self.units[self.items[93]] = "Volts"
		self.units[self.items[94]] = "Volts"
		self.units[self.items[95]] = "Volts"
		self.units[self.items[96]] = "Volts"
		self.units[self.items[97]] = "Volts"
		self.units[self.items[98]] = "Volts"
		self.units[self.items[99]] = "Volts"
		self.units[self.items[100]] = "Volts"
		self.units[self.items[101]] = "Volts"
		self.units[self.items[102]] = "Volts"
		self.units[self.items[103]] = "Volts"
		self.units[self.items[104]] = "Volts"
		self.units[self.items[105]] = "Volts"
		self.units[self.items[106]] = "Amps"
		self.units[self.items[107]] = "Amps"
		self.units[self.items[108]] = "ul"
		self.units[self.items[109]] = "K"
		self.units[self.items[110]] = "K"
		self.units[self.items[111]] = "K"
		self.units[self.items[112]] = "K"
		self.units[self.items[113]] = "K"
		self.units[self.items[114]] = "K"
		self.units[self.items[115]] = "K"
		self.units[self.items[116]] = "K"
		self.units[self.items[117]] = "K"
		self.units[self.items[118]] = "K"
		self.units[self.items[119]] = "K"
		self.units[self.items[120]] = "K"
		self.units[self.items[121]] = "K"
		self.units[self.items[122]] = "K"
		self.units[self.items[123]] = "K"
		self.units[self.items[124]] = "K"
		self.units[self.items[125]] = "K"
		self.units[self.items[126]] = "K"
		self.units[self.items[127]] = "K"
		self.units[self.items[128]] = "K"
		self.units[self.items[129]] = "K"
		self.units[self.items[130]] = "K"
		self.units[self.items[131]] = "K"
		self.units[self.items[132]] = "K"
		self.units[self.items[133]] = "ms"
		self.units[self.items[134]] = "us"
		self.units[self.items[135]] = "Hz"
		self.units[self.items[136]] = "Hz"
		self.units[self.items[137]] = "bytes"
		self.units[self.items[138]] = "ul"
		self.units[self.items[139]] = "ul"
		self.units[self.items[140]] = "ul"
		self.units[self.items[141]] = "ul"
		self.units[self.items[142]] = "ul"
		self.units[self.items[143]] = "ul"
		self.units[self.items[144]] = "ul"

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
		self.dict[self.items[9]] = float((float(struct.unpack("<h", packet[16:18])[0]))/1)
		self.dict[self.items[10]] = float((float(struct.unpack("<h", packet[18:20])[0]))/1)
		self.dict[self.items[11]] = float((float(struct.unpack("<h", packet[20:22])[0]))/1)
		self.dict[self.items[12]] = float((float(struct.unpack("<h", packet[22:24])[0]))/1)
		self.dict[self.items[13]] = float((float(struct.unpack("<h", packet[24:26])[0]))/1)
		self.dict[self.items[14]] = float((float(struct.unpack("<h", packet[26:28])[0]))/1)
		self.dict[self.items[15]] = float((float(struct.unpack("<h", packet[28:30])[0]))/1)
		self.dict[self.items[16]] = float((float(struct.unpack("<h", packet[30:32])[0]))/1)
		self.dict[self.items[17]] = float((float(struct.unpack("<h", packet[32:34])[0]))/1)
		self.dict[self.items[18]] = float((float(struct.unpack("<h", packet[34:36])[0]))/1)
		self.dict[self.items[19]] = float((float(struct.unpack("<h", packet[36:38])[0]))/1)
		self.dict[self.items[20]] = float((float(struct.unpack("<h", packet[38:40])[0]))/1)
		self.dict[self.items[21]] = float((float(struct.unpack("<h", packet[40:42])[0]))/1)
		self.dict[self.items[22]] = float((float(struct.unpack("<h", packet[42:44])[0]))/1)
		self.dict[self.items[23]] = float((float(struct.unpack("<h", packet[44:46])[0]))/1)
		self.dict[self.items[24]] = float((float(struct.unpack("<h", packet[46:48])[0]))/1)
		self.dict[self.items[25]] = float((float(struct.unpack("<h", packet[48:50])[0]))/1)
		self.dict[self.items[26]] = float((float(struct.unpack("<h", packet[50:52])[0]))/1)
		self.dict[self.items[27]] = float((float(struct.unpack("<h", packet[52:54])[0]))/1)
		self.dict[self.items[28]] = float((float(struct.unpack("<h", packet[54:56])[0]))/1)
		self.dict[self.items[29]] = float((float(struct.unpack("<h", packet[56:58])[0]))/1)
		self.dict[self.items[30]] = float((float(struct.unpack("<h", packet[58:60])[0]))/1)
		self.dict[self.items[31]] = float((float(struct.unpack("<h", packet[60:62])[0]))/100)
		self.dict[self.items[32]] = float((float(struct.unpack("<h", packet[62:64])[0]))/100)
		self.dict[self.items[33]] = int((float(struct.unpack("<B", packet[64:65])[0]))/1)
		self.dict[self.items[34]] = int((float(struct.unpack("<H", packet[65:67])[0]))/1)
		self.dict[self.items[35]] = float((float(struct.unpack("<H", packet[67:69])[0]))/1)
		self.dict[self.items[36]] = float((float(struct.unpack("<H", packet[69:71])[0]))/1)
		self.dict[self.items[37]] = float((float(struct.unpack("<H", packet[71:73])[0]))/1)
		self.dict[self.items[38]] = float((float(struct.unpack("<H", packet[73:75])[0]))/1)
		self.dict[self.items[39]] = float((float(struct.unpack("<B", packet[75:76])[0]))/10)
		self.dict[self.items[40]] = float((float(struct.unpack("<B", packet[76:77])[0]))/10)
		self.dict[self.items[41]] = float((float(struct.unpack("<B", packet[77:78])[0]))/10)
		self.dict[self.items[42]] = float((float(struct.unpack("<B", packet[78:79])[0]))/10)
		self.dict[self.items[43]] = float((float(struct.unpack("<B", packet[79:80])[0]))/10)
		self.dict[self.items[44]] = float((float(struct.unpack("<B", packet[80:81])[0]))/10)
		self.dict[self.items[45]] = float((float(struct.unpack("<B", packet[81:82])[0]))/10)
		self.dict[self.items[46]] = float((float(struct.unpack("<B", packet[82:83])[0]))/10)
		self.dict[self.items[47]] = float((float(struct.unpack("<B", packet[83:84])[0]))/10)
		self.dict[self.items[48]] = float((float(struct.unpack("<B", packet[84:85])[0]))/10)
		self.dict[self.items[49]] = float((float(struct.unpack("<B", packet[85:86])[0]))/10)
		self.dict[self.items[50]] = float((float(struct.unpack("<B", packet[86:87])[0]))/10)
		self.dict[self.items[51]] = float((float(struct.unpack("<B", packet[87:88])[0]))/10)
		self.dict[self.items[52]] = float((float(struct.unpack("<B", packet[88:89])[0]))/10)
		self.dict[self.items[53]] = float((float(struct.unpack("<B", packet[89:90])[0]))/10)
		self.dict[self.items[54]] = float((float(struct.unpack("<B", packet[90:91])[0]))/10)
		self.dict[self.items[55]] = float((float(struct.unpack("<B", packet[91:92])[0]))/10)
		self.dict[self.items[56]] = float((float(struct.unpack("<B", packet[92:93])[0]))/10)
		self.dict[self.items[57]] = float((float(struct.unpack("<B", packet[93:94])[0]))/10)
		self.dict[self.items[58]] = float((float(struct.unpack("<B", packet[94:95])[0]))/10)
		self.dict[self.items[59]] = float((float(struct.unpack("<B", packet[95:96])[0]))/10)
		self.dict[self.items[60]] = float((float(struct.unpack("<B", packet[96:97])[0]))/10)
		self.dict[self.items[61]] = float((float(struct.unpack("<B", packet[97:98])[0]))/10)
		self.dict[self.items[62]] = float((float(struct.unpack("<B", packet[98:99])[0]))/10)
		self.dict[self.items[63]] = float((float(struct.unpack("<B", packet[99:100])[0]))/10)
		self.dict[self.items[64]] = float((float(struct.unpack("<B", packet[100:101])[0]))/10)
		self.dict[self.items[65]] = float((float(struct.unpack("<B", packet[101:102])[0]))/10)
		self.dict[self.items[66]] = float((float(struct.unpack("<B", packet[102:103])[0]))/10)
		self.dict[self.items[67]] = float((float(struct.unpack("<B", packet[103:104])[0]))/10)
		self.dict[self.items[68]] = float((float(struct.unpack("<B", packet[104:105])[0]))/10)
		self.dict[self.items[69]] = float((float(struct.unpack("<B", packet[105:106])[0]))/10)
		self.dict[self.items[70]] = float((float(struct.unpack("<B", packet[106:107])[0]))/10)
		self.dict[self.items[71]] = float((float(struct.unpack("<B", packet[107:108])[0]))/10)
		self.dict[self.items[72]] = float((float(struct.unpack("<B", packet[108:109])[0]))/10)
		self.dict[self.items[73]] = float((float(struct.unpack("<B", packet[109:110])[0]))/10)
		self.dict[self.items[74]] = float((float(struct.unpack("<B", packet[110:111])[0]))/10)
		self.dict[self.items[75]] = float((float(struct.unpack("<B", packet[111:112])[0]))/10)
		self.dict[self.items[76]] = float((float(struct.unpack("<B", packet[112:113])[0]))/10)
		self.dict[self.items[77]] = float((float(struct.unpack("<B", packet[113:114])[0]))/10)
		self.dict[self.items[78]] = float((float(struct.unpack("<B", packet[114:115])[0]))/10)
		self.dict[self.items[79]] = float((float(struct.unpack("<B", packet[115:116])[0]))/10)
		self.dict[self.items[80]] = float((float(struct.unpack("<B", packet[116:117])[0]))/10)
		self.dict[self.items[81]] = float((float(struct.unpack("<B", packet[117:118])[0]))/10)
		self.dict[self.items[82]] = float((float(struct.unpack("<B", packet[118:119])[0]))/10)
		self.dict[self.items[83]] = float((float(struct.unpack("<B", packet[119:120])[0]))/10)
		self.dict[self.items[84]] = float((float(struct.unpack("<B", packet[120:121])[0]))/10)
		self.dict[self.items[85]] = float((float(struct.unpack("<B", packet[121:122])[0]))/10)
		self.dict[self.items[86]] = float((float(struct.unpack("<B", packet[122:123])[0]))/10)
		self.dict[self.items[87]] = float((float(struct.unpack("<B", packet[123:124])[0]))/10)
		self.dict[self.items[88]] = float((float(struct.unpack("<B", packet[124:125])[0]))/10)
		self.dict[self.items[89]] = float((float(struct.unpack("<B", packet[125:126])[0]))/10)
		self.dict[self.items[90]] = float((float(struct.unpack("<B", packet[126:127])[0]))/10)
		self.dict[self.items[91]] = float((float(struct.unpack("<B", packet[127:128])[0]))/10)
		self.dict[self.items[92]] = float((float(struct.unpack("<B", packet[128:129])[0]))/10)
		self.dict[self.items[93]] = float((float(struct.unpack("<B", packet[129:130])[0]))/10)
		self.dict[self.items[94]] = float((float(struct.unpack("<B", packet[130:131])[0]))/10)
		self.dict[self.items[95]] = float((float(struct.unpack("<B", packet[131:132])[0]))/10)
		self.dict[self.items[96]] = float((float(struct.unpack("<B", packet[132:133])[0]))/10)
		self.dict[self.items[97]] = float((float(struct.unpack("<B", packet[133:134])[0]))/10)
		self.dict[self.items[98]] = float((float(struct.unpack("<B", packet[134:135])[0]))/10)
		self.dict[self.items[99]] = float((float(struct.unpack("<B", packet[135:136])[0]))/10)
		self.dict[self.items[100]] = float((float(struct.unpack("<B", packet[136:137])[0]))/10)
		self.dict[self.items[101]] = float((float(struct.unpack("<B", packet[137:138])[0]))/10)
		self.dict[self.items[102]] = float((float(struct.unpack("<B", packet[138:139])[0]))/10)
		self.dict[self.items[103]] = float((float(struct.unpack("<i", packet[139:143])[0]))/100)
		self.dict[self.items[104]] = float((float(struct.unpack("<i", packet[143:147])[0]))/100)
		self.dict[self.items[105]] = float((float(struct.unpack("<h", packet[147:149])[0]))/100)
		self.dict[self.items[106]] = float((float(struct.unpack("<B", packet[149:150])[0]))/100)
		self.dict[self.items[107]] = float((float(struct.unpack("<B", packet[150:151])[0]))/100)
		self.dict[self.items[108]] = float((float(struct.unpack("<H", packet[151:153])[0]))/1)
		self.dict[self.items[109]] = float((float(struct.unpack("<H", packet[153:155])[0]))/100)
		self.dict[self.items[110]] = float((float(struct.unpack("<H", packet[155:157])[0]))/100)
		self.dict[self.items[111]] = float((float(struct.unpack("<H", packet[157:159])[0]))/100)
		self.dict[self.items[112]] = float((float(struct.unpack("<H", packet[159:161])[0]))/100)
		self.dict[self.items[113]] = float((float(struct.unpack("<H", packet[161:163])[0]))/100)
		self.dict[self.items[114]] = float((float(struct.unpack("<H", packet[163:165])[0]))/100)
		self.dict[self.items[115]] = float((float(struct.unpack("<H", packet[165:167])[0]))/100)
		self.dict[self.items[116]] = float((float(struct.unpack("<H", packet[167:169])[0]))/100)
		self.dict[self.items[117]] = float((float(struct.unpack("<H", packet[169:171])[0]))/100)
		self.dict[self.items[118]] = float((float(struct.unpack("<H", packet[171:173])[0]))/100)
		self.dict[self.items[119]] = float((float(struct.unpack("<H", packet[173:175])[0]))/100)
		self.dict[self.items[120]] = float((float(struct.unpack("<H", packet[175:177])[0]))/100)
		self.dict[self.items[121]] = float((float(struct.unpack("<H", packet[177:179])[0]))/100)
		self.dict[self.items[122]] = float((float(struct.unpack("<H", packet[179:181])[0]))/100)
		self.dict[self.items[123]] = float((float(struct.unpack("<H", packet[181:183])[0]))/100)
		self.dict[self.items[124]] = float((float(struct.unpack("<H", packet[183:185])[0]))/100)
		self.dict[self.items[125]] = float((float(struct.unpack("<H", packet[185:187])[0]))/100)
		self.dict[self.items[126]] = float((float(struct.unpack("<H", packet[187:189])[0]))/100)
		self.dict[self.items[127]] = float((float(struct.unpack("<H", packet[189:191])[0]))/100)
		self.dict[self.items[128]] = float((float(struct.unpack("<H", packet[191:193])[0]))/100)
		self.dict[self.items[129]] = float((float(struct.unpack("<H", packet[193:195])[0]))/100)
		self.dict[self.items[130]] = float((float(struct.unpack("<H", packet[195:197])[0]))/100)
		self.dict[self.items[131]] = float((float(struct.unpack("<H", packet[197:199])[0]))/100)
		self.dict[self.items[132]] = float((float(struct.unpack("<H", packet[199:201])[0]))/100)
		self.dict[self.items[133]] = int((float(struct.unpack("<I", packet[201:205])[0]))/1)
		self.dict[self.items[134]] = int((float(struct.unpack("<Q", packet[205:213])[0]))/1)
		self.dict[self.items[135]] = int((float(struct.unpack("<I", packet[213:217])[0]))/1)
		self.dict[self.items[136]] = int((float(struct.unpack("<I", packet[217:221])[0]))/1)
		self.dict[self.items[137]] = int((float(struct.unpack("<I", packet[221:225])[0]))/1)
		self.dict[self.items[138]] = int((float(struct.unpack("<B", packet[225:226])[0]))/1)
		self.dict[self.items[139]] = float((float(struct.unpack("<H", packet[226:228])[0]))/1)
		self.dict[self.items[140]] = float((float(struct.unpack("<H", packet[228:230])[0]))/1)
		self.dict[self.items[141]] = float((float(struct.unpack("<H", packet[230:232])[0]))/1)
		self.dict[self.items[142]] = float((float(struct.unpack("<H", packet[232:234])[0]))/1)
		self.dict[self.items[143]] = int((float(struct.unpack("<B", packet[234:235])[0]))/1)
		self.dict[self.items[144]] = int((float(struct.unpack("<B", packet[235:236])[0]))/1)
