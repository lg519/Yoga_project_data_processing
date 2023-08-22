from tkinter import Tk
from filtering import butter_bandpass_filter, butter_lowpass_filter
import numpy as np
from scipy.io import loadmat
from tkinter import filedialog
from rectify_signal import rectify_signal
from amplifier_config import sampling_frequency, lowcut, highcut, get_channel_names
import matplotlib.pyplot as plt
import fnmatch
import os
from utilis import get_exercise_name, trim_data


def process_mvc_data_for_channel(channel_data):
    """Process raw MVC data for a specific channel and return the computed MVC value."""
    # Trim operation
    trimmed_data = trim_data(channel_data, sampling_frequency)

    # Filter the data with a bandpass filter
    filtered_data = butter_bandpass_filter(
        trimmed_data, lowcut, highcut, sampling_frequency
    )

    # Rectify the signal
    rectified_data = rectify_signal(filtered_data)

    # Get the envelope of the rectified signal using a lowpass filter
    mvc_envelope = butter_lowpass_filter(
        rectified_data, cutoff=5, sampling_frequency=sampling_frequency
    )

    # Calculate the MVC value for the channel
    return calculate_mvc_for_channel(mvc_envelope, sampling_frequency)


def get_mvc_files(directory_path):
    mvc_files = []
    mvc_filenames = []
    for filename in os.listdir(directory_path):
        if fnmatch.fnmatch(filename, "*MVC*.mat"):
            filepath = os.path.join(directory_path, filename)
            mat = loadmat(filepath)
            data = mat["data"]
            mvc_files.append(data)
            mvc_filenames.append(filename)
    return mvc_files, mvc_filenames


def calculate_mvc_for_channel(data, sampling_frequency, window_duration=1):
    window_size = int(window_duration * sampling_frequency)
    max_mean_value = float("-inf")

    for start_index in range(0, len(data) - window_size):
        end_index = start_index + window_size
        windowed_data = data[start_index:end_index]
        mean_value = np.mean(windowed_data)
        if mean_value > max_mean_value:
            max_mean_value = mean_value
    return max_mean_value


def calculate_mvc_for_each_channel(directory_path):
    mvc_datas, mvc_filenames = get_mvc_files(directory_path)
    channel_names = get_channel_names(directory_path)

    max_mvc_values = []
    mvc_exercise_names_for_channels = []

    for i, channel_name in enumerate(channel_names):
        max_mvc_value = float("-inf")
        max_mvc_value_index = 0

        for j, mvc_data in enumerate(mvc_datas):
            channel_data = mvc_data[i, :]
            mvc_value = process_mvc_data_for_channel(channel_data)

            if mvc_value > max_mvc_value:
                max_mvc_value = mvc_value
                max_mvc_value_index = j

        max_mvc_values.append(max_mvc_value)
        mvc_exercise_names_for_channels.append(
            get_exercise_name(mvc_filenames[max_mvc_value_index])
        )

    return np.array(max_mvc_values), mvc_exercise_names_for_channels


if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the main window
    directory_path = filedialog.askdirectory(title="Select MVC Files directory")
    root.destroy()

    max_mvc_values, mvc_exercise_names_for_channels = calculate_mvc_for_each_channel(
        directory_path
    )

    channel_names = get_channel_names(directory_path)
    print("Max MVC Values and Filenames for Each Channel:")
    for i, (value, filename) in enumerate(
        zip(max_mvc_values, mvc_exercise_names_for_channels)
    ):
        channel_name = channel_names[i]
        print(f"{channel_name}: Max Value = {value}, Filename = {filename}")

    print("\nAll MVC Values Calculated:")
    mvc_datas, mvc_filenames = get_mvc_files(directory_path)
    for i, channel_name in enumerate(channel_names):
        print(f"{channel_name}:")
        for j, mvc_data in enumerate(mvc_datas):
            channel_data = mvc_data[i, :]
            mvc_value = process_mvc_data_for_channel(channel_data)
            print(f"  File {j+1} ({mvc_filenames[j]}): {mvc_value}")
