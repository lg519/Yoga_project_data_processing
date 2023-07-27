from tkinter import Tk
from tkinter.filedialog import askopenfilename
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


def choose_mvc_file():
    """
    Open a file dialog to choose the MVC file, load the selected file, and return the loaded data.

    Returns:
        data (np.array): The loaded MVC data.
    """
    root = Tk()
    root.withdraw()  # Hide the main window
    filename = filedialog.askopenfilename(title="Select MVC File")
    root.destroy()  # Destroy the main window

    # Load the data from the .mat file
    mat = loadmat(filename)

    # Assuming 'data' is the key for the data you want
    data = mat["data"]

    return data


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
    mvc_value = np.max(windowed_data)

    return mvc_value


def calculate_mvc_for_each_channel():
    """
    Opens a file picker dialog to select the MVC file and calculates the MVC values for each channel.

    Returns:
        mvc_values (array): The MVC values for each channel.
    """
    mvc_data = choose_mvc_file()

    mvc_values = []
    fig, axs = plt.subplots(mvc_data.shape[0], 1, figsize=(10, 2 * mvc_data.shape[0]))
    fig.suptitle("MVC Envelopes", fontsize=14, weight="bold")
    for i in range(mvc_data.shape[0]):  # Iterating over channels
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
        axs[i].plot(mvc_envelope)
        axs[i].set_title(f"Channel {i+1}")

    plt.tight_layout()
    plt.show()

    return np.array(mvc_values)
