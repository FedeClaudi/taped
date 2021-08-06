import time
from rich.table import Table
import pandas as pd

from myterial import orange, amber


def timestamp(just_time=False):
    """
    Returns a formatted timestamp
    """
    if not just_time:
        return time.strftime("%y%m%d_%H%M%S")
    else:
        return time.strftime("%H:%M:%S")


def _make_table(left_header, right_header, nodim=False):
    tb = Table(box=None)
    tb.add_column(
        left_header,
        header_style=f"{amber}" if nodim else f"{amber} dim",
        style=None if nodim else "dim",
    )
    tb.add_column(right_header, header_style=orange)

    return tb


def as_pandas(data):
    """Returns a dataframe if possible, an error otherwise"""
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, dict):
        return pd.DataFrame(data)
    else:
        raise TypeError(
            f"Expected a DataFrame or dict type, got: {type(data)} insead"
        )
