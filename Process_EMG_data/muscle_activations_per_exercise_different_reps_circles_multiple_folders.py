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
):
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection="polar")

    num_reps = len(activations[0])
    colors = plt.cm.tab10(np.linspace(0, 1, num_reps))

    mean_activations = [np.mean([np.mean(rep) for rep in reps]) for reps in activations]

    theta = np.linspace(0.0, 2 * np.pi, len(channel_names), endpoint=False)

    ax.plot(
        np.concatenate([theta, [theta[0]]]),
        mean_activations + [mean_activations[0]],
        linestyle="--",
        color="black",
        label="Mean Activation",
        alpha=0.7,
    )

    for rep_index in range(num_reps):
        activations_for_rep = [
            np.mean(activations[channel][rep_index])
            if len(activations[channel]) > rep_index
            else 0
            for channel in range(len(channel_names))
        ]

        ax.plot(
            np.concatenate([theta, [theta[0]]]),
            activations_for_rep + [activations_for_rep[0]],
            marker="o",
            color=colors[rep_index],
            label=f"Rep {rep_index + 1}",
        )

    font_properties = {"fontsize": 12, "fontweight": "bold"}
    channel_names = [
        name.replace(" (", "\n(") if "(" in name else name for name in channel_names
    ]

    ax.set_xticks(theta)
    ax.set_xticklabels(channel_names, **font_properties)
    ax.set_title(
        f"{participant_type} - {exercise_name}", va="bottom", **font_properties
    )
    ax.legend(loc="upper right")

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

    overall_activations_per_exercise = defaultdict(list)

    for directory_path in directory_paths:
        mvc_values, max_mvc_filenames = calculate_mvc_for_each_channel(directory_path)
        channel_names = get_channel_names(directory_path)
        filenames = get_mat_filenames(directory_path)

        activations_per_exercise = compute_exercise_activations(
            filenames, range(len(channel_names)), mvc_values
        )

        # Merging activations
        overall_activations_per_exercise = merge_activations(
            overall_activations_per_exercise, activations_per_exercise
        )

    # Assuming channel names and sorting are consistent across all directories:
    sorted_indices = np.argsort(channel_names)
    channel_names = [channel_names[i] for i in sorted_indices]

    for exercise_name, activations in overall_activations_per_exercise.items():
        overall_activations_per_exercise[exercise_name] = [
            activations[i] for i in sorted_indices
        ]

    save_directory = os.path.join(
        directory_paths[0], "figures_muscle_activation_per_exercise_circles"
    )  # Using the first directory as the save path
    os.makedirs(save_directory, exist_ok=True)

    # We're only plotting the mapping table for the first directory for now.
    # If you'd like it for each directory, you'd need a loop around this.
    plot_mvc_mapping_table(
        channel_names,
        max_mvc_filenames,
        mvc_values,
        get_partecipant_type(filenames[0]),
        save_directory,
    )

    for exercise_name, activations in overall_activations_per_exercise.items():
        plot_muscle_activation_per_exercise_different_reps(
            activations,
            channel_names,
            exercise_name,
            "Overall",  # We use 'Overall' as a generic participant_type since we're combining multiple directories
            save_directory,
        )
