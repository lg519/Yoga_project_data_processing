from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mvc_processing import calculate_mvc_for_each_channel
from apply_processing_pipeline import apply_processing_pipeline
from amplifier_config import sampling_frequency, get_channel_names
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


def plot_muscle_activation_per_channel(
    activation_means,
    exercise_names,
    channel_name,
    participant_type,
    max_mvc_filename,
    asymmetrical_exercises=["side_angle", "side_plank", "warrior2"],
):
    # Filter out exercise names containing "MVC" and their corresponding activations
    exercise_names_filtered, activation_means_filtered = zip(
        *[
            (name, activation)
            for name, activation in zip(exercise_names, activation_means)
            if "MVC" not in name
        ]
    )

    # Sort the data by exercise names
    sort_indices = np.argsort(exercise_names_filtered)
    sorted_exercise_names = np.array(exercise_names_filtered)[sort_indices]
    sorted_activation_means = np.array(activation_means_filtered)[sort_indices]

    # Create color list based on exercise name
    color_list = []
    for name in sorted_exercise_names:
        if (
            "left" in name.lower()
            or "right" in name.lower()
            or name in asymmetrical_exercises
        ):
            color_list.append("r")  # Red for asymmetrical
        else:
            color_list.append("b")  # Blue for symmetrical

    # Generate a bar graph of the average muscle activation
    bars = plt.bar(
        np.arange(len(sorted_exercise_names)), sorted_activation_means, color=color_list
    )

    # Create a legend
    symmetrical_patch = mpatches.Patch(color="blue", label="Symmetrical")
    asymmetrical_patch = mpatches.Patch(color="red", label="Asymmetrical")
    plt.legend(handles=[symmetrical_patch, asymmetrical_patch], fontsize=10)

    # Label the bars with the exercise names
    plt.xticks(
        np.arange(len(sorted_exercise_names)),
        sorted_exercise_names,
        rotation="vertical",
        fontsize=12,  # Increase the font size for x-axis tick labels
        fontweight="bold",  # Make the text bold
    )
    plt.yticks(fontsize=10)  # Increase the font size for y-axis tick labels

    plt.ylabel(
        "Muscle average activation (MVC fraction)", fontsize=12, fontweight="bold"
    )  # Increase the font size for y-axis label
    plt.title(
        f"{participant_type} - {channel_name}",
        fontsize=12,
        fontweight="bold",
    )  # Increase the font size for title

    # Add the max MVC filename to the plot
    plt.text(
        0.05,
        0.95,
        f"MVC used for Normalization: {max_mvc_filename}",
        transform=plt.gca().transAxes,
        fontsize=12,  # Increase the font size for x-axis tick labels
        # make the text italicized
        style="italic",
    )

    # Show the plot
    # plt.tight_layout()
    plt.show()


def compute_exercise_mean_activations(filenames, channel_indices, mvc_values):
    activation_means_per_exercise = defaultdict(lambda: [0] * len(channel_indices))

    for filename in filenames:
        mat_file = loadmat(filename)
        data = mat_file["data"]
        exercise_name = get_exercise_name(os.path.basename(filename))

        for channel_index in channel_indices:
            processed_data = apply_processing_pipeline(
                data[channel_index, :], sampling_frequency, mvc_values[channel_index]
            )
            mean_activation = np.mean(processed_data)
            activation_means_per_exercise[exercise_name][
                channel_index
            ] = mean_activation

    return activation_means_per_exercise


# New function to merge data from same filenames in both directories
def merge_data_from_directories(filename, dir1, dir2):
    file1_path = os.path.join(dir1, filename)
    file2_path = os.path.join(dir2, filename)

    data1 = loadmat(file1_path)["data"]
    data2 = loadmat(file2_path)["data"]

    return np.concatenate(
        (data1, data2), axis=1
    )  # Assuming data arrays are 2D and merging along columns


def compute_channel_mean_activations_from_merged_data(
    merged_data_dict, channel_index, mvc_values_1, mvc_values_2
):
    activation_means_dict = defaultdict(list)
    max_mvc_filename = None

    for filename, data in merged_data_dict.items():
        # Determine which MVC values to use based on channel index
        if channel_index < len(mvc_values_1):
            mvc_value = mvc_values_1[channel_index]
            max_mvc_filename = max_mvc_filenames_1[channel_index]
        else:
            mvc_value = mvc_values_2[channel_index - len(mvc_values_1)]
            max_mvc_filename = max_mvc_filenames_2[channel_index - len(mvc_values_1)]

        # Process the merged data
        processed_data = apply_processing_pipeline(
            data[channel_index, :], sampling_frequency, mvc_value
        )

        mean_activation = np.mean(processed_data)
        exercise_name = get_exercise_name(filename)
        activation_means_dict[exercise_name].append(mean_activation)

    return activation_means_dict, max_mvc_filename


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
    selected_channels = [
        0,
        1,
        2,
        3,
        4,
        5,
        10,
        11,
    ]  # Replace with your desired channel indices

    # Extract participant type (from the first filename as an example)
    participant_type = get_partecipant_type(list(merged_data_dict.keys())[0])

    # For each channel in the selected channels, compute and plot the mean activation
    for channel_index in selected_channels:
        channel_name = merged_channel_names[channel_index]

        print(f"Processing data for channel: {channel_name}")

        (
            activation_means_dict,
            max_mvc_filename,
        ) = compute_channel_mean_activations_from_merged_data(
            merged_data_dict, channel_index, mvc_values_1, mvc_values_2
        )

        # Compute the mean of means for each exercise
        exercise_names = list(activation_means_dict.keys())
        activation_means = [np.mean(means) for means in activation_means_dict.values()]

        # Plot the data for the current channel
        plot_muscle_activation_per_channel(
            activation_means,
            exercise_names,
            channel_name,
            participant_type,
            max_mvc_filename,
        )
