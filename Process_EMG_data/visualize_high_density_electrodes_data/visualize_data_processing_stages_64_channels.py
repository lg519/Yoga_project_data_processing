import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from tkinter import filedialog
from tkinter import Tk
import os
import re
import glob
import sys

print(sys.path)

from Process_EMG_data.helpers.filtering import (
    butter_bandpass_filter,
    notch_mains_interference,
)
from Process_EMG_data.helpers.rectify_signal import rectify_signal
from Process_EMG_data.helpers.amplifier_config import (
    highcut,
    lowcut,
    sampling_frequency,
)
from Process_EMG_data.helpers.apply_processing_pipeline import extract_envelope
import gc  # import garbage collector


def plot_and_save(
    data,
    sampling_frequency,
    folder,
    filename_prefix,
    title_prefix,
    start_channel,
    rep_number=None,
):
    total_channels = data.shape[0]
    channels_per_plot = 8

    fig, axs = plt.subplots(
        channels_per_plot, 1, sharex=True, figsize=(10, 2 * channels_per_plot)
    )
    fig.suptitle(f"{title_prefix} - {filename_prefix}", fontsize=14, weight="bold")

    for idx, channel_num in enumerate(
        range(start_channel, min(start_channel + channels_per_plot, total_channels))
    ):
        channel_data = data[channel_num, :]
        time = np.linspace(0, len(channel_data) / sampling_frequency, len(channel_data))
        axs[idx].plot(time, channel_data)
        axs[idx].set_title(f"Channel {channel_num + 1}")
        axs[idx].set_ylabel("Amplitude")

    axs[-1].set_xlabel("Time (s)")
    output_path = os.path.join(folder, f"{filename_prefix}_channel_{start_channel}.png")
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    directory_path = filedialog.askdirectory(
        title="Select directory containing .mat files"
    )

    num_files_to_plot = int(input("Enter the number of files to plot: "))
    file_start_index = int(input("Enter the starting file index (0-based index): "))

    stages_folder = os.path.join(directory_path, "data_processing_stages")
    raw_folder = os.path.join(stages_folder, "raw_signal")
    filtered_folder = os.path.join(stages_folder, "filtered_signal")
    envelope_folder = os.path.join(stages_folder, "envelope_signal")

    for folder in [stages_folder, raw_folder, filtered_folder, envelope_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    mat_files = sorted(glob.glob(os.path.join(directory_path, "*.mat")))

    for file_index in range(file_start_index, file_start_index + num_files_to_plot):
        if file_index >= len(mat_files):
            break

        file_path = mat_files[file_index]
        filename = os.path.splitext(os.path.basename(file_path))[0]
        date_match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
        rep_match = re.search(r"_rep(\d+)_", filename)

        if date_match:
            parts = filename.split(date_match.group())
            participant_type = parts[0].split("_")[0]
            yoga_position = "_".join(parts[0].split("_")[1:]).rstrip("_")
        else:
            print(f"Could not find a date in the filename {filename}.")
            continue

        rep_number = int(rep_match.group(1)) if rep_match else None

        mat = loadmat(file_path)
        raw_data = mat["data"]
        del mat

        # Filter the raw data
        filtered_data = butter_bandpass_filter(
            raw_data, lowcut, highcut, sampling_frequency
        )
        filtered_data = notch_mains_interference(
            filtered_data, mains_freq=50, sampling_frequency=sampling_frequency
        )

        # Extract the envelope of the filtered data
        envelope_data = extract_envelope(raw_data, sampling_frequency)

        channels_per_plot = 8

        for start_channel in range(0, 64, channels_per_plot):
            # Plot and Save Raw Data
            plot_and_save(
                raw_data,
                sampling_frequency,
                raw_folder,
                filename,
                participant_type + " - " + yoga_position + " - Raw Data",
                start_channel,
                rep_number,
            )

            # Plot and Save Filtered Data
            plot_and_save(
                filtered_data,
                sampling_frequency,
                filtered_folder,
                filename,
                participant_type + " - " + yoga_position + " - Filtered Data",
                start_channel,
                rep_number,
            )

            # Plot and Save Envelope Data
            plot_and_save(
                envelope_data,
                sampling_frequency,
                envelope_folder,
                filename,
                participant_type + " - " + yoga_position + " - Envelope Data",
                start_channel,
                rep_number,
            )

        del raw_data, filtered_data, envelope_data
        gc.collect()
