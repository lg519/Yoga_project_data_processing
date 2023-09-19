from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt

from Process_EMG_data.helpers.mvc_processing import calculate_mvc_for_each_channel
from Process_EMG_data.helpers.apply_processing_pipeline import normalize_signal
from Process_EMG_data.helpers.amplifier_config import (
    sampling_frequency,
)
from Process_EMG_data.helpers.utilis import (
    get_mat_filenames,
    get_partecipant_type,
    get_exercise_name,
    get_channel_names,
)


def plot_mean_muscle_activation_per_exercise(
    activation_means,
    channel_names,
    exercise_name,
    participant_type,
    max_mvc_filenames,
):
    """
    Plot the mean muscle activation for each channel for a given exercise.

    Args:
        activation_means (list): Mean activation values for each channel.
        channel_names (list): Names of the channels.
        exercise_name (str): Name of the exercise.
        participant_type (str): Type of the participant.
        max_mvc_filenames (list): Filenames used for max MVC normalization.

    Returns:
        None
    """
    # Create a bar graph of the average muscle activation for each channel
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(channel_names)), activation_means)

    # Set font properties
    font_properties = {"fontsize": 12, "fontweight": "bold"}

    plt.xticks(
        range(len(channel_names)), channel_names, rotation="vertical", **font_properties
    )
    plt.ylabel("Muscle average activation (MVC fraction)", **font_properties)
    plt.title(f"{participant_type} - {exercise_name}", **font_properties)

    # # Applying bold font to the bar values
    # for bar in bars:
    #     height = bar.get_height()
    #     plt.text(
    #         bar.get_x() + bar.get_width() / 2.0,
    #         height,
    #         f"{height:.2f}",
    #         ha="center",
    #         va="bottom",
    #         **font_properties,
    #     )

    plt.tight_layout()
    plt.show()

    # Create a separate figure for the table
    fig, ax = plt.subplots(figsize=(8, 6))  # Adjust the figure size if needed

    # Remove paths from filenames for brevity in the table
    stripped_mvc_filenames = [os.path.basename(f) for f in max_mvc_filenames]
    rows = list(zip(channel_names, stripped_mvc_filenames))
    table_data = [["Channel Name", "MVC File"]] + rows

    ax.axis("off")  # This hides the axis
    ax.table(cellText=table_data, cellLoc="center", loc="center", colWidths=[0.4, 0.6])

    plt.title(
        f"{participant_type} - MVC File Mapping for {exercise_name}", **font_properties
    )
    plt.show()


def compute_exercise_mean_activations(filenames, channel_indices, mvc_values):
    """
    Compute mean activations for each channel based on a list of exercises.

    Args:
        filenames (list): List of filenames containing the EMG data.
        channel_indices (list): Indices of the channels.
        mvc_values (list): List of MVC values for normalization.

    Returns:
        dict: Dictionary mapping exercise names to their respective mean activations for each channel.
    """
    activation_means_per_exercise = defaultdict(lambda: [0] * len(channel_indices))

    for filename in filenames:
        mat_file = loadmat(filename)
        data = mat_file["data"]

        exercise_name = get_exercise_name(os.path.basename(filename))

        for channel_index in channel_indices:
            processed_data = normalize_signal(
                data[channel_index, :],
                sampling_frequency,
                mvc_values[channel_index],
            )
            mean_activation = np.mean(processed_data)
            activation_means_per_exercise[exercise_name][
                channel_index
            ] = mean_activation

    return activation_means_per_exercise


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    directory_path = filedialog.askdirectory(
        title="Select directory with exercise data"
    )

    mvc_values, max_mvc_filenames = calculate_mvc_for_each_channel(directory_path)
    channel_names = get_channel_names(directory_path)
    filenames = get_mat_filenames(directory_path)
    participant_type = get_partecipant_type(filenames[0])

    activation_means_per_exercise = compute_exercise_mean_activations(
        filenames, range(len(channel_names)), mvc_values
    )

    for exercise_name, activation_means in activation_means_per_exercise.items():
        plot_mean_muscle_activation_per_exercise(
            activation_means,
            channel_names,
            exercise_name,
            participant_type,
            max_mvc_filenames,
        )
