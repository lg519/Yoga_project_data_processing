import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os
from collections import defaultdict
from mvc_processing import calculate_mvc_for_each_channel
from apply_processing_pipeline import apply_processing_pipeline
from amplifier_config import sampling_frequency, get_channel_names
import matplotlib.patches as mpatches
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


def plot_muscle_activation_comparison(
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
            # if "MVC" not in name
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
    plt.legend(handles=[symmetrical_patch, asymmetrical_patch])

    # Label the bars with the exercise names
    plt.xticks(
        np.arange(len(sorted_exercise_names)),
        sorted_exercise_names,
        rotation="vertical",
    )

    # Set the y-axis label
    plt.ylabel("Muscle average activation (MVC fraction)")

    # Set the title
    plt.title(f"Participant Type: {participant_type}, Channel: {channel_name}")

    # Add the max MVC filename to the plot
    plt.text(
        0.05,
        0.95,
        f"MVC used for Normalization: {max_mvc_filename}",
        transform=plt.gca().transAxes,
    )

    # Show the plot
    plt.tight_layout()
    plt.show()


def compute_channel_mean_activations(filenames, channel_index):
    # Initialize dictionary to store mean muscle activation values per exercise
    activation_means_dict = defaultdict(list)

    for filename in filenames:
        # Load the data from the .mat file
        mat_file = loadmat(filename)

        # Extract the data
        data = mat_file["data"]

        # Process the EMG data
        processed_data = apply_processing_pipeline(
            data[channel_index, :], sampling_frequency, mvc_values[channel_index]
        )
        # TODO: apply windowing method here
        # Compute the mean muscle activation for the selected channel
        mean_activation = np.mean(processed_data)

        # Extract the partecipant type and yoga position from the filename and store for labeling
        filename = os.path.basename(filename)
        exercise_name = get_exercise_name(filename)

        activation_means_dict[exercise_name].append(mean_activation)

    return activation_means_dict


if __name__ == "__main__":
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a directory dialog
    directory_path = filedialog.askdirectory(
        title="Select directory with exercise data"
    )

    # Calculate the MVC value for each channel and get corresponding filenames
    mvc_values, max_mvc_filenames = calculate_mvc_for_each_channel(directory_path)

    # Get channels configuration
    channel_names = get_channel_names(directory_path)

    # Extract .mat filenames
    filenames = get_mat_filenames(directory_path)

    # Extract partecipant type
    participant_type = get_partecipant_type(filenames[0])

    # For each channel, compute the mean activation for each exercise and plot
    for channel_index, channel_name in enumerate(channel_names):
        max_mvc_filename = max_mvc_filenames[channel_index]
        # Compute the mean activation of each exercise for a given channel
        activation_means_dict = compute_channel_mean_activations(
            filenames, channel_index
        )

        # Compute the mean of means for each exercise
        exercise_names = list(activation_means_dict.keys())
        activation_means = [np.mean(means) for means in activation_means_dict.values()]

        # Plot the data for the current channel
        plot_muscle_activation_comparison(
            activation_means,
            exercise_names,
            channel_name,
            participant_type,
            max_mvc_filename,
        )
