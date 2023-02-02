from synnax import (
    Synnax, 
    ValidationError, 
    Unreachable
)

from synnax.io import DataFrameWriter


class SynnaxLog():
    wrapped: DataFrameWriter

    def __init__(self):
        try:
            self.wrapped = Synnax()
        except ValidationError:
            print("No Synnax credentials found in keychain. Please run `synnax login` to set them up.")
        except Unreachable:
