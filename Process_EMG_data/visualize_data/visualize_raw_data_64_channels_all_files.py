import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from tkinter import filedialog
from tkinter import Tk
import os
import re
import glob

if __name__ == "__main__":
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a directory dialog
    directory_path = filedialog.askdirectory(
        title="Select directory containing .mat files"
    )

    # Ensure the raw_data folder exists in the selected directory
    output_folder = os.path.join(directory_path, "raw_data")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Fetch all .mat files in the selected directory and sort them
    mat_files = sorted(glob.glob(os.path.join(directory_path, "*.mat")))

    for file_path in mat_files:
        # Get the filename without the extension
        filename = os.path.splitext(os.path.basename(file_path))[0]

        # Use regex to extract date pattern "DD_MM_YYYY" and rep number
        date_match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
        rep_match = re.search(r"_rep(\d+)_", filename)

        if date_match:
            # Split the filename into parts before and after the date
            parts = filename.split(date_match.group())
            participant_type = parts[0].split("_")[0]
            yoga_position = "_".join(parts[0].split("_")[1:]).rstrip("_")
        else:
            print(f"Could not find a date in the filename {filename}.")
            continue

        rep_number = int(rep_match.group(1)) if rep_match else None

        # Load the data from the .mat file
        mat = loadmat(file_path)
        data = mat["data"]

        # Dynamically determine the number of channels
        total_channels = data.shape[0]

        # Create a time array for x-axis, considering sampling frequency
        sampling_frequency = 2000  # Hz
        time = np.linspace(0, data.shape[1] / sampling_frequency, data.shape[1])

        # Number of channels to plot at a time
        channels_per_plot = 8

        for start_channel in range(0, total_channels, channels_per_plot):
            fig, axs = plt.subplots(
                channels_per_plot, 1, sharex=True, figsize=(10, 2 * channels_per_plot)
            )
            title = f"{participant_type} - {yoga_position}"
            if rep_number:
                title += f" - Rep {rep_number}"
            fig.suptitle(title, fontsize=14, weight="bold")

            # Plot the raw data in separate subplots
            for idx, channel_num in enumerate(
                range(
                    start_channel,
                    min(start_channel + channels_per_plot, total_channels),
                )
            ):
                axs[idx].plot(time, data[channel_num, :])
                axs[idx].set_title(f"Channel {channel_num + 1}")
                axs[idx].set_ylabel("Amplitude")

            axs[-1].set_xlabel("Time (s)")

            # Save the figure to the raw_data folder
            output_path = os.path.join(
                output_folder, f"{filename}_channel_{start_channel}.png"
            )
            plt.savefig(output_path)
            plt.close()  # Close the figure to free memory
