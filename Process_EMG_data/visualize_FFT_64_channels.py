import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from tkinter import filedialog
from tkinter import Tk
import os
import re

if __name__ == "__main__":
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a file dialog
    file_path = filedialog.askopenfilename(filetypes=[("MAT files", "*.mat")])

    # Get the directory path
    directory_path = os.path.dirname(file_path)

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

    # Dynamically determine the number of channels
    total_channels = data.shape[0]
    print(f"Total number of channels: {total_channels}")

    # Create frequency array for x-axis, considering sampling frequency
    sampling_frequency = 2000  # Hz
    frequencies = np.fft.fftfreq(data.shape[1], d=1 / sampling_frequency)

    # Number of channels to plot at a time
    channels_per_plot = 8

    for start_channel in range(0, total_channels, channels_per_plot):
        fig, axs = plt.subplots(
            channels_per_plot, 1, sharex=True, figsize=(10, 2 * channels_per_plot)
        )
        fig.suptitle(
            f"{participant_type} - {yoga_position}", fontsize=14, weight="bold"
        )

        # Plot the magnitude of the Fourier transform in separate subplots
        for idx, channel_num in enumerate(
            range(start_channel, min(start_channel + channels_per_plot, total_channels))
        ):
            spectrum = np.abs(np.fft.fft(data[channel_num, :]))
            axs[idx].plot(frequencies, spectrum)
            axs[idx].set_title(f"Channel {channel_num + 1}")
            axs[idx].set_ylabel("Magnitude")
            axs[idx].set_xlim(
                [0, sampling_frequency / 2]
            )  # Only show positive frequencies

            # Adding vertical lines at 20Hz and 450Hz
            axs[idx].axvline(20, color="r", linestyle="--", alpha=0.6)
            axs[idx].axvline(450, color="r", linestyle="--", alpha=0.6)

        axs[-1].set_xlabel("Frequency (Hz)")

        # Show the plot
        plt.tight_layout()
        plt.show()
