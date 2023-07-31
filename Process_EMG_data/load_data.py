import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from tkinter import filedialog
from tkinter import Tk
import os
import re

from global_variables import (
    num_channels_to_plot,
    channel_names,
    sampling_frequency,
)


def extract_window(data, sampling_frequency, window_size_seconds=3):
    """
    Extract a window from the provided signal data for each channel.

    Args:
        data (np.array): The input signal data. The first dimension is channels, and the second is samples.
        sampling_frequency (int): The sampling frequency of the signal.
        window_size_seconds (int): The desired window size in seconds.

    Returns:
        windowed_data (np.array): The windowed data. The first dimension is channels, and the second is time.
    """
    # Calculate the number of samples in the window
    window_size_samples = window_size_seconds * sampling_frequency

    # Extract the middle index of the data
    middle_index = data.shape[1] // 2

    # Calculate the start and end indices of the window
    start_index = middle_index - window_size_samples // 2
    end_index = middle_index + window_size_samples // 2

    # Extract the window for each channel
    windowed_data = data[:, start_index:end_index]

    return windowed_data


def load_data():
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a file dialog
    file_path = filedialog.askopenfilename(
        title="Select recording file", filetypes=[("MAT files", "*.mat")]
    )

    # Get the filename without the extension
    filename = os.path.splitext(os.path.basename(file_path))[0]

    # Use a regex to find the date pattern "DD_MM_YYYY" in the filename
    match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
    if match:
        # Split the filename into parts before and after the date
        parts = filename.split(match.group())
        participant_type = parts[0].split("_")[0]
        yoga_position = "_".join(parts[0].split("_")[1:]).rstrip("_")
    else:
        print("Could not find a date in the filename.")

    # Load the data from the .mat file
    mat = loadmat(file_path)
    data = mat["data"]
    print(f"data.shape: {data.shape}")

    # Extract a 3-second window from the data
    windowed_data = extract_window(data, sampling_frequency)
    print(f"windowed_data.shape: {windowed_data.shape}")

    return windowed_data, participant_type, yoga_position, filename


def plot_data(
    data,
    participant_type,
    yoga_position,
    channel_names,
    num_channels_to_plot,
    sampling_frequency,
):
    # Create time array for x-axis, considering sampling frequency
    time = np.arange(0, len(data[0])) / sampling_frequency

    # Create a new figure
    fig, axs = plt.subplots(
        num_channels_to_plot, 1, sharex=True, figsize=(10, 2 * num_channels_to_plot)
    )
    fig.suptitle(f"{participant_type} - {yoga_position}", fontsize=14, weight="bold")

    # Plot the data in separate subplots
    for i in range(num_channels_to_plot):
        axs[i].plot(time, data[i, :])
        axs[i].set_title(f"Channel {i+1} - {channel_names[i]}")
        axs[i].set_ylabel("Amplitude (mV)")

    axs[-1].set_xlabel("Time (s)")

    # Show the plot
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    data, participant_type, yoga_position, filename = load_data()

    plot_data(
        data,
        participant_type,
        yoga_position,
        channel_names,
        num_channels_to_plot,
        sampling_frequency,
    )
