from tkinter import Tk, filedialog
from collections import defaultdict
from scipy.io import loadmat
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name
from amplifier_config import sampling_frequency, get_channel_names
from apply_processing_pipeline import apply_processing_pipeline
from mvc_processing import calculate_mvc_for_each_channel
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from muscle_activations_per_exercise_different_reps import (
    plot_muscle_activation_per_exercise,
)


# New function to merge data from same filenames in both directories
def merge_data_from_directories(filename, dir1, dir2):
    file1_path = os.path.join(dir1, filename)
    file2_path = os.path.join(dir2, filename)

    data1 = loadmat(file1_path)["data"]
    data2 = loadmat(file2_path)["data"]

    return np.concatenate(
        (data1, data2), axis=1
    )  # Assuming data arrays are 2D and merging along columns


def compute_exercise_activations(
    filenames, channel_indices_1, channel_indices_2, mvc_values_1, mvc_values_2
):
    activations_per_exercise = defaultdict(
        lambda: [list() for _ in channel_indices_1 + channel_indices_2]
    )

    for filename in filenames:
        mat_file = loadmat(filename)
        data = mat_file["data"]
        exercise_name = get_exercise_name(os.path.basename(filename))

        # Process data for directory_path_1
        for channel_index in channel_indices_1:
            mvc_value = mvc_values_1[channel_index]
            processed_data = apply_processing_pipeline(
                data[channel_index, :], sampling_frequency, mvc_value
            )
            activations_per_exercise[exercise_name][channel_index].append(
                processed_data
            )

        # Process data for directory_path_2
        for channel_index in channel_indices_2:
            mvc_value = mvc_values_2[channel_index]
            processed_data = apply_processing_pipeline(
                data[channel_index + len(channel_indices_1), :],
                sampling_frequency,
                mvc_value,
            )
            activations_per_exercise[exercise_name][
                channel_index + len(channel_indices_1)
            ].append(processed_data)

    return activations_per_exercise


if __name__ == "__main__":
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a directory dialog for two folders
    directory_path_1 = filedialog.askdirectory(
        title="Select the first directory with exercise data"
    )
    directory_path_2 = filedialog.askdirectory(
        title="Select the second directory with exercise data"
    )

    # Calculate MVC values and filenames for both directories
    mvc_values_1, max_mvc_filenames_1 = calculate_mvc_for_each_channel(directory_path_1)
    mvc_values_2, max_mvc_filenames_2 = calculate_mvc_for_each_channel(directory_path_2)
    # Merge MVC values from both directories
    merged_mvc_values = np.concatenate((mvc_values_1, mvc_values_2))
    print(f"mvc_values_1: {mvc_values_1}")
    print(f"mvc_values_2: {mvc_values_2}")
    print(f"merged_mvc_values: {merged_mvc_values}")

    # Get channel names from both directories and merge them
    channel_names_1 = get_channel_names(directory_path_1)
    channel_names_2 = get_channel_names(directory_path_2)
    merged_channel_names = channel_names_1 + channel_names_2

    # Print for sanity checks
    print(f"Channel names from directory 1: {channel_names_1}")
    print(f"Channel names from directory 2: {channel_names_2}")
    print(f"Merged channel names: {merged_channel_names}")

    # Merge data from same filenames in both directories
    merged_data_dict = {}
    for filename in get_mat_filenames(
        directory_path_1
    ):  # assuming filenames are the same in both directories
        merged_data = merge_data_from_directories(
            filename, directory_path_1, directory_path_2
        )
        merged_data_dict[filename] = merged_data

    # Print total number of merged files
    print(f"Total number of merged files: {len(merged_data_dict)}")

    # Hardcoded channels
    # selected_channels = [
    #     0,
    #     1,
    #     2,
    #     3,
    #     4,
    #     5,
    #     10,
    #     11,
    # ]  # Replace with your desired channel indices

    selected_channels_1 = [0, 1, 2, 3, 4, 5]
    selected_channels_2 = [4, 5]

    # Compute activations for the merged data
    activations_per_exercise = compute_exercise_activations(
        list(merged_data_dict.keys()),
        selected_channels_1,
        selected_channels_2,
        mvc_values_1,
        mvc_values_2,
    )

    # Extract participant type (from the first filename as an example)
    participant_type = get_partecipant_type(list(merged_data_dict.keys())[0])

    # Plot for each exercise
    for exercise_name, activations in activations_per_exercise.items():
        # Merge MVC filenames from both directories
        merged_mvc_filenames = max_mvc_filenames_1 + max_mvc_filenames_2

        # Call the plotting function
        plot_muscle_activation_per_exercise(
            activations,
            merged_channel_names,
            exercise_name,
            participant_type,
            merged_mvc_filenames,
        )
