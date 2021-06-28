from pathlib import Path
from fcutils.path import files
import matplotlib.pyplot as plt
import numpy as np

from tpd import recorder

recorder.start()


def test_copy_file():
    recorder.copy(Path(__file__))
    recorder.copy(__file__)

    if not Path(__file__).name in [f.name for f in files(recorder.folder)]:
        raise ValueError("File not copied!")


def test_save_figure():
    f, ax = plt.subplots()

    recorder.add_figure(f, "fig1")
    recorder.add_figure(ax, "f1 from ax", svg=False)

    assert recorder.n_figures == 2

    recorder.describe()
    del f


def test_save_figures():
    f = plt.figure()
    f2 = plt.figure()
    plt.figure()

    f._save_name = "ff1"
    f2._save_name = "ff2"

    recorder.add_figures()

    assert recorder.n_figures == 4


def test_save_numpy():
    X = np.random.rand(100, 100)

    recorder.add_data(
        X, "data", fmt="npy", description="This is my random data"
    )

    assert recorder.n_data == 1


def test_save_matlab():
    X = np.random.rand(100, 100)

    recorder.add_data(
        X, "matlab_data", fmt="mat", description="This is my random data"
    )

    assert recorder.n_data == 2
