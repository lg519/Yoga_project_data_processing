import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os
import re


def plot_data(data, channel_names):
    # Compute the average muscle activity for each channel
    avg_activity = np.mean(data, axis=1)

    # Generate a bar graph of the average muscle activity
    plt.bar(
        np.arange(len(channel_names)),
        avg_activity,
    )

    # Label the bars with the channel names
    plt.xticks(np.arange(len(channel_names)), channel_names, rotation="vertical")

    # Set the y-axis label
    plt.ylabel("Mean activity (% of MVC)")

    # Show the plot
    plt.tight_layout()
    plt.show()


# Hide the main tkinter window
root = Tk()
root.withdraw()

# Open a file dialog
mvc_file_path = filedialog.askopenfilename(
    title="Select MVC file", filetypes=[("MAT files", "*.mat")]
)
file_path = filedialog.askopenfilename(
    title="Select EMG recording file", filetypes=[("MAT files", "*.mat")]
)

# Load the data from the .mat file
mat = loadmat(file_path)
mvc_mat = loadmat(mvc_file_path)

# Get the data and the MVC data
data = mat["data"]
mvc_data = mvc_mat["data"]

# Ask the user for the number of channels to plot
num_channels_to_plot = int(input("Enter the number of channels to plot: "))

# Define channel names
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

# Select subset of channels
data = data[:num_channels_to_plot, :]
mvc_data = mvc_data[:num_channels_to_plot, :]

# Rectify the signal
data = np.abs(data)

# Normalize the data by the MVC
max_mvc = np.max(mvc_data, axis=1)
normalized_data = np.zeros(data.shape)
for i in range(data.shape[0]):
    normalized_data[i, :] = data[i, :] / max_mvc[i]

# Select subset of channel names
channel_names = channel_names[:num_channels_to_plot]

# Plot the data
plot_data(normalized_data, channel_names)
