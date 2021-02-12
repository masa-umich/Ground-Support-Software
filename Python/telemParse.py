### BEGIN AUTOGENERATED SECTION - MODIFICATIONS TO THIS CODE WILL BE OVERWRITTEN

### telemParse.py
### Autogenerated by firmware-libraries/SerialComms/python/telem_file_generator.py on Thu Feb 11 18:33:29 2021

import time
import struct

class TelemParse:

	def __init__(self):
		self.csv_header = "Time (s),valve_states (ul),pressure[0] (psi),pressure[1] (psi),pressure[2] (psi),pressure[3] (psi),pressure[4] (psi),pressure[5] (psi),e_batt (Volts),i_batt (Amps),STATE (ul),vlv0.i (Amps),vlv1.i (Amps),vlv2.i (Amps),vlv3.i (Amps),vlv4.i (Amps),vlv5.i (Amps),vlv6.i (Amps),vlv7.i (Amps),vlv8.i (Amps),vlv0.e (Volts),vlv1.e (Volts),vlv2.e (Volts),vlv3.e (Volts),vlv4.e (Volts),vlv5.e (Volts),vlv6.e (Volts),vlv7.e (Volts),vlv8.e (Volts),e3v (Volts),e5v (Volts),i5v (Amps),i3v (Amps),last_command_id (ul),tc[0] (K),tc[1] (K),tc[2] (K),tc[3] (K),tc[4] (K),mtr0.ia (Amps),mtr0.ib (Amps),mtr1.ia (Amps),mtr1.ib (Amps),i_mtr[0] (Amps),i_mtr[1] (Amps),mtr0.pos (deg),mtr1.pos (deg),mtr0.vel (step/s),mtr1.vel (step/s),mtr0.set (deg),mtr1.set (deg),mtr0.i (ul),mtr1.i (ul),mtr0.d (ul),mtr1.d (ul),mtr0.p (ul),mtr1.p (ul),mtr0.kp_err (ul),mtr1.kp_err (ul),mtr0.ki_err (ul),mtr1.ki_err (ul),mtr0.kd_err (ul),mtr1.kd_err (ul),tank_tar_pres[0] (psi),tank_tar_pres[1] (psi),tank_high_pres[0] (psi),tank_high_pres[1] (psi),tank_low_pres[0] (psi),tank_low_pres[1] (psi),epot[0] (deg),epot[1] (deg),epot[2] (deg),epot[3] (deg),test_duration (ms),micros (us),telem_rate (Hz),adc_rate (Hz),flash_mem (bytes),own_board_addr (ul),\n"
		self.packet_byte_size = 165
		self.log_string = ""
		self.num_items = 85
		
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
		self.items[45] = 'mtr0.ia' 
		self.items[46] = 'mtr0.ib' 
		self.items[47] = 'mtr1.ia' 
		self.items[48] = 'mtr1.ib' 
		self.items[49] = 'i_mtr[0]' 
		self.items[50] = 'i_mtr[1]' 
		self.items[51] = 'mtr0.pos' 
		self.items[52] = 'mtr1.pos' 
		self.items[53] = 'mtr0.vel' 
		self.items[54] = 'mtr1.vel' 
		self.items[55] = 'mtr0.set' 
		self.items[56] = 'mtr1.set' 
		self.items[57] = 'mtr0.i' 
		self.items[58] = 'mtr1.i' 
		self.items[59] = 'mtr0.d' 
		self.items[60] = 'mtr1.d' 
		self.items[61] = 'mtr0.p' 
		self.items[62] = 'mtr1.p' 
		self.items[63] = 'mtr0.kp_err' 
		self.items[64] = 'mtr1.kp_err' 
		self.items[65] = 'mtr0.ki_err' 
		self.items[66] = 'mtr1.ki_err' 
		self.items[67] = 'mtr0.kd_err' 
		self.items[68] = 'mtr1.kd_err' 
		self.items[69] = 'tank_tar_pres[0]' 
		self.items[70] = 'tank_tar_pres[1]' 
		self.items[71] = 'tank_high_pres[0]' 
		self.items[72] = 'tank_high_pres[1]' 
		self.items[73] = 'tank_low_pres[0]' 
		self.items[74] = 'tank_low_pres[1]' 
		self.items[75] = 'epot[0]' 
		self.items[76] = 'epot[1]' 
		self.items[77] = 'epot[2]' 
		self.items[78] = 'epot[3]' 
		self.items[79] = 'test_duration' 
		self.items[80] = 'micros' 
		self.items[81] = 'telem_rate' 
		self.items[82] = 'adc_rate' 
		self.items[83] = 'flash_mem' 
		self.items[84] = 'own_board_addr' 

		self.units[self.items[0]] = "ul"
		self.units[self.items[1]] = "ul"
		self.units[self.items[2]] = "ul"
		self.units[self.items[3]] = "ul"
		self.units[self.items[4]] = "ul"
		self.units[self.items[5]] = "ul"
		self.units[self.items[6]] = "ul"
		self.units[self.items[7]] = "ul"
		self.units[self.items[8]] = "psi"
		self.units[self.items[9]] = "psi"
		self.units[self.items[10]] = "psi"
		self.units[self.items[11]] = "psi"
		self.units[self.items[12]] = "psi"
		self.units[self.items[13]] = "psi"
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
		self.units[self.items[37]] = "Amps"
		self.units[self.items[38]] = "Amps"
		self.units[self.items[39]] = "ul"
		self.units[self.items[40]] = "K"
		self.units[self.items[41]] = "K"
		self.units[self.items[42]] = "K"
		self.units[self.items[43]] = "K"
		self.units[self.items[44]] = "K"
		self.units[self.items[45]] = "Amps"
		self.units[self.items[46]] = "Amps"
		self.units[self.items[47]] = "Amps"
		self.units[self.items[48]] = "Amps"
		self.units[self.items[49]] = "Amps"
		self.units[self.items[50]] = "Amps"
		self.units[self.items[51]] = "deg"
		self.units[self.items[52]] = "deg"
		self.units[self.items[53]] = "step/s"
		self.units[self.items[54]] = "step/s"
		self.units[self.items[55]] = "deg"
		self.units[self.items[56]] = "deg"
		self.units[self.items[57]] = "ul"
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
		self.units[self.items[69]] = "psi"
		self.units[self.items[70]] = "psi"
		self.units[self.items[71]] = "psi"
		self.units[self.items[72]] = "psi"
		self.units[self.items[73]] = "psi"
		self.units[self.items[74]] = "psi"
		self.units[self.items[75]] = "deg"
		self.units[self.items[76]] = "deg"
		self.units[self.items[77]] = "deg"
		self.units[self.items[78]] = "deg"
		self.units[self.items[79]] = "ms"
		self.units[self.items[80]] = "us"
		self.units[self.items[81]] = "Hz"
		self.units[self.items[82]] = "Hz"
		self.units[self.items[83]] = "bytes"
		self.units[self.items[84]] = "ul"

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
		self.dict[self.items[14]] = float((float(struct.unpack("<h", packet[27:29])[0]))/100)
		self.dict[self.items[15]] = float((float(struct.unpack("<h", packet[29:31])[0]))/100)
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
		self.dict[self.items[39]] = float((float(struct.unpack("<H", packet[60:62])[0]))/1)
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
		self.dict[self.items[51]] = float((float(struct.unpack("<h", packet[84:86])[0]))/10)
		self.dict[self.items[52]] = float((float(struct.unpack("<h", packet[86:88])[0]))/10)
		self.dict[self.items[53]] = int((float(struct.unpack("<h", packet[88:90])[0]))/1)
		self.dict[self.items[54]] = int((float(struct.unpack("<h", packet[90:92])[0]))/1)
		self.dict[self.items[55]] = float((float(struct.unpack("<h", packet[92:94])[0]))/10)
		self.dict[self.items[56]] = float((float(struct.unpack("<h", packet[94:96])[0]))/10)
		self.dict[self.items[57]] = float((float(struct.unpack("<H", packet[96:98])[0]))/100)
		self.dict[self.items[58]] = float((float(struct.unpack("<H", packet[98:100])[0]))/100)
		self.dict[self.items[59]] = float((float(struct.unpack("<H", packet[100:102])[0]))/100)
		self.dict[self.items[60]] = float((float(struct.unpack("<H", packet[102:104])[0]))/100)
		self.dict[self.items[61]] = float((float(struct.unpack("<H", packet[104:106])[0]))/100)
		self.dict[self.items[62]] = float((float(struct.unpack("<H", packet[106:108])[0]))/100)
		self.dict[self.items[63]] = float((float(struct.unpack("<h", packet[108:110])[0]))/100)
		self.dict[self.items[64]] = float((float(struct.unpack("<h", packet[110:112])[0]))/100)
		self.dict[self.items[65]] = float((float(struct.unpack("<h", packet[112:114])[0]))/100)
		self.dict[self.items[66]] = float((float(struct.unpack("<h", packet[114:116])[0]))/100)
		self.dict[self.items[67]] = float((float(struct.unpack("<h", packet[116:118])[0]))/100)
		self.dict[self.items[68]] = float((float(struct.unpack("<h", packet[118:120])[0]))/100)
		self.dict[self.items[69]] = float((float(struct.unpack("<h", packet[120:122])[0]))/10)
		self.dict[self.items[70]] = float((float(struct.unpack("<h", packet[122:124])[0]))/10)
		self.dict[self.items[71]] = float((float(struct.unpack("<h", packet[124:126])[0]))/10)
		self.dict[self.items[72]] = float((float(struct.unpack("<h", packet[126:128])[0]))/10)
		self.dict[self.items[73]] = float((float(struct.unpack("<h", packet[128:130])[0]))/10)
		self.dict[self.items[74]] = float((float(struct.unpack("<h", packet[130:132])[0]))/10)
		self.dict[self.items[75]] = float((float(struct.unpack("<h", packet[132:134])[0]))/1000)
		self.dict[self.items[76]] = float((float(struct.unpack("<h", packet[134:136])[0]))/1000)
		self.dict[self.items[77]] = float((float(struct.unpack("<h", packet[136:138])[0]))/1000)
		self.dict[self.items[78]] = float((float(struct.unpack("<h", packet[138:140])[0]))/1000)
		self.dict[self.items[79]] = int((float(struct.unpack("<I", packet[140:144])[0]))/1)
		self.dict[self.items[80]] = int((float(struct.unpack("<Q", packet[144:152])[0]))/1)
		self.dict[self.items[81]] = int((float(struct.unpack("<I", packet[152:156])[0]))/1)
		self.dict[self.items[82]] = int((float(struct.unpack("<I", packet[156:160])[0]))/1)
		self.dict[self.items[83]] = int((float(struct.unpack("<I", packet[160:164])[0]))/1)
		self.dict[self.items[84]] = int((float(struct.unpack("<B", packet[164:165])[0]))/1)
		self.log_string = str(time.clock()) + ',' + str(self.dict[self.items[7]]) + ',' + str(self.dict[self.items[8]]) + ',' + str(self.dict[self.items[9]]) + ',' + str(self.dict[self.items[10]]) + ',' + str(self.dict[self.items[11]]) + ',' + str(self.dict[self.items[12]]) + ',' + str(self.dict[self.items[13]]) + ',' + str(self.dict[self.items[14]]) + ',' + str(self.dict[self.items[15]]) + ',' + str(self.dict[self.items[16]]) + ',' + str(self.dict[self.items[17]]) + ',' + str(self.dict[self.items[18]]) + ',' + str(self.dict[self.items[19]]) + ',' + str(self.dict[self.items[20]]) + ',' + str(self.dict[self.items[21]]) + ',' + str(self.dict[self.items[22]]) + ',' + str(self.dict[self.items[23]]) + ',' + str(self.dict[self.items[24]]) + ',' + str(self.dict[self.items[25]]) + ',' + str(self.dict[self.items[26]]) + ',' + str(self.dict[self.items[27]]) + ',' + str(self.dict[self.items[28]]) + ',' + str(self.dict[self.items[29]]) + ',' + str(self.dict[self.items[30]]) + ',' + str(self.dict[self.items[31]]) + ',' + str(self.dict[self.items[32]]) + ',' + str(self.dict[self.items[33]]) + ',' + str(self.dict[self.items[34]]) + ',' + str(self.dict[self.items[35]]) + ',' + str(self.dict[self.items[36]]) + ',' + str(self.dict[self.items[37]]) + ',' + str(self.dict[self.items[38]]) + ',' + str(self.dict[self.items[39]]) + ',' + str(self.dict[self.items[40]]) + ',' + str(self.dict[self.items[41]]) + ',' + str(self.dict[self.items[42]]) + ',' + str(self.dict[self.items[43]]) + ',' + str(self.dict[self.items[44]]) + ',' + str(self.dict[self.items[45]]) + ',' + str(self.dict[self.items[46]]) + ',' + str(self.dict[self.items[47]]) + ',' + str(self.dict[self.items[48]]) + ',' + str(self.dict[self.items[49]]) + ',' + str(self.dict[self.items[50]]) + ',' + str(self.dict[self.items[51]]) + ',' + str(self.dict[self.items[52]]) + ',' + str(self.dict[self.items[53]]) + ',' + str(self.dict[self.items[54]]) + ',' + str(self.dict[self.items[55]]) + ',' + str(self.dict[self.items[56]]) + ',' + str(self.dict[self.items[57]]) + ',' + str(self.dict[self.items[58]]) + ',' + str(self.dict[self.items[59]]) + ',' + str(self.dict[self.items[60]]) + ',' + str(self.dict[self.items[61]]) + ',' + str(self.dict[self.items[62]]) + ',' + str(self.dict[self.items[63]]) + ',' + str(self.dict[self.items[64]]) + ',' + str(self.dict[self.items[65]]) + ',' + str(self.dict[self.items[66]]) + ',' + str(self.dict[self.items[67]]) + ',' + str(self.dict[self.items[68]]) + ',' + str(self.dict[self.items[69]]) + ',' + str(self.dict[self.items[70]]) + ',' + str(self.dict[self.items[71]]) + ',' + str(self.dict[self.items[72]]) + ',' + str(self.dict[self.items[73]]) + ',' + str(self.dict[self.items[74]]) + ',' + str(self.dict[self.items[75]]) + ',' + str(self.dict[self.items[76]]) + ',' + str(self.dict[self.items[77]]) + ',' + str(self.dict[self.items[78]]) + ',' + str(self.dict[self.items[79]]) + ',' + str(self.dict[self.items[80]]) + ',' + str(self.dict[self.items[81]]) + ',' + str(self.dict[self.items[82]]) + ',' + str(self.dict[self.items[83]]) + ',' + str(self.dict[self.items[84]]) + ','