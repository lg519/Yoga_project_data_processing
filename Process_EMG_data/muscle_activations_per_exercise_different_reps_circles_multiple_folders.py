from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt

from mvc_processing import calculate_mvc_for_each_channel, plot_mvc_mapping_table
from apply_processing_pipeline import normalize_signal
from amplifier_config import sampling_frequency, get_channel_names
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


def select_multiple_directories(title="Select Directories"):
    directories = []
    while True:
        directory = filedialog.askdirectory(title=title)
        if not directory:  # User either selected 'Cancel' or closed the dialog
            break
        directories.append(directory)
    return directories


def plot_muscle_activation_per_exercise_different_reps(
    activations,
    channel_names,
    exercise_name,
    participant_type,
    save_directory,
    colors_by_directory,
):
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection="polar")

    theta = np.linspace(0.0, 2 * np.pi, len(channel_names), endpoint=False)

    legend_handles = []  # to store legend handles

    # Loop over all directories (i.e., color groups)
    for color, reps_by_color in activations.items():
        num_reps = len(reps_by_color[0])

        for rep_index in range(num_reps):
            activations_for_rep = [
                np.mean(reps_by_color[channel][rep_index])
                if len(reps_by_color[channel]) > rep_index
                else 0
                for channel in range(len(channel_names))
            ]

            (line,) = ax.plot(
                np.concatenate([theta, [theta[0]]]),
                activations_for_rep + [activations_for_rep[0]],
                marker="o",
                color=colors_by_directory[color],
            )

        # Add legend entry for this directory
        legend_handles.append(line)

    font_properties = {"fontsize": 12, "fontweight": "bold"}
    channel_names = [
        name.replace(" (", "\n(") if "(" in name else name for name in channel_names
    ]

    ax.set_xticks(theta)
    ax.set_xticklabels(channel_names, **font_properties)
    ax.set_title(
        f"{participant_type} - {exercise_name}", va="bottom", **font_properties
    )

    # Use just the basename of the directory for legend labels
    directory_labels = [os.path.basename(directory) for directory in activations.keys()]
    ax.legend(
        legend_handles, directory_labels, loc="upper right", bbox_to_anchor=(1.25, 1.0)
    )

    plt.tight_layout()
    plot_filename = os.path.join(
        save_directory, f"{participant_type} - {exercise_name}.png"
    )
    plt.savefig(plot_filename)
    plt.close()


def compute_exercise_activations(filenames, channel_indices, mvc_values):
    activations_per_exercise = defaultdict(lambda: [list() for _ in channel_indices])

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
            activations_per_exercise[exercise_name][channel_index].append(
                processed_data
            )

    return activations_per_exercise


def merge_activations(old_activations, new_activations):
    for exercise, channels in new_activations.items():
        if exercise not in old_activations:
            old_activations[exercise] = channels
        else:
            for i, reps in enumerate(channels):
                old_activations[exercise][i].extend(reps)
    return old_activations


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    directory_paths = select_multiple_directories(
        "Select multiple directories with exercise data"
    )

    # Define a color for each directory
    colors_by_directory = {
        directory: color
        for directory, color in zip(
            directory_paths, plt.cm.tab10(np.linspace(0, 1, len(directory_paths)))
        )
    }

    overall_activations_per_exercise = defaultdict(lambda: defaultdict(list))

    for directory_path in directory_paths:
        mvc_values, max_mvc_filenames = calculate_mvc_for_each_channel(directory_path)
        channel_names = get_channel_names(directory_path)
        filenames = get_mat_filenames(directory_path)

        activations_per_exercise = compute_exercise_activations(
            filenames, range(len(channel_names)), mvc_values
        )
        # Sort channel names and reorder related data
        sorted_indices = np.argsort(channel_names)
        channel_names = [channel_names[i] for i in sorted_indices]
        mvc_values = [mvc_values[i] for i in sorted_indices]
        max_mvc_filenames = [max_mvc_filenames[i] for i in sorted_indices]

        # Sort activations for each exercise according to the sorted channel names
        for exercise_name, activations in activations_per_exercise.items():
            activations_per_exercise[exercise_name] = [
                activations[i] for i in sorted_indices
            ]

        # Merging activations
        for exercise, activations in activations_per_exercise.items():
            overall_activations_per_exercise[exercise][directory_path] = activations

    # Create directory to save images where the script is run
    save_directory = "figures_muscle_activation_per_exercise_circles_overall"
    os.makedirs(save_directory, exist_ok=True)

    for exercise_name, activations in overall_activations_per_exercise.items():
        plot_muscle_activation_per_exercise_different_reps(
            activations,
            channel_names,
            exercise_name,
            "Overall",  # Use 'Overall' as a generic participant_type since combining multiple directories
            save_directory,
            colors_by_directory,
        )
