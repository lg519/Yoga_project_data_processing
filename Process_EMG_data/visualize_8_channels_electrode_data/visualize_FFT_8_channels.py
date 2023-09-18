import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from tkinter import filedialog
from tkinter import Tk
import os
import re
from Process_EMG_data.helpers.amplifier_config import get_channel_names

if __name__ == "__main__":
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a file dialog
    file_path = filedialog.askopenfilename(filetypes=[("MAT files", "*.mat")])

    # Get the directory path
    directory_path = os.path.dirname(file_path)

    # Get channel names using the provided function
    channel_names = get_channel_names(directory_path)

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

    # Number of channels to plot
    num_channels_to_plot = len(channel_names)

    # Create frequency array for x-axis, considering sampling frequency
    sampling_frequency = 2000  # Hz
    frequencies = np.fft.fftfreq(data.shape[1], d=1 / sampling_frequency)

    # Create a new figure
    fig, axs = plt.subplots(
        num_channels_to_plot, 1, sharex=True, figsize=(10, 2 * num_channels_to_plot)
    )
    fig.suptitle(f"{participant_type} - {yoga_position}", fontsize=14, weight="bold")

    # Plot the magnitude of the Fourier transform in separate subplots
    for i in range(num_channels_to_plot):
        spectrum = np.abs(np.fft.fft(data[i, :]))
        axs[i].plot(frequencies, spectrum)
        axs[i].set_title(f"Channel {i+1} - {channel_names[i]}")
        axs[i].set_ylabel("Magnitude")
        axs[i].set_xlim([0, sampling_frequency / 2])  # Only show positive frequencies

        # Adding vertical lines at 20Hz and 450Hz
        axs[i].axvline(20, color="r", linestyle="--", alpha=0.6)
        axs[i].axvline(450, color="r", linestyle="--", alpha=0.6)

    axs[-1].set_xlabel("Frequency (Hz)")

    # Show the plot
    plt.tight_layout()
    plt.show()
