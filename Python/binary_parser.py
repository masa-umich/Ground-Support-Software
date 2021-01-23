import sys
from s2Interface import S2_Interface
interface = S2_Interface()
parser = interface.parser

file = open(sys.argv[1], 'rb')
datalog = open(sys.argv[1]+'_datalog.csv', 'w')
datalog.write(parser.csv_header)

packets = []
this_line = []
n = 0
while True:
	b = file.read(1)
	# print(b)
	if not b:
		break;
	if b == b'\x00':
		n += 1
		packets.append(this_line)
		this_line = []
	else:
		this_line += b

print(n)

for packet in packets:
	unstuffed = interface.unstuff_packet(packet)
	try:
		parser.parse_packet(unstuffed)
	except:
		pass
	#if not(parser.valve_states == 65535):
	#	datalog.write(parser.log_string+'\n')
	datalog.write(parser.log_string+'\n')