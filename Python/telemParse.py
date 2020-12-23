import time
import struct

# TODO: autogenerate section below
class TelemParse:
    def __init__(self):
        self.csv_header = "Time (s),valve_states (),pressure[0] (counts),pressure[1] (counts),pressure[2] (counts),pressure[3] (counts),pressure[4] (counts),pressure[5] (counts),pressure[6] (counts),pressure[7] (counts),pressure[8] (counts),pressure[9] (counts),pressure[10] (counts),pressure[11] (counts),pressure[12] (counts),pressure[13] (counts),pressure[14] (counts),pressure[15] (counts),pressure[16] (counts),pressure[17] (counts),pressure[18] (counts),pressure[19] (counts),pressure[20] (counts),pressure[21] (count),samplerate (Hz),main_cycle_time (microseconds),motor_cycle_time (microseconds),adc_cycle_time (microseconds),telemetry_cycle_time (microseconds),ebatt (Volts),ibus (Amps),telemetry_rate (Hz),STATE (),load[0] (counts),load[1] (counts),load[2] (counts),load[3] (counts),load[4] (counts),ivlv[0] (Amps),ivlv[1] (Amps),ivlv[2] (Amps),ivlv[3] (Amps),ivlv[4] (Amps),ivlv[5] (Amps),ivlv[6] (Amps),ivlv[7] (Amps),ivlv[8] (Amps),ivlv[9] (Amps),ivlv[10] (Amps),ivlv[11] (Amps),ivlv[12] (Amps),ivlv[13] (Amps),ivlv[14] (Amps),ivlv[15] (Amps),ivlv[16] (Amps),ivlv[17] (Amps),ivlv[18] (Amps),ivlv[19] (Amps),ivlv[20] (Amps),ivlv[21] (Amps),ivlv[22] (Amps),ivlv[23] (Amps),ivlv[24] (Amps),ivlv[25] (Amps),ivlv[26] (Amps),ivlv[27] (Amps),ivlv[28] (Amps),ivlv[29] (Amps),ivlv[30] (Amps),ivlv[31] (Amps),evlv[0] (Volts),evlv[1] (Volts),evlv[2] (Volts),evlv[3] (Volts),evlv[4] (Volts),evlv[5] (Volts),evlv[6] (Volts),evlv[7] (Volts),evlv[8] (Volts),evlv[9] (Volts),evlv[10] (Volts),evlv[11] (Volts),evlv[12] (Volts),evlv[13] (Volts),evlv[14] (Volts),evlv[15] (Volts),evlv[16] (Volts),evlv[17] (Volts),evlv[18] (Volts),evlv[19] (Volts),evlv[20] (Volts),evlv[21] (Volts),evlv[22] (Volts),evlv[23] (Volts),evlv[24] (Volts),evlv[25] (Volts),evlv[26] (Volts),evlv[27] (Volts),evlv[28] (Volts),evlv[29] (Volts),evlv[30] (Volts),evlv[31] (Volts),e3v (Volts),e5v (Volts),e28v (Volts),i5v (amps),i3v (amps),BOARD_ID (),last_packet_number (),last_command_id (),tbrd (),tvlv (),tmtr (),error_code (),LOGGING_ACTIVE (),current_page (),tc[0] (K),tc[1] (K),tc[2] (K),tc[3] (K),tc[4] (K),tc[5] (K),tc[6] (K),tc[7] (K),tc[8] (K),tc[9] (K),tc[10] (K),tc[11] (K),tc[12] (K),tc[13] (K),tc[14] (K),tc[15] (K),rtd[0] (K),rtd[1] (K),rtd[2] (K),rtd[3] (K),rtd[4] (K),rtd[5] (K),rtd[6] (K),rtd[7] (K),zero (),zero (),zero (),zero (),zero (),zero (),zero (),zero (),zero (),zero (),zero (),zero (),\n"
        self.valve_states = 0
        self.pressure = [0]*22
        self.samplerate = 0
        self.motor_setpoint = [0]*4
        self.main_cycle_time = 0
        self.motor_cycle_time = 0
        self.adc_cycle_time = 0
        self.telemetry_cycle_time = 0
        self.ebatt = 0
        self.ibus = 0
        self.telemetry_rate = 0
        self.motor_control_gain = [0]*4
        self.motor_position = [0]*4
        self.motor_pwm = [0]*4
        self.count1 = 0
        self.count2 = 0
        self.count3 = 0
        self.STATE = 0
        self.load = [0]*5
        self.thrust_load = 0
        self.thermocouple = [0]*4
        self.ivlv = [0]*32
        self.evlv = [0]*32
        self.LOG_TO_AUTO = 0
        self.auto_states = 0
        self.debug = [0]*8
        self.e5v = 0
        self.e3v = 0
        self.BOARD_ID = 0
        self.last_packet_number = -1
        self.last_command_id = -1
        self.imtr = [0]*2
        self.tbrd = 0
        self.tvlv = 0
        self.tmtr = 0
        self.error_code = 0
        self.LOGGING_ACTIVE = 0
        self.current_page = -1
        self.zero = 0
        self.e28v = 0
        self.i3v = 0
        self.i5v = 0
        self.tc = [0]*16
        self.rtd = [0]*8
        self.log_string = ""
        self.num_items = 152
        
        self.dict = {}
        
        self.items = [''] * self.num_items
        self.items[0] = 'valve_states' 
        self.items[1] = 'pressure[0]' 
        self.items[2] = 'pressure[1]' 
        self.items[3] = 'pressure[2]' 
        self.items[4] = 'pressure[3]' 
        self.items[5] = 'pressure[4]' 
        self.items[6] = 'pressure[5]' 
        self.items[7] = 'pressure[6]' 

    def parse_packet(self, packet):
        byte_rep = packet[0:4]
        self.valve_states = int((float(struct.unpack("<I", byte_rep)[0]))/1)
        self.dict[self.items[0]] = self.valve_states
        byte_rep = packet[4:6]
        self.pressure[0] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[1]] = self.pressure[0]
        byte_rep = packet[6:8]
        self.pressure[1] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[2]] = self.pressure[1]
        byte_rep = packet[8:10]
        self.pressure[2] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[3]] = self.pressure[2]
        byte_rep = packet[10:12]
        self.pressure[3] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[4]] = self.pressure[3]
        byte_rep = packet[12:14]
        self.pressure[4] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[5]] = self.pressure[4]
        byte_rep = packet[14:16]
        self.pressure[5] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[6]] = self.pressure[5]
        byte_rep = packet[16:18]
        self.pressure[6] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[7]] = self.pressure[6]
        byte_rep = packet[18:20]
        self.pressure[7] = float((float(struct.unpack("<h", byte_rep)[0]))/1)
        self.dict[self.items[8]] = self.pressure[7]
        byte_rep = packet[20:22]