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

    # Open a directory dialog
    directory_path = filedialog.askdirectory(title="Select a Directory")

    # Get all the .mat files in the chosen directory
    file_paths = [
        os.path.join(directory_path, f)
        for f in os.listdir(directory_path)
        if f.endswith(".mat")
    ]

    # Get the number of files the user wants to plot
    num_files_to_plot = int(input("Enter the number of files you want to plot: "))

    # Ensure the user doesn't request more files than selected
    # num_files_to_plot = min(num_files_to_plot, len(file_paths))

    # Get the starting channel index
    start_channel = 0
    file_start_index = int(input("Enter the starting file index (0-based index): "))

    for file_path in file_paths[
        file_start_index : num_files_to_plot + file_start_index
    ]:
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
        total_channels = 64
        print(f"Total number of channels: {total_channels}")

        # Create frequency array for x-axis, considering sampling frequency
        sampling_frequency = 2000  # Hz
        frequencies = np.fft.fftfreq(data.shape[1], d=1 / sampling_frequency)

        # Number of channels to plot at a time
        channels_per_plot = 8

        save_dir = os.path.join(
            directory_path, "data_processing_stages", "FFT_raw_signal"
        )
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for channel_group_start in range(
            start_channel, total_channels, channels_per_plot
        ):
            fig, axs = plt.subplots(
                channels_per_plot, 1, sharex=True, figsize=(10, 2 * channels_per_plot)
            )
            fig.suptitle(
                f"{participant_type} - {yoga_position}", fontsize=14, weight="bold"
            )

            # Plot the magnitude of the Fourier transform in separate subplots
            for idx, channel_num in enumerate(
                range(
                    channel_group_start,
                    min(channel_group_start + channels_per_plot, total_channels),
                )
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
            # Save the figure to the directory
            plt.savefig(
                os.path.join(
                    save_dir,
                    f"{participant_type}_{yoga_position}_channels_{channel_group_start+1}_to_{min(channel_group_start + channels_per_plot, total_channels)}.png",
                )
            )

            # Close the figure
            plt.close()
