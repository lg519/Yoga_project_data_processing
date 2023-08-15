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
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


def plot_muscle_activation_per_exercise(
    activation_means,
    channel_names,
    exercise_name,
    participant_type,
    max_mvc_filename,
):
    # Create a bar graph of the average muscle activation for each channel
    plt.bar(range(len(channel_names)), activation_means)

    # Label the bars with the channel names
    plt.xticks(range(len(channel_names)), channel_names, rotation="vertical")

    plt.ylabel("Muscle average activation (MVC fraction)")
    plt.title(f"{participant_type} - {exercise_name}")

    # Show the plot
    plt.tight_layout()
    plt.show()


def compute_exercise_mean_activations(filenames, channel_indices, mvc_values):
    # Dictionary to store mean muscle activation values per exercise and channel
    activation_means_per_exercise = defaultdict(lambda: [0] * len(channel_indices))

    for filename in filenames:
        # Load the data from the .mat file
        mat_file = loadmat(filename)

        # Extract the data
        data = mat_file["data"]

        # Extract the exercise name from the filename and store for labeling
        exercise_name = get_exercise_name(os.path.basename(filename))

        for channel_index in channel_indices:
            # Process the EMG data for the given channel
            processed_data = apply_processing_pipeline(
                data[channel_index, :], sampling_frequency, mvc_values[channel_index]
            )

            # Compute the mean muscle activation for the selected channel
            mean_activation = np.mean(processed_data)

            activation_means_per_exercise[exercise_name][
                channel_index
            ] = mean_activation

    return activation_means_per_exercise


if __name__ == "__main__":
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a directory dialog
    directory_path = filedialog.askdirectory(
        title="Select directory with exercise data"
    )

    # Calculate the MVC value for each channel
    mvc_values, max_mvc_filenames = calculate_mvc_for_each_channel(directory_path)

    # Get channels configuration
    channel_names = get_channel_names(directory_path)

    # Extract .mat filenames
    filenames = get_mat_filenames(directory_path)

    # Extract partecipant type
    participant_type = get_partecipant_type(filenames[0])

    # Compute the mean activation of each channel for each exercise
    activation_means_per_exercise = compute_exercise_mean_activations(
        filenames, range(len(channel_names)), mvc_values
    )

    # Plot the data for each exercise
    for exercise_name, activation_means in activation_means_per_exercise.items():
        max_mvc_filename = "MAX_MVC_FILE.mat"  # Replace with the correct filename
        plot_muscle_activation_per_exercise(
            activation_means,
            channel_names,
            exercise_name,
            participant_type,
            max_mvc_filename,
        )
