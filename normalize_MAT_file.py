import numpy as np
from scipy.io import loadmat
from matplotlib import pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os
import re


# function to normalize data
def normalize_data(data, mvc_data):
    normalized_data = np.zeros(data.shape)
    for i in range(data.shape[0]):
        max_mvc = np.max(mvc_data[i, :])
        normalized_data[i, :] = data[i, :] / max_mvc
    return normalized_data


# function to plot data
def plot_data(data, channel_names, filename):
    # parse filename to get participant type and yoga position
    # Use a regex to find the date pattern "DD_MM_YYYY" in the filename
    match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
    if match:
        # Split the filename into parts before and after the date
        parts = filename.split(match.group())
        participant_type = parts[0].split("_")[0]
        yoga_position = "_".join(parts[0].split("_")[1:]).rstrip("_")
    else:
        print("Error: Incorrect filename. Could not find a date in the filename.")
    # create figure and subplots
    fig, axs = plt.subplots(
        data.shape[0], 1, sharex=True, figsize=(10, 2 * data.shape[0])
    )
    fig.suptitle(
        f"{participant_type} - {yoga_position} - normalized", fontsize=14, weight="bold"
    )
    for i in range(data.shape[0]):
        axs[i].plot(data[i, :], color="C1")
        axs[i].set_title(f"Channel {i+1} - {channel_names[i]}", fontsize=10)
        axs[i].set_ylabel("% of MVC")
    axs[-1].set_xlabel("Time")
    plt.tight_layout()
    plt.show()


# main function to load files and process data
def process_data():
    # open a file dialog to select the MVC file
    root = Tk()
    root.withdraw()
    mvc_file = filedialog.askopenfilename(
        title="Select MVC file",
        filetypes=(("mat files", "*.mat"), ("all files", "*.*")),
    )
    mvc_mat = loadmat(mvc_file)
    mvc_data = mvc_mat["data"]

    # open a file dialog to select the EMG data file to normalize
    emg_file = filedialog.askopenfilename(
        title="Select EMG file to normalize",
        filetypes=(("mat files", "*.mat"), ("all files", "*.*")),
    )
    emg_mat = loadmat(emg_file)
    emg_data = emg_mat["data"]

    # specify the channel names
    channel_names = [
        "Upper Trap (Right side)",
        "Middle Trap (Right side)",
        "Lower Trap (Right side)",
        "Serratus Anterior (Right side)",
        "Upper Trap (Left side)",
        "Middle Trap (Left side)",
        "Lower Trap (Left side)",
        "Serratus Anterior (Left side)",
    ]

    # ask the user for the number of channels to process
    num_channels = int(input("Enter the number of channels to process (max 8): "))
    assert num_channels <= len(
        channel_names
    ), "Number of channels exceeds available channels."

    # normalize and plot only the specified number of channels
    normalized_emg_data = normalize_data(
        emg_data[:num_channels, :], mvc_data[:num_channels, :]
    )

    plot_data(
        normalized_emg_data, channel_names[:num_channels], os.path.basename(emg_file)
    )


process_data()
