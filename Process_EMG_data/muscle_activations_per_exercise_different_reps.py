from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt

from mvc_processing import calculate_mvc_for_each_channel
from apply_processing_pipeline import apply_processing_pipeline
from amplifier_config import sampling_frequency, get_channel_names
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


def plot_muscle_activation_per_exercise(
    activations,
    channel_names,
    exercise_name,
    participant_type,
    max_mvc_filenames,
):
    plt.figure(figsize=(10, 6))

    # Get the number of reps for the first channel (assuming consistent repetitions across channels)
    num_reps = len(activations[0])
    colors = plt.cm.viridis(np.linspace(0, 1, num_reps))

    # Getting bar positions
    positions = np.arange(len(channel_names))
    width = 0.2  # Adjust as necessary if you have more repetitions

    for rep_index in range(num_reps):
        activations_for_rep = [
            np.mean(activations[channel][rep_index])
            if len(activations[channel]) > rep_index
            else 0
            for channel in range(len(channel_names))
        ]
        plt.bar(
            positions + rep_index * width,
            activations_for_rep,
            color=colors[rep_index],
            alpha=0.7,
            width=width,
            label=f"Rep {rep_index + 1}",
        )

    font_properties = {"fontsize": 12, "fontweight": "bold"}
    plt.xticks(positions + width, channel_names, rotation="vertical", **font_properties)
    plt.ylabel("Muscle average activation (MVC fraction)", **font_properties)
    plt.title(f"{participant_type} - {exercise_name}", **font_properties)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Creating the table
    fig, ax = plt.subplots(figsize=(8, 6))
    stripped_mvc_filenames = [os.path.basename(f) for f in max_mvc_filenames]
    rows = list(zip(channel_names, stripped_mvc_filenames))
    table_data = [["Channel Name", "MVC File"]] + rows

    ax.axis("off")
    ax.table(cellText=table_data, cellLoc="center", loc="center", colWidths=[0.4, 0.6])
    plt.title(
        f"{participant_type} - MVC File Mapping for {exercise_name}", **font_properties
    )
    plt.show()


def compute_exercise_activations(filenames, channel_indices, mvc_values):
    activations_per_exercise = defaultdict(lambda: [list() for _ in channel_indices])

    for filename in filenames:
        mat_file = loadmat(filename)
        data = mat_file["data"]
        exercise_name = get_exercise_name(os.path.basename(filename))

        for channel_index in channel_indices:
            processed_data = apply_processing_pipeline(
                data[channel_index, :],
                sampling_frequency,
                mvc_values[channel_index],
            )
            activations_per_exercise[exercise_name][channel_index].append(
                processed_data
            )

    return activations_per_exercise


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

    activations_per_exercise = compute_exercise_activations(
        filenames, range(len(channel_names)), mvc_values
    )

    for exercise_name, activations in activations_per_exercise.items():
        plot_muscle_activation_per_exercise(
            activations,
            channel_names,
            exercise_name,
            participant_type,
            max_mvc_filenames,
        )
