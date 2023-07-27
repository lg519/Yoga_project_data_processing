from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from load_data import load_data
from filtering import butter_bandpass_filter, find_filter_values
from rms_envelope import compute_rms_envelope
import numpy as np
from scipy.io import loadmat
from tkinter import filedialog
from rms_envelope import rectify_signal
from low_pass_filtering import butter_lowpass_filter
from fft_processing import compute_fft
from global_variables import (
    sampling_frequency,
)
import matplotlib.pyplot as plt

from global_variables import num_channels_to_plot


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


def calculate_mvc(filtered_mvc_data, sampling_frequency):
    """
    Calculate the MVC value for a single channel using a 3-second window in the middle of the signal.

    Args:
        filtered_mvc_data (np.array): The filtered MVC data for one channel.
        sampling_frequency (int): The sampling frequency of the signal.

    Returns:
        mvc_value (float): The MVC value for the channel.
    """
    middle_index = len(filtered_mvc_data) // 2
    window_size = 3 * sampling_frequency  # window size for 3 seconds
    start_index = middle_index - window_size // 2
    end_index = middle_index + window_size // 2
    windowed_data = filtered_mvc_data[start_index:end_index]

    # Calculate the MVC value as the average value within the window
    mvc_value = np.mean(windowed_data)

    return mvc_value


def calculate_mvc_for_each_channel():
    """
    Opens a file picker dialog to select the MVC files and calculates the MVC values for each channel.

    Returns:
        max_mvc_values (array): The maximum MVC values for each channel across files.
    """
    mvc_datas = choose_mvc_files()

    max_mvc_values = []
    for i in range(num_channels_to_plot):  # Iterating over channels
        mvc_values = []
        fig, axs = plt.subplots(len(mvc_datas), 1, figsize=(10, 2 * len(mvc_datas)))
        fig.suptitle(f"Channel {i+1} MVC Envelopes", fontsize=14, weight="bold")
        for j, mvc_data in enumerate(mvc_datas):
            xf, yf = compute_fft(mvc_data[i, :], sampling_frequency)
            highcut, lowcut = find_filter_values(yf)
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
            # Plot MVC envelope for each channel
            axs[j].plot(mvc_envelope)
            axs[j].set_title(f"File {j+1}")

        max_mvc_values.append(max(mvc_values))

        plt.tight_layout()
        plt.show()

    return np.array(max_mvc_values)
