import traceback
import sys


class BinaryParser:
    """
    Converts flash binaries into CSV files
    """

    def __init__(self, interface):
        self.interface = interface

        self.dataframe = {}
        for channel in self.interface.channels:
            self.dataframe[channel] = ""

    def get_logstring(self):
        """Constructs a datalog CSV row from current data

        Returns:
            str: Formatted CSV row
        """

        logstring = ""
        for channel in self.interface.channels:
            logstring += "%s," % (self.dataframe[channel])
        return logstring

    def bin2csv(self, filename: str, verbose: bool = True):
        """Converts a binary flash dump to a .CSV

        Args:
            filename (str): Filename of binary dump
        """

        file = open(filename, 'rb')
        datalog = False  # Initially - so it knows it hasn't opened anything yet

        packets = []
        this_line = []
        n = 0
        while True:
            b = file.read(1)
            if not b:
                break
            if b == b'\x00':
                n += 1
                packets.append(this_line)
                this_line = []
            else:
                this_line += b

        if verbose:
            print("Num Packets: %s, %s" % (n, len(packets)))

        num_cons_zeros = 0  # Track consecutive 0s found in the binary - 2000 0's in a row signals the start of a log
        num_logs = 0
        open_new_file = False
        for packet in packets:
            try:
                if len(packet) > 0:
                    num_cons_zeros = 0

                    if open_new_file:
                        datalog = open(filename.rstrip(".bin")+'_datalog_' + str(num_logs) + '.csv', 'w')  # tests are 1 indexed for consistency
                        datalog.write(self.interface.get_header())  # csv header
                        open_new_file = False

                    if verbose:
                        print(len(packet))
                        print(bytes(packet))
                    packet_addr = self.interface.parse_packet(packet)
                    #print
                    if packet_addr != -1:
                        new_data = self.interface.board_parser[packet_addr].dict
                        #print(new_data)
                        prefix = self.interface.getPrefix(
                            self.interface.getName(packet_addr))
                        for key in new_data.keys():
                            self.dataframe[str(prefix + key)] = new_data[key]
                        #print(self.dataframe)
                        if datalog:
                            datalog.write(self.get_logstring()+'\n')
                else:
                    num_cons_zeros += 1
                    if (num_cons_zeros >= 2000):  # Test delimiter
                        open_new_file = True
                        num_cons_zeros = 0
                        num_logs += 1
                        if datalog:
                            datalog.close()
            except:
                traceback.print_exc()
        if datalog:
            datalog.close()


if __name__ == "__main__":
    from s2Interface import S2_Interface
    binparse = BinaryParser(interface = S2_Interface())

    args = len(sys.argv)
    if args == 3:
        FILENAME = str(sys.argv[1])
        IS_VERBOSE = bool(int(sys.argv[2]))
    elif args == 2:
        FILENAME = str(sys.argv[1])
        IS_VERBOSE = True
    else:
        FILENAME = "flash_dump/test.bin"
        IS_VERBOSE = True

    print(FILENAME, IS_VERBOSE)
    binparse.bin2csv(filename=FILENAME, verbose=IS_VERBOSE)
