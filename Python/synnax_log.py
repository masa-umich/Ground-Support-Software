import numpy as np

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
    convert_time_units
)

from synnax import io


def _synnax_shield(func):
    """Shields a function from crashing the server"""
    backoff = False

    def wrapper(*args, **kwargs):
        nonlocal backoff
        try:
            if not backoff:
                return func(*args, **kwargs)
        except Exception as e:
            warn(f"Synnax - Unexpected error: {e}, backing off")
            if not backoff:
                backoff = True

    return wrapper


def new_client() -> Synnax:
    return Synnax(
        host="10.0.0.15",
        port=9090,
        username="synnax",
        password="seldon",
        secure=False,
    )


class SynnaxLog(io.DataFrameWriter):
    """An implementation of io.DataFrameWriter that serves as a buffer log for writing
    to a Synnax cluster. This buffer accumulates data until either the size or time
    threshold is reached, at which point the data is flushed to the ster.
    """

    DEFAULT_SIZE_THRESHOLD = 400 * 500
    # buffer size of 2 seconds with 20hz sampling rate,
    DEFAULT_TIME_THRESHOLD = TimeSpan.SECOND * 2

    _client: Synnax | None = None
    _wrapped: io.DataFrameWriter | None = None
    _started: bool = False
    _size_threshold: int
    _time_threshold: TimeSpan

    @_synnax_shield
    def __init__(
            self,
            size_threshold: int = DEFAULT_SIZE_THRESHOLD,
            time_threshold: TimeSpan = DEFAULT_TIME_THRESHOLD,
    ):
        try:
            self._client = new_client()
        except Exception as e:
            self._client = None
            raise e
        self._size_threshold = size_threshold
        self._time_threshold = time_threshold

    @_synnax_shield
    def write(
            self,
            df: DataFrame,
    ):
        df = convert_df_to_fc(df)
        if self._client is None:
            return
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
        channels = maybe_create_channels(self._client, df)
        df = df.dropna(axis="columns")
        self._wrapped = BufferedDataFrameWriter(
            wrapped=self._client.new_writer(
                TimeStamp.now(),
                channels,
                strict=False,
                suppress_warnings=True,
            ),
            size_threshold=self._size_threshold,
            time_threshold=self._time_threshold,
        )


def generate_virtual_time(start: TimeStamp, data: np.ndarray) -> np.ndarray:
    return convert_time_units(data, "us", "ns") + start


def get_elapsed_time_channel(df: DataFrame) -> np.ndarray | None:
    OPTIONS = ["ec.timestamp (hs)", "gse.timestamp (hs)", "fc.timestamp (hs)"]
    for opt in OPTIONS:
        if opt in df.columns:
            return df[opt].to_numpy(dtype=np.int64)
    return None


def maybe_create_channels(client: Synnax, df: DataFrame) -> list[str]:
    if "aux.Time" not in df.columns:
        raise ValueError("Synnax Dataframe must have a column named 'Time'")

    columns = []
    for col in df.columns.tolist():
        if col.startswith("fc"):
            columns.append(col)
    channels = client.channels.retrieve(columns, include_not_found=False)
    not_found = list()
    for ch in columns:
        _ch = [c for c in channels if c.name == ch]
        if len(_ch) == 0:
            not_found.append(ch)

    valid_channels = list()
    time_ch = [ch for ch in channels if ch.name == "aux.Time"]
    if len(time_ch) == 0:
        time_ch = client.channels.create(
            name="aux.Time", data_type=DataType.TIMESTAMP, is_index=True
        )
        valid_channels.append(time_ch.name)
    else:
        time_ch = time_ch[0]

    to_create = list[Channel]()
    for col in columns:
        samples = df[col].to_numpy()
        if samples.dtype != np.int64 and samples.dtype != np.float64:
            continue
        if col in not_found:
            if col != "Time":
                to_create.append(
                    Channel(name=col, data_type=np.float64, index=time_ch.key)
                )
        else:
            ch = [ch for ch in channels if ch.name == col][0]
            if can_cast(samples.dtype, ch.data_type.np):
                valid_channels.append(ch.name)

    if len(to_create) > 0:
        print(f"[synnax] - creating {len(to_create)} channels")
        channels = client.channels.create(to_create)
        valid_channels.extend([ch.name for ch in channels])

    return valid_channels


def to_fc(name: str) -> str:
    return f"aux.{name}"


def from_fc(name: str) -> str:
    return name[4:]


def convert_df_to_fc(df: DataFrame) -> DataFrame:
    df.columns = [to_fc(col) for col in df.columns]
    return df
