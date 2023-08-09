from tkinter import Tk
from filtering import butter_bandpass_filter, butter_lowpass_filter
import numpy as np
from scipy.io import loadmat
from tkinter import filedialog
from rectify_signal import rectify_signal
from amplifier_config import sampling_frequency, lowcut, highcut, get_channel_names
import matplotlib.pyplot as plt
import fnmatch
import os


def choose_mvc_files():
    """
    Open a file dialog to choose the MVC files, load the selected files, and return the loaded data.

    Returns:
        datas (list of np.array): The loaded MVC data for each file.
    """
    root = Tk()
    root.withdraw()  # Hide the main window
    filenames = filedialog.askopenfilenames(title="Select MVC Files")
    root.destroy()  # Destroy the main window

    datas = []
    for filename in filenames:
        # Load the data from the .mat file
        mat = loadmat(filename)

        # Assuming 'data' is the key for the data you want
        data = mat["data"]

        datas.append(data)

    return datas


def get_mvc_files(directory_path):
    """
    Find all files in a directory with 'MVC' in their name, load these files, and return the loaded data.

    Args:
        directory (str): The directory to search for MVC files.

    Returns:
        mvc_files (list of np.array): The loaded MVC data for each file.
    """
    mvc_files = []
    for filename in os.listdir(directory_path):
        if fnmatch.fnmatch(filename, "*MVC*.mat"):
            filepath = os.path.join(directory_path, filename)
            # Load the data from the .mat file
            mat = loadmat(filepath)

            # Assuming 'data' is the key for the data you want
            data = mat["data"]

            mvc_files.append(data)

    return mvc_files


import numpy as np


def calculate_mvc(filtered_mvc_data, sampling_frequency, window_duration=0.5):
    """
    Calculate the MVC value for a single channel using a window and returns the value corresponding to the window with the maximum mean value.

    Args:
        filtered_mvc_data (np.array): The filtered MVC data for one channel.
        sampling_frequency (int): The sampling frequency of the signal.
        window_duration (int, optional): The duration of the window in seconds. Defaults to 3 seconds.

    Returns:
        mvc_value (float): The MVC value for the channel.
    """
    window_size = int(window_duration * sampling_frequency)
    max_mean_value = float("-inf")
    mvc_value = 0

    # Iterate through the entire signal with a sliding window of size window_size
    for start_index in range(0, len(filtered_mvc_data) - window_size):
        end_index = start_index + window_size
        windowed_data = filtered_mvc_data[start_index:end_index]

        # Calculate the mean value within the window
        mean_value = np.mean(windowed_data)

        # Update the mvc_value if the mean value is greater than the current max_mean_value
        if mean_value > max_mean_value:
            max_mean_value = mean_value
            mvc_value = mean_value

    return mvc_value


def calculate_mvc_for_each_channel(directory_path):
    """
    Returns:
        max_mvc_values (array): The maximum MVC values for each channel across files.
    """
    mvc_datas = get_mvc_files(directory_path)
    channel_names = get_channel_names(directory_path)
    num_channels = len(channel_names)

    max_mvc_values = []
    for i in range(num_channels):  # Iterating over channels
        mvc_values = []
        # fig, axs = plt.subplots(len(mvc_datas), 1, figsize=(10, 2 * len(mvc_datas)))
        # fig.suptitle(f"Channel {i+1} MVC Envelopes", fontsize=14, weight="bold")
        for j, mvc_data in enumerate(mvc_datas):
            # apply bandpass filter
            filtered_mvc_data = butter_bandpass_filter(
                mvc_data[i, :], lowcut, highcut, sampling_frequency
            )
            # rectify the signal
            rectified_mvc_data = rectify_signal(filtered_mvc_data)
            # extract envelpoe
            mvc_envelope = butter_lowpass_filter(
                rectified_mvc_data, cutoff=5, sampling_frequency=sampling_frequency
            )
            mvc_value = calculate_mvc(mvc_envelope, sampling_frequency)
            mvc_values.append(mvc_value)
            # # Plot MVC envelope for each channel
            # axs[j].plot(mvc_envelope)
            # axs[j].set_title(f"File {j+1}")

        max_mvc_values.append(max(mvc_values))

        # plt.tight_layout()
        # plt.show()

    return np.array(max_mvc_values)
