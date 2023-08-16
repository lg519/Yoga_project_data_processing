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
import numpy as np
from utilis import get_exercise_name
from amplifier_config import get_channel_names


def choose_mvc_files():
    """
    Open a file dialog to choose the MVC files, load the selected files, and return the loaded data.

    Returns:
        datas (list of np.array): The loaded MVC data for each file.
    """
    root = Tk()
    root.withdraw()  # Hide the main window
    filenames = filedialog.askopenfilenames(title="Select MVC Files")
    root.destroy()  # Destroy the main window

    datas = []
    for filename in filenames:
        # Load the data from the .mat file
        mat = loadmat(filename)

        # Assuming 'data' is the key for the data you want
        data = mat["data"]

        datas.append(data)

    return datas


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


def calculate_mvc(filtered_mvc_data, sampling_frequency, window_duration=1):
    window_size = int(window_duration * sampling_frequency)
    max_mean_value = float("-inf")
    mvc_value = 0

    for start_index in range(0, len(filtered_mvc_data) - window_size):
        end_index = start_index + window_size
        windowed_data = filtered_mvc_data[start_index:end_index]
        mean_value = np.mean(windowed_data)

        if mean_value > max_mean_value:
            max_mean_value = mean_value
            mvc_value = mean_value

    return mvc_value


# TODO: remove this function to refactor the code
def trim_data_for_mvc(data, sampling_frequency):
    # Calculate the number of samples corresponding to one second
    samples_to_remove = int(sampling_frequency)

    return data[:, samples_to_remove:-samples_to_remove]


def calculate_mvc_for_each_channel(directory_path):
    mvc_datas, mvc_filenames = get_mvc_files(directory_path)
    channel_names = get_channel_names(directory_path)
    num_channels = len(channel_names)

    max_mvc_values = []
    mvc_exercise_names_for_channels = []

    for i in range(num_channels):
        mvc_values = []
        max_mvc_value = float("-inf")
        max_mvc_value_index = 0
        for j, mvc_data in enumerate(mvc_datas):
            # TODO: Refactor this code to make it only one function call
            trimmed_mvc_data = trim_data_for_mvc(mvc_data, sampling_frequency)
            filtered_mvc_data = butter_bandpass_filter(
                trimmed_mvc_data[i, :], lowcut, highcut, sampling_frequency
            )
            rectified_mvc_data = rectify_signal(filtered_mvc_data)
            mvc_envelope = butter_lowpass_filter(
                rectified_mvc_data, cutoff=5, sampling_frequency=sampling_frequency
            )
            mvc_value = calculate_mvc(mvc_envelope, sampling_frequency)
            mvc_values.append(mvc_value)
            if mvc_value > max_mvc_value:
                max_mvc_value = mvc_value
                max_mvc_value_index = j

        max_mvc_values.append(max(mvc_values))
        mvc_exercise_names_for_channels.append(
            get_exercise_name(mvc_filenames[max_mvc_value_index])
        )

    return np.array(max_mvc_values), mvc_exercise_names_for_channels


if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the main window
    directory_path = filedialog.askdirectory(title="Select MVC Files directory")

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
            filtered_mvc_data = butter_bandpass_filter(
                mvc_data[i, :], lowcut, highcut, sampling_frequency
            )
            rectified_mvc_data = rectify_signal(filtered_mvc_data)
            mvc_envelope = butter_lowpass_filter(
                rectified_mvc_data, cutoff=5, sampling_frequency=sampling_frequency
            )
            mvc_value = calculate_mvc(mvc_envelope, sampling_frequency)
            print(f"  File {j+1} ({mvc_filenames[j]}): {mvc_value}")
