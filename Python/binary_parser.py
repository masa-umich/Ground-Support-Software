import traceback
import sys

import pandas as pd
from synnax import TimeStamp

from synnax_log import generate_virtual_time, get_elapsed_time_channel


class BinaryParser:
    """
    Converts flash binaries into CSV files
    """

    def __init__(self, interface):
        self.interface = interface

        self.dataframe = pd.DataFrame()
        self.data_list = []

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

        file = open(filename, "rb")
        datalog = False  # Initially - so it knows it hasn't opened anything yet

        # print("loading file...")

        packets = []
        this_line = []
        n = 0
        while True:
            b = file.read(1)
            if not b:
                break
            if b == b"\x00":
                n += 1
                packets.append(this_line)
                this_line = []
            else:
                this_line += b

        if verbose:
            print("Num Packets: %s, %s" % (n, len(packets)))

        # print("reading packets...")

        num_cons_zeros = 0  # Track consecutive 0s found in the binary - 2000 0's in a row signals the start of a log
        num_logs = 0
        open_new_file = False
        counter = 0
        for i, packet in enumerate(packets):
            try:
                if len(packet) > 0:
                    num_cons_zeros = 0
                    if open_new_file:
                        datalog =filename.rstrip(".bin") + "_datalog_" + str(num_logs) + ".csv"
                        open_new_file = False
                    if verbose:
                        print(len(packet))
                        print(bytes(packet))
                    packet_addr, packet_type = self.interface.parse_packet(packet)
                    # print
                    if packet_addr != -1:
                        print(packet_addr)
                        # print the progress
                        counter += 1
                        if counter > 100:
                            print(f"Progress: {i/len(packets)}")
                            counter = 0

                        new_data = self.interface.board_parser[packet_addr].dict
                        prefix = self.interface.getPrefix(
                            self.interface.getName(packet_addr)
                        )
                        if datalog:
                            self.data_list.append({f"{prefix}{key} (hs)": new_data[key] for key in new_data.keys()})
                else:
                    num_cons_zeros += 1
                    print("Opening new file")
                    if num_cons_zeros >= 2000:  # Test delimiter
                        open_new_file = True
                        num_cons_zeros = 0
                        num_logs += 1
            except:
                traceback.print_exc()

        self.dataframe = pd.DataFrame.from_dict(self.data_list)
        self.dataframe = self.dataframe.dropna(axis=1, how="all")
        channel = get_elapsed_time_channel(self.dataframe)
        if channel is not None:
            self.dataframe["FCTime"] = generate_virtual_time(TimeStamp.now(), channel)

        if datalog:
            self.dataframe.to_csv(datalog, index=False)

if __name__ == "__main__":
    from s2Interface import S2_Interface

    binparse = BinaryParser(interface=S2_Interface())

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
