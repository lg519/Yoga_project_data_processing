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

from similarity_metrics import (
    average_pearson_coefficient_over_directories,
    compute_icc_for_exercise,
    average_cosine_similarity_over_directories,
)


def select_multiple_directories(title="Select Directories"):
    all_directories = []
    yt_directories = []
    yp_directories = []

    root_directory = filedialog.askdirectory(title=title)
    if root_directory:  # User didn't press cancel or close
        # Scan for all folders inside root_directory that ends with MAT
        for subdirectory in os.listdir(root_directory):
            if subdirectory.endswith("MAT"):
                full_path = os.path.join(root_directory, subdirectory)
                all_directories.append(full_path)
                if os.path.basename(subdirectory).startswith("YT"):
                    yt_directories.append(full_path)
                elif os.path.basename(subdirectory).startswith("YP"):
                    yp_directories.append(full_path)

    return yt_directories, yp_directories, all_directories


def generate_colors(n):
    """Generate n distinct colors using the viridis colormap."""
    colormap = plt.cm.viridis
    return [colormap(i) for i in np.linspace(0, 1, n)]


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
                alpha=0.55,
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
        legend_handles, directory_labels, loc="upper right", bbox_to_anchor=(1.50, 1.0)
    )

    # Compute the Pearson coefficient for the current exercise
    pearson_coefficient = average_pearson_coefficient_over_directories(
        activations_by_directory, exercise_name
    )

    # Compute the ICC for the current exercise
    icc2_value = compute_icc_for_exercise(activations_by_directory, exercise_name)

    # Compute the cosine similarity for the current exercise
    cosine_similarity = average_cosine_similarity_over_directories(
        activations_by_directory, exercise_name
    )

    # Display the Pearson coefficient, ICC, and cosine similarity in the plot
    ax.annotate(
        f"Pearson Correlation: {pearson_coefficient:.2f}\nICC2: {icc2_value:.2f}\nCosine Similarity: {cosine_similarity:.2f}",
        xy=(1.10, -0.15),  # Adjust these values for desired padding
        xycoords="axes fraction",
        fontsize=12,
        fontweight="bold",
        verticalalignment="bottom",
        horizontalalignment="left",
        bbox=dict(facecolor="white", alpha=0.5),
    )

    plt.tight_layout()
    plot_filename = os.path.join(
        save_directory, f"{participant_type} - {exercise_name}.png"
    )
    plt.savefig(plot_filename)
    plt.close()


def get_rep_number(filename):
    """Extracts the repetition number from the filename."""
    base_name = os.path.basename(filename)
    rep_num_str = base_name.split("_rep")[-1].split(".")[
        0
    ]  # Assuming the extension comes after "_repX"
    return int(rep_num_str)


def compute_exercise_activations(filenames, channel_indices, mvc_values):
    activations_per_exercise = defaultdict(lambda: [list() for _ in channel_indices])

    # Dictionary to keep track of the last rep number for each exercise
    last_rep_for_exercise = defaultdict(int)

    for filename in filenames:
        mat_file = loadmat(filename)
        data = mat_file["data"]
        exercise_name = get_exercise_name(os.path.basename(filename))

        # Checking rep order for each exercise
        current_rep = get_rep_number(filename)
        if current_rep <= last_rep_for_exercise[exercise_name]:
            print(f"Error: {filename} is out of order for {exercise_name}")
        last_rep_for_exercise[exercise_name] = current_rep

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

    yt_directories, yp_directories, all_directories = select_multiple_directories(
        "Select root directory with exercise data"
    )

    # Loop over each group of directories
    for directory_paths, participant_type in zip(
        [yt_directories, yp_directories, all_directories], ["YT", "YP", "Overall"]
    ):
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
        overall_activations_by_exercise = defaultdict(lambda: defaultdict(list))

        for directory_path in directory_paths:
            mvc_values, max_mvc_filenames = calculate_mvc_for_each_channel(
                directory_path, use_automatic
            )
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
                overall_activations_by_exercise[exercise][directory_path] = activations

        save_suffix = "_automatic" if use_automatic else "_fixed"
        main_directory = (
            f"figures_muscle_activation_per_exercise_circles_overall{save_suffix}"
        )
        save_directory = os.path.join(main_directory, participant_type)
        os.makedirs(save_directory, exist_ok=True)

        for exercise_name in overall_activations_by_exercise:
            if "MVC" in exercise_name:  # Skip exercises with "MVC" in their name
                continue
            plot_muscle_activation_per_exercise_different_reps(
                overall_activations_by_exercise,  # pass the overall data
                channel_names,
                exercise_name,
                participant_type,
                save_directory,
                colors_by_directory,
            )
