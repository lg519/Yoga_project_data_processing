from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt

from mvc_processing import (
    calculate_mvc_for_each_channel,
    plot_mvc_mapping_table,
    use_automatic,
)
from apply_processing_pipeline import normalize_signal
from amplifier_config import sampling_frequency, get_channel_names
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


def plot_muscle_activation_per_exercise_different_reps(
    activations,
    channel_names,
    exercise_name,
    participant_type,
    save_directory,
):
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection="polar")

    # Checks for empty reps and activations
    for reps, channel in zip(activations, channel_names):
        if len(reps) == 0:
            print(f"Empty reps for Exercise: {exercise_name}, Channel: {channel}")
        for rep_num, rep in enumerate(reps, start=1):
            if len(rep) == 0:
                print(
                    f"Empty rep #{rep_num} in Exercise: {exercise_name}, Channel: {channel}"
                )

    # Get the number of reps for the first channel (assuming consistent repetitions across channels)
    num_reps = len(activations[0])
    colors = plt.cm.tab10(np.linspace(0, 1, num_reps))

    # Calculate mean activations for the entire exercise
    mean_activations = [np.mean([np.mean(rep) for rep in reps]) for reps in activations]

    # Convert channel positions to radians for polar plotting
    theta = np.linspace(0.0, 2 * np.pi, len(channel_names), endpoint=False)

    # Plot average activation with dotted lines
    ax.plot(
        np.concatenate(
            [theta, [theta[0]]]
        ),  # Repeat the first theta to close the circle
        mean_activations
        + [mean_activations[0]],  # Repeat the first value to close the circle
        linestyle="--",
        color="black",  # Black color for clarity
        label="Mean Activation",
        alpha=0.7,
    )

    # Plot lines connecting the mean activation for each repetition across channels
    for rep_index in range(num_reps):
        # Check for empty activation
        for channel in range(len(channel_names)):
            if len(activations[channel]) <= rep_index:
                print(
                    f"Empty activation for Exercise: {exercise_name}, Channel: {channel_names[channel]}, Rep: {rep_index}"
                )

        activations_for_rep = [
            np.mean(activations[channel][rep_index])
            if len(activations[channel]) > rep_index
            else 0
            for channel in range(len(channel_names))
        ]

        ax.plot(
            np.concatenate(
                [theta, [theta[0]]]
            ),  # Repeat the first theta to close the circle
            activations_for_rep
            + [activations_for_rep[0]],  # Repeat the first value to close the circle
            marker="o",
            color=colors[rep_index],
            label=f"Rep {rep_index + 1}",
        )

    font_properties = {"fontsize": 12, "fontweight": "bold"}

    # Split channel names at the first opening bracket for better display
    channel_names = [
        name.replace(" (", "\n(") if "(" in name else name for name in channel_names
    ]

    ax.set_xticks(theta)
    ax.set_xticklabels(channel_names, **font_properties)
    ax.set_title(
        f"{participant_type} - {exercise_name}", va="bottom", **font_properties
    )
    ax.legend(loc="upper right")

    # Save the plot
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


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    directory_path = filedialog.askdirectory(
        title="Select directory with exercise data"
    )

    mvc_values, max_mvc_filenames = calculate_mvc_for_each_channel(
        directory_path, use_automatic
    )
    channel_names = get_channel_names(directory_path)

    filenames = get_mat_filenames(directory_path)
    participant_type = get_partecipant_type(filenames[0])

    activations_per_exercise = compute_exercise_activations(
        filenames, range(len(channel_names)), mvc_values
    )

    # Sort channel names and reorder related data right before plotting
    sorted_indices = np.argsort(channel_names)
    channel_names = [channel_names[i] for i in sorted_indices]
    mvc_values = [mvc_values[i] for i in sorted_indices]
    max_mvc_filenames = [max_mvc_filenames[i] for i in sorted_indices]

    # Sort activations for each exercise according to the sorted channel names
    for exercise_name, activations in activations_per_exercise.items():
        activations_per_exercise[exercise_name] = [
            activations[i] for i in sorted_indices
        ]

    # After selecting the directory_path and before plotting:
    save_suffix = "_automatic" if use_automatic else "_fixed"
    save_directory = os.path.join(
        directory_path, f"figures_muscle_activation_per_exercise_circles{save_suffix}"
    )
    os.makedirs(save_directory, exist_ok=True)

    plot_mvc_mapping_table(
        channel_names, max_mvc_filenames, mvc_values, participant_type, save_directory
    )

    for exercise_name, activations in activations_per_exercise.items():
        plot_muscle_activation_per_exercise_different_reps(
            activations,
            channel_names,
            exercise_name,
            participant_type,
            save_directory,
        )
