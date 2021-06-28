from tpd import recorder

recorder.start(
    # base_folder='my_computer/my_data',
    # name='simulation_2'
)
"""
    Creates a folder 'simulation_2' in the 'base_folder'
    From now on, all data, logs and plots will be saved in
        my_computer/my_data/simulation_2
"""

# all logs will be saved in a .log file
from loguru import logger

logger.info("I cant wait to check the logs later!")


# you can add data easily
import numpy as np

X = np.random.rand(100, 100)
recorder.add_data(X, "my_results", fmt="npy")  # or 'mat' for matlab


# and save plots
import matplotlib.pyplot as plt

f = plt.figure()
recorder.add_figure(f, "first plot", svg=True)
plt.close(f)

# and save multiple figures at once
f1 = plt.figure()
f2 = plt.figure()

f1._save_name = "first of two"
f2._save_name = "second of two"
recorder.add_figures()

# finally, you can check what's saved so far
recorder.describe()
