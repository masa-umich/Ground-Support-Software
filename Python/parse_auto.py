from s2Interface import S2_Interface
import traceback

def parse_auto(command_list: list, i: int = 0):
    """Recursive autosequence parser

    Args:
        command_list (list): List of autosequence commands
        i (int, optional): Index in autosequence. Defaults to 0.

    Returns:
        list: unrolled autosequence or loop
        int: ending index in autosequence or loop
    """
    interface = S2_Interface()
    commands = list(interface.get_cmd_names_dict().keys())
    try:
        # unpack loops and compile into single sequence
        constructed = []
        loop = []
        loop_len = 0
        #in_loop = False
        while i < len(command_list):  # loop parsing
            line = command_list[i]
            cmd = line[0]
            args = line[1:]
            #print(line)

            if cmd == "loop":  # start loop
                loop_len = int(args[0])
                #in_loop = True
                (loop, i) = parse_auto(command_list, i+1)
                constructed += (loop * loop_len)
            elif cmd in (commands + ["set_addr", "delay"]):  # add commands to loop
                constructed.append(line)
            elif cmd == "auto":
                seq = args[0]
                path = "autos/" + str(seq) + ".txt"
                with open(path) as f:
                    new_lines = f.read().splitlines()
                auto = []
                for new_line in new_lines:  # loop parsing
                    auto.append(new_line.lstrip().lower().split(" "))
                constructed += parse_auto(auto)[0]
            elif cmd == "end_loop":  # stop loop and add to sequence
                return (constructed, i)

            i+=1
        return (constructed, i)
    except:
        traceback.print_exc()
        return ([], i)
        