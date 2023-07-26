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


def load_data():
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a file dialog
    file_path = filedialog.askopenfilename(filetypes=[("MAT files", "*.mat")])

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

    # Assuming 'data' is the key for the data you want
    data = mat["data"]

    return data, participant_type, yoga_position, filename


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
