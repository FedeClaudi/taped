from pathlib import Path
from typing import Union
import numpy as np
from loguru import logger
from rich.logging import RichHandler
import matplotlib.pyplot as plt
from shutil import copyfile
from rich import print
from scipy.io import savemat
import json
import pandas as pd
import csv

from fcutils import path as fcpath
from fcutils.plot.figure import save_figure
from pyinspect.panels import Report
from myterial import salmon, green, green_light, blue_light, orange

from tpd import utils


def raise_if_not_started(fn):
    def wrapper(self, *args, **kwargs):
        if not self.started_status:
            raise ValueError(
                "Recorded must be started first, call `recorder.start()`"
            )
        return fn(self, *args, **kwargs)

    return wrapper


class Recorder:
    def __init__(self):
        self.started_status = False
        self.saved_figures = []
        self.saved_data = []
        self.folder = "not yet startd: call `recorder.start()...)`"
        self.name = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Data Plots Logs - recorder: {self.folder}"

    @property
    def n_figures(self):
        """
            Number of saved figures
        """
        return len(self.saved_figures)

    @property
    def n_data(self):
        """
            Number of saved data fies
        """
        return len(self.saved_data)

    @property
    def n_files(self):
        """
            Total number of files in folder
        """
        return len(fcpath.files(self.folder))

    def start(
        self,
        base_folder: Union[str, Path] = None,
        name: str = None,
        timestamp: bool = True,
    ):
        self.started = utils.timestamp()
        self.started_status = True

        # get inputs
        self.base_folder = (
            Path(base_folder) if base_folder is not None else Path("./cache")
        )
        self.name = name or f"dpl_log"

        if timestamp:
            self.name += f"_{utils.timestamp()}"
        # create folders
        if not self.base_folder.exists():
            logger.warning(
                f'The base folder does not exist: "{self.base_folder}", creating it.'
            )
            self.base_folder.mkdir()

        self.folder = self.base_folder / self.name
        if not self.folder.exists():
            logger.warning(
                f'The destination folder does not exist: "{self.folder}", creating it.'
            )
            self.folder.mkdir(exist_ok=True)

        # start logging
        logger.configure(
            handlers=[
                {"sink": RichHandler(markup=True), "format": "{message}"}
            ]
        )
        log_file_path = self.folder / "log.log"
        if log_file_path.exists():
            log_file_path.unlink()
        logger.add(log_file_path)

        logger.debug(f"DPL - Saving data and logs to {self.folder}")
        logger.debug(f"Saving log file to: {str(log_file_path)}")

    @raise_if_not_started
    def copy(self, source: Union[str, Path]):
        """
            Copy a source file to the logs folder
        """
        source = Path(source)
        dest = self.folder / source.name

        logger.debug(f'Copying "{source}" to "{dest}"')
        if dest.exists():
            logger.warning("Source file exists already! OVERWRITING")
        copyfile(source, dest)

    @raise_if_not_started
    def add_data(
        self,
        data: np.ndarray,
        name: str,
        fmt: str = "npy",
        description: str = None,
    ):
        """
            Saves data from a numpy array to file.
            Can save to different formats (numpy, matlab...).
            If a 'description' is passed, a .txt file is saved describing what the
            data is. 
        """
        logger.debug(
            f'Saving data to file "{name}" with format {fmt}\nDescription: "{description}"'
        )

        # get destination path
        dest = self.folder / (name + "." + fmt)
        if dest.exists():
            logger.warning(
                f"Trying to save data to a file, but the destination file exists already - OVERWRITING"
            )

        # save data
        if fmt == "npy":
            np.save(dest, data)
        elif fmt == "mat":
            savemat(dest, mdict={name: data})
        elif fmt == "h5":
            # assumes the data are passed as a dataframe or dict
            utils.as_pandas(data).to_hdf(dest, key="hdf")
        elif fmt == "json":
            # assumes the data are passed as a dict
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        elif fmt == "csv":
            # assumes that data are a dict or pandas dataframe
            if isinstance(data, pd.DataFrame):
                data.to_csv(dest)
            else:
                with open(dest, "w", encoding="utf8", newline="") as f:
                    writer = csv.DictWriter(f, data.keys())
                    writer.writeheader()
                    writer.writerow(data)
        else:
            raise ValueError(f'Cannot save data to format: "{fmt}"')

        # save data description
        if description is not None:
            self.add_text(description, name=description)

        self.saved_data.append(dest)

    @raise_if_not_started
    def add_text(self, text: str, name="str"):
        """
            Saves a name.txt file with the text string
        """
        logger.debug(f"Writing text to: {name}.txt")
        path = self.folder / (name + ".txt")
        with open(path, "w") as dout:
            dout.write(text)

    @raise_if_not_started
    def add_figure(
        self, figure: Union[plt.Figure, plt.Axes], name: str, svg: bool = True
    ):
        """
            Saves a matplotlib figure to file
        """
        dest = self.folder / name
        logger.debug(f"Saving figure to: {dest}")

        if isinstance(figure, plt.Axes):
            figure = figure.figure
        save_figure(figure, dest, svg=svg)
        self.saved_figures.append(dest)

    @raise_if_not_started
    def add_figures(self, svg: bool = True):
        """
            Saves all open matplotlb figures, it assumes that each figure
            has a '._save_name' attribute with the name to use for saving.
        """
        # get all open figures
        figures = list(map(plt.figure, plt.get_fignums()))
        for figure in figures:
            try:
                self.add_figure(figure, figure._save_name, svg=svg)
            except AttributeError:
                logger.warning(
                    "Could not save an open figure since it did not have an `_save_name` attribute"
                )

    @raise_if_not_started
    def describe(self):
        if self.name is None:
            logger.warning(
                "recorder is not properly startd yet, call `recorder.start(...)` first"
            )
            return
        print("\n\n")
        rep = Report(
            title=f"LOGS: {self.name}",
            color=salmon,
            dim=orange,
            accent=orange,
            show_info=True,
        )

        rep.add(f'Logs saved at: [{blue_light}]"{self.folder}"')
        rep.add(f"Started at: [{blue_light}]{self.started}")

        # saved figures
        rep.spacer()
        rep.add(f"Saved: [bold {orange}]{len(self.saved_figures)}[/] figures:")
        figs_table = utils._make_table("#", "name")
        for n, fl in enumerate(self.saved_figures):
            figs_table.add_row(str(n), f"{fl.name}.png")

        rep.add(figs_table, "rich")

        # saved data
        rep.spacer()
        rep.add(f"Saved: [bold {orange}]{len(self.saved_data)}[/] data:")
        data_table = utils._make_table("#", "name")
        for n, fl in enumerate(self.saved_data):
            data_table.add_row(str(n), f"{fl.name}")
        rep.add(data_table, "rich")

        rep.print()

        # list files in destination folder
        files_table = utils._make_table("name", "size", nodim=True)
        for n, f in enumerate(fcpath.files(self.folder)):
            files_table.add_row(
                f"[{green_light}]{n} " + str(f.name),
                f"[{blue_light}]{fcpath.size(f)}",
            )
        print(f"\n[bold {green}]Files in destination folder ({self.folder})\n")
        print(files_table)
        print(
            f"[dim {green_light}]Total number of files: [dim {blue_light}]{self.n_files}"
        )


if __name__ == "__main__":
    rec = Recorder()
    rec.start()
    rec.add_data([1, 2], "test")
