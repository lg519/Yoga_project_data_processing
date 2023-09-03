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
from scipy.stats import pearsonr


def select_multiple_directories(title="Select Directories"):
    directories = []

    root_directory = filedialog.askdirectory(title=title)
    if root_directory:  # User didn't press cancel or close
        # Scan for all folders inside root_directory that ends with MAT
        for subdirectory in os.listdir(root_directory):
            if subdirectory.endswith("MAT"):
                directories.append(os.path.join(root_directory, subdirectory))

    return directories


def generate_colors(n):
    """Generate n distinct colors using the viridis colormap."""
    colormap = plt.cm.viridis
    return [colormap(i) for i in np.linspace(0, 1, n)]


import numpy as np
from scipy.stats import pearsonr


def average_pearson_coefficient_over_directories(
    activations_by_directory, exercise_name
):
    """Calculate the average Pearson correlation between reps of the same exercise
    across directories based on their activations."""

    correlations = []

    # List of 8-dimensional vectors for each rep in every directory
    vectors_per_rep = []
    directory_rep_info = []  # Store directory and rep index for each vector

    # Loop over all directories (i.e., sessions or individuals)
    for (
        directory_path,
        channel_activations_by_directory,
    ) in activations_by_directory.items():
        # Number of reps (assuming all channels have the same number of reps)
        num_reps = len(channel_activations_by_directory[0])

        # Construct vectors for each rep in the current directory
        for rep_index in range(num_reps):
            vector_for_rep = [
                np.mean(channel_activations[rep_index]) if channel_activations else 0
                for channel_activations in channel_activations_by_directory
            ]
            vectors_per_rep.append(vector_for_rep)
            directory_rep_info.append(
                (directory_path, rep_index)
            )  # Store the directory and rep info

    # Check and print vectors with NaN or inf values
    for i, vec in enumerate(vectors_per_rep):
        if np.any(np.isnan(vec)) or np.any(np.isinf(vec)):
            directory, rep_index = directory_rep_info[i]
            print(
                f"Exercise: {exercise_name}, Directory: {directory}, Rep: {rep_index} has problematic values: {vec}"
            )

    # Compute correlations among vectors of reps
    for i in range(len(vectors_per_rep)):
        for j in range(i + 1, len(vectors_per_rep)):
            if len(vectors_per_rep[i]) == len(
                vectors_per_rep[j]
            ):  # Ensure the vectors have the same length
                # Check if either vector contains NaN or inf before correlation calculation
                if (
                    np.any(np.isnan(vectors_per_rep[i]))
                    or np.any(np.isnan(vectors_per_rep[j]))
                    or np.any(np.isinf(vectors_per_rep[i]))
                    or np.any(np.isinf(vectors_per_rep[j]))
                ):
                    continue
                correlation, _ = pearsonr(vectors_per_rep[i], vectors_per_rep[j])
                correlations.append(correlation)

    return np.mean(correlations)


def plot_muscle_activation_per_exercise_different_reps(
    overall_activations_by_exercise,
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

    # Activations for the given exercise
    activations_by_directory = overall_activations_by_exercise[exercise_name]

    # Loop over all directories (i.e., color groups)
    for color, reps_by_color in activations_by_directory.items():
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

    # Use just the first part (before the first underscore) of the directory for legend labels
    directory_labels = [
        os.path.basename(directory).split("_")[0]
        for directory in activations_by_directory.keys()
    ]

    ax.legend(
        legend_handles, directory_labels, loc="upper right", bbox_to_anchor=(1.25, 1.0)
    )

    # Compute and display the Pearson coefficient for the current exercise
    pearson_coefficient = average_pearson_coefficient_over_directories(
        activations_by_directory, exercise_name
    )

    ax.annotate(
        f"Pearson Coefficient: {pearson_coefficient:.2f}",
        xy=(0.02, 0.02),  # Adjust these values for desired padding
        xycoords="axes fraction",
        fontsize=12,
        fontweight="bold",
        verticalalignment="bottom",
        horizontalalignment="left",
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
            directory_paths, generate_colors(len(directory_paths))
        )
    }

    # overall_activations_per_exercise has the following structure:
    # overall_activations_per_exercise[exercise_name][directory_path][channel_index][rep_index]
    # and is a dictionary of dictionaries of lists of lists
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

    for exercise_name in overall_activations_per_exercise:
        if "MVC" in exercise_name:  # Skip exercises with "MVC" in their name
            continue
        plot_muscle_activation_per_exercise_different_reps(
            overall_activations_per_exercise,  # pass the overall data
            channel_names,
            exercise_name,
            "Overall",
            save_directory,
            colors_by_directory,
        )
