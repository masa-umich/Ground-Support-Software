from numpy import can_cast
from warnings import warn
from pandas import DataFrame
from synnax import (
    DataType,
    Synnax,
    TimeSpan,
    BufferedDataFrameWriter,
    TimeStamp,
    Channel,
)

from synnax import io


def _synnax_shield(func):
    """Shields a function from crashing the server"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return warn(f"Synnax - Unexpected error: {e}")

    return wrapper


class SynnaxLog(io.DataFrameWriter):
    """An implementation of io.DataFrameWriter that serves as a buffer log for writing
    to a Synnax cluster. This buffer accumulates data until either the size or time
    threshold is reached, at which point the data is flushed to the ster.
    """

    DEFAULT_SIZE_THRESHOLD = (
        400 * 500
    )  # buffer size of 20 seconds with 20hz sampling rate,
    DEFAULT_TIME_THRESHOLD = TimeSpan.SECOND * 30

    _client: Synnax
    _wrapped: io.DataFrameWriter | None = None
    _started: bool = False
    _size_threshold: int
    _time_threshold: TimeSpan

    def __init__(
        self,
        size_threshold: int = DEFAULT_SIZE_THRESHOLD,
        time_threshold: TimeSpan = DEFAULT_TIME_THRESHOLD,
    ):
        self._client = Synnax(
            host="10.0.0.15",
            port=9090,
            username="synnax",
            password="seldon",
        )
        self._size_threshold = size_threshold
        self._time_threshold = time_threshold

    @_synnax_shield
    def write(
        self,
        df: DataFrame,
    ):
        if not self._started:
            self._new_writer(df)
            self._started = True
        if self._wrapped is not None:
            self._wrapped.write(df)

    @_synnax_shield
    def close(self):
        if self._wrapped is not None:
            self._wrapped.close()
        if self._client is not None:
            self._client.close()

    def _new_writer(self, df: DataFrame):
        """Open a new writer for the channels in the given dataframe."""
        assert self._client is not None
        df = df.dropna(axis="columns")
        channels, not_found = self._client.channels.retrieve(
            names=df.columns.tolist(), include_not_found=True
        )

        valid_channels = list()
        invalid_channels = list()
        time_ch = [ch for ch in channels if ch.name == "Time"]
        if len(time_ch) == 0:
            time_ch = self._client.channels.create(
                name="Time", data_type=DataType.TIMESTAMP, is_index=True
            )
            valid_channels.append(time_ch.name)
        else:
            time_ch = time_ch[0]

        to_create = list[Channel]()
        for col in df.columns:
            samples = df[col].to_numpy()
            if col in not_found:
                to_create.append(
                    Channel(name=col, data_type=samples.dtype, index=time_ch.key)
                )
            else:
                ch = [ch for ch in channels if ch.name == col][0]
                if can_cast(samples.dtype, ch.data_type.np):
                    valid_channels.append(ch.name)
                else:
                    invalid_channels.append(ch.name)

        if len(to_create) > 0:
            print(f"Creating {len(to_create)} channels")
            channels = self._client.channels.create(to_create)
            valid_channels.extend([ch.name for ch in channels])

        self._wrapped = BufferedDataFrameWriter(
            wrapped=self._client.new_writer(
                start=TimeStamp.now(),
                names=valid_channels,
                strict=False,  # Will prevent hrow
                suppress_warnings=False,
                skip_invalid=True,
            ),
            size_threshold=self._size_threshold,
            time_threshold=self._time_threshold,
        )
