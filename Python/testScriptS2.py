import time
import serial
import struct
import serial.tools.list_ports
from s2Interface import S2_Interface

s2_interface = S2_Interface()
ports = s2_interface.scan()
# print(ports)

s2_interface.connect("COM7", 115200, 2)
set_vlv = {
    "function_name": "set_vlv",
    "target_board_addr": 0,
    "timestamp": 99,
    "args": [0, 1],
}

start = {
    "function_name": "start_logging",
    "target_board_addr": 3,
    "timestamp": 100,
    "args": [],
}

stop = {
    "function_name": "stop_logging",
    "target_board_addr": 3,
    "timestamp": 101,
    "args": [],
}

erase = {
    "function_name": "wipe_flash",
    "target_board_addr": 3,
    "timestamp": 102,
    "args": [],
}

zero_stepper = {
    "function_name": "set_stepper_zero",
    "target_board_addr": 3,
    "timestamp": 103,
    "args": [0],
}

set_arm_state = {
    "function_name": "set_state",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [1],
}

set_run_state = {
    "function_name": "set_state",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [2],
}

set_target_pressure = {
    "function_name": "set_control_target_pressure",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [1, 35.1],
}

set_lower_pressure = {
    "function_name": "set_low_toggle_percent",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [1, 0.8],
}

set_upper_pressure = {
    "function_name": "set_high_toggle_percent",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [1, 1.2],
}

ambientize_pts = {
    "function_name": "ambientize_pressure_transducers",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [],
}

set_control_loop_dur = {
    "function_name": "set_control_loop_duration",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [2000],
}

set_stepper_speed = {
    "function_name": "set_stepper_speed",
    "target_board_addr": 3,
    "timestamp": 104,
    "args": [1, 1000],
}

move_stepper = {
    "function_name": "set_stepper_pos",
    "target_board_addr": 3,
    "timestamp": 103,
    "args": [0, 1800],
}

enable_tank = {
    "function_name": "set_presstank_status",
    "target_board_addr": 3,
    "timestamp": 103,
    "args": [0, 1],
}

set_mtr_kp = {
    "function_name": "set_kp",
    "target_board_addr": 3,
    "timestamp": 103,
    "args": [1, 9.69],
}

ambientize_pot = {
    "function_name": "ambientize_pot",
    "target_board_addr": 3,
    "timestamp": 103,
    "args": [0],
}


def test_set_vlv():
    s2_interface.s2_command(set_vlv)


def test_set_stepper_speed():
    s2_interface.s2_command(set_stepper_speed)
    time.sleep(1)
    s2_interface.s2_command(zero_stepper)
    time.sleep(1)
    s2_interface.s2_command(move_stepper)


def test_set_press():
    s2_interface.s2_command(set_target_pressure)
    time.sleep(0.1)
    s2_interface.s2_command(set_lower_pressure)
    time.sleep(0.1)
    s2_interface.s2_command(set_upper_pressure)


def test_set_state_control():
    s2_interface.s2_command(set_arm_state)
    time.sleep(0.2)
    s2_interface.s2_command(set_run_state)


def test_set_control_loop_dur():
    s2_interface.s2_command(set_control_loop_dur)
    time.sleep(0.1)


def test_ambientize_pts():
    s2_interface.s2_command(ambientize_pts)
    time.sleep(0.1)


def test_stepper():
    s2_interface.s2_command(zero_stepper)
    time.sleep(0.1)
    s2_interface.s2_command(move_stepper)
    # time.sleep(6)
    # s2_interface.s2_command(zero_stepper)
    # time.sleep(2)
    # s2_interface.s2_command(move_stepper)


def test_valve():
    s2_interface.s2_command(set_vlv)
    time.sleep(1)


def test_flash():
    s2_interface.s2_command(erase)
    time.sleep(5)
    s2_interface.s2_command(start)
    time.sleep(1)
    s2_interface.s2_command(stop)
    time.sleep(1)
    with open("deleteme.txt", "w+") as command_log:
        s2_interface.download_flash(3, 103, command_log)


def test_telem():
    while 1:
        parse_status = 0
        parse_status = s2_interface.parse_serial()
        if parse_status == 1:
            print(s2_interface.parser.dict)  # get telem values
            print(s2_interface.parser.units)  # get units


def test_enable_tank():
    s2_interface.s2_command(enable_tank)


def test_set_mtr_kp():
    s2_interface.s2_command(set_mtr_kp)


def test_ambientize_pot():
    s2_interface.s2_command(ambientize_pot)


# function calls for tests go here

# test_stepper()
test_set_vlv()
# test_ambientize_pot()
# test_set_control_loop_dur()
# test_set_state_control()
print(s2_interface.channels)
print(s2_interface.num_valves)
print(s2_interface.num_motors)

# print(s2_interface.units)
