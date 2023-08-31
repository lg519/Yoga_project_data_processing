import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os
from collections import defaultdict
from mvc_processing import calculate_mvc_for_each_channel
from apply_processing_pipeline import normalize_signal, extract_envelope
from amplifier_config import sampling_frequency, get_channel_names
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


def plot_muscle_activation_per_channel_different_reps_unnormalized(
    activation_reps,
    exercise_names,
    channel_name,
    participant_type,
    max_mvc_filename,
):
    # Filter out exercise names containing "MVC" and their corresponding activations
    exercise_names_filtered, activation_reps_filtered = zip(
        *[
            (name, activations)
            for name, activations in zip(exercise_names, activation_reps)
            if "MVC" not in name
        ]
    )

    # Calculate mean activations for sorting
    mean_activations = [np.mean(reps) for reps in activation_reps_filtered]

    # Sort the data by mean activations
    sort_indices = np.argsort(mean_activations)[::-1]
    # Sort the data by exercise name
    # sort_indices = np.argsort(exercise_names_filtered)
    sorted_exercise_names = np.array(exercise_names_filtered)[sort_indices]
    sorted_activation_reps = np.array(activation_reps_filtered, dtype=object)[
        sort_indices
    ]

    colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_activation_reps[0])))

    # Plot mean activations as bars with a hatch pattern
    bar_width = 0.6
    sorted_mean_activations = [mean_activations[index] for index in sort_indices]
    bars = plt.bar(
        range(len(sorted_exercise_names)),
        sorted_mean_activations,
        width=bar_width,
        color="gray",
        alpha=0.6,
        hatch="/",
        label="Mean Activation",
    )

    # Overlay the mean activation value using a dot and a horizontal line
    for index, (bar, mean_activation) in enumerate(zip(bars, sorted_mean_activations)):
        plt.plot(
            [bar.get_x(), bar.get_x() + bar_width],
            [mean_activation, mean_activation],
            color="black",
        )

    max_reps = max([len(reps) for reps in sorted_activation_reps])
    # Overlay repetitions using colored dots
    for rep_index in range(max_reps):
        current_reps = [
            reps[rep_index] if rep_index < len(reps) else None
            for reps in sorted_activation_reps
        ]
        plt.scatter(
            range(len(sorted_exercise_names)),
            current_reps,
            color=colors[rep_index],
            label=f"Rep {rep_index+1}",
            zorder=2,
        )

    # Label the bars with the exercise names
    plt.xticks(
        np.arange(len(sorted_exercise_names)),
        sorted_exercise_names,
        rotation="vertical",
        fontsize=12,
        fontweight="bold",
    )
    plt.yticks(fontsize=10)
    plt.legend()

    plt.ylabel("Muscle activation mV", fontsize=12, fontweight="bold")
    plt.title(
        f"{participant_type} - {channel_name}",
        fontsize=12,
        fontweight="bold",
    )

    # Add the max MVC filename to the plot
    # plt.text(
    #     0.05,
    #     0.95,
    #     f"MVC used for Normalization: {max_mvc_filename}",
    #     transform=plt.gca().transAxes,
    #     fontsize=12,
    #     style="italic",
    # )

    plt.tight_layout()
    plt.show()


def compute_channel_mean_activations(filenames, channel_index, mvc_values):
    activation_reps_dict = defaultdict(list)

    for filename in filenames:
        mat_file = loadmat(filename)
        data = mat_file["data"]

        processed_data = extract_envelope(
            data[channel_index, :],
            sampling_frequency,
            # mvc_values[channel_index],
        )

        mean_activation = np.mean(processed_data)

        filename = os.path.basename(filename)
        exercise_name = get_exercise_name(filename)

        activation_reps_dict[exercise_name].append(mean_activation)

    return activation_reps_dict


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

    for channel_index, channel_name in enumerate(channel_names):
        max_mvc_filename = max_mvc_filenames[channel_index]
        activation_reps_dict = compute_channel_mean_activations(
            filenames, channel_index, mvc_values
        )

        exercise_names = list(activation_reps_dict.keys())
        activation_reps = [reps for reps in activation_reps_dict.values()]

        plot_muscle_activation_per_channel_different_reps_unnormalized(
            activation_reps,
            exercise_names,
            channel_name,
            participant_type,
            max_mvc_filename,
        )
