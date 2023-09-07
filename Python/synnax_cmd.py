from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from synnax_log import new_client
import synnax as sy


class SynnaxCommander(QThread):
    sendProcessCommandSignal = pyqtSignal(dict)
    _client: sy.Synnax | None = None

    def __init__(self, server):
        super().__init__()
        self.sendProcessCommandSignal.connect(self.server.process_client_command)
        try:
            self._client = new_client()
        except Exception as e:
            self._client = None
            raise e

    def run(self):
        channels = create_channels(self._client)
        with self._client.new_streamer([ch.name for ch in channels]) as streamer:
            for frame in streamer:
                for ch in channels:
                    if ch.name in frame.keys:
                        cmd = self.parse_cmd(ch.name, frame[ch.name])
                        if cmd is not None:
                            self.sendProcessCommandSignal.emit(self.parse_cmd(ch.name, frame[ch.name]))

    def parse_cmd(self, name: str, series: sy.Series) -> dict | None:
        if len(series) == 0:
            return
        # get the last value in the series
        value = series[-1]
        if "vlv-cmd" in name:
            # get the valve number
            vlv_num = int(name.split("-")[-1])
            return {
                "function_name": "set_vlv",
                "target_board_addr": getBoardAddr("GSE Controller"),
                "timestamp": int(datetime.now().timestamp()),
                "args": [int(vlv_num), int(value)],
            }
        elif "gse-cmd-start-logging" in name:
            return {
                "function_name": "start_logging",
                "target_board_addr": getBoardAddr("GSE Controller"),
                "timestamp": int(datetime.now().timestamp()),
                "args": [],
            }
        elif "gse-cmd-stop-logging" in name:
            return {
                "function_name": "stop_logging",
                "target_board_addr": getBoardAddr("GSE Controller"),
                "timestamp": int(datetime.now().timestamp()),
                "args": [],
            }
        elif "gse-cmd-ambientize" in name:
            return {
                "function_name": "ambientize_pressure_transducers",
                "target_board_addr": getBoardAddr("GSE Controller"),
                "timestamp": int(datetime.now().timestamp()),
                "args": [],
            }


VALVE_COUNT = 32


def create_channels(client: sy.Synnax) -> list[sy.Channel]:
    channels = []

    # Create channels for the valves
    for i in range(VALVE_COUNT):
        time_ch_name = f"gse-vlv-cmd-time-{i}"
        cmd_ch_name = f"gse-vlv-cmd-{i}"
        existing = client.channels.retrieve([time_ch_name, cmd_ch_name])
        if len(existing) == 2:
            channels.extend(existing)
            continue
        time_ch = client.channels.create(
            name=time_ch_name, data_type=sy.DataType.TIMESTAMP, is_index=True
        )
        cmd_ch = client.channels.create(
            name=cmd_ch_name, data_type=sy.DataType.FLOAT32, index=time_ch.key
        )
        channels.append(time_ch)
        channels.append(cmd_ch)

    # Create channels for the GSE
    start_logging_time_ch_name = "gse-cmd-start-logging-time"
    start_logging_cmd_ch_name = "gse-cmd-start-logging"
    existing = client.channels.retrieve([start_logging_time_ch_name, start_logging_cmd_ch_name])
    if len(existing) != 2:
        time_ch = client.channels.create(
            name=start_logging_time_ch_name, data_type=sy.DataType.TIMESTAMP, is_index=True
        )
        cmd_ch = client.channels.create(
            name=start_logging_cmd_ch_name, data_type=sy.DataType.FLOAT32, index=time_ch.key
        )
        channels.append(time_ch)
        channels.append(cmd_ch)
    else:
        channels.extend(existing)

    stop_logging_time_ch_name = "gse-cmd-stop-logging-time"
    stop_logging_cmd_ch_name = "gse-cmd-stop-logging"
    existing = client.channels.retrieve([stop_logging_time_ch_name, stop_logging_cmd_ch_name])
    if len(existing) != 2:
        time_ch = client.channels.create(
            name=stop_logging_time_ch_name, data_type=sy.DataType.TIMESTAMP, is_index=True
        )
        cmd_ch = client.channels.create(
            name=stop_logging_cmd_ch_name, data_type=sy.DataType.FLOAT32, index=time_ch.key
        )
        channels.append(time_ch)
        channels.append(cmd_ch)
    else:
        channels.extend(existing)

    # Create channels for the GSE ambientize
    ambientize_time_ch_name = "gse-cmd-ambientize-time"
    ambientize_cmd_ch_name = "gse-cmd-ambientize"
    existing = client.channels.retrieve([ambientize_time_ch_name, ambientize_cmd_ch_name])
    if len(existing) != 2:
        time_ch = client.channels.create(
            name=ambientize_time_ch_name, data_type=sy.DataType.TIMESTAMP, is_index=True
        )
        cmd_ch = client.channels.create(
            name=ambientize_cmd_ch_name, data_type=sy.DataType.FLOAT32, index=time_ch.key
        )
        channels.append(time_ch)
        channels.append(cmd_ch)
    else:
        channels.extend(existing)

    return channels
