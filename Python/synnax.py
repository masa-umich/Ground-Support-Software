from warnings import warn
from pandas import DataFrame
from synnax import (
    Synnax,
    TimeSpan, 
    BufferedDataFrameWriter,
    TimeStamp
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
    threshold is reached, at which point the data is flushed to the cluster.
    """

    DEFAULT_SIZE_THRESHOLD = 400*500 # buffer size of 20 seconds with 20hz sampling rate,
    DEFAULT_TIME_THRESHOLD = TimeSpan.SECOND * 20

    _client: Synnax
    _wrapped: io.DataFrameWriter | None = None

    
    @_synnax_shield
    def __init__(
         self,
         channels: list[str],
         size_threshold: int = DEFAULT_SIZE_THRESHOLD,
         time_threshold: TimeSpan = DEFAULT_TIME_THRESHOLD,
    ):
        self._client = Synnax()
        self._wrapped = BufferedDataFrameWriter(
                wrapped=self._client.new_writer(
                    start=TimeStamp.now(),
                    names=channels,
                    strict=False, # Will prevent hrow
                    suppress_warnings=False,
                    skip_invalid=True,
                ),
                size_threshold=size_threshold,
                time_threshold=time_threshold,
        )

    @_synnax_shield
    def write(
        self,
        df: DataFrame,
    ):      
        if self._wrapped is not None:
            self._wrapped.write(df) 


    @_synnax_shield
    def close(self):
        if self._wrapped is not None:
            self._wrapped.close() 
        if self._client is not None:
            self._client.close() 

