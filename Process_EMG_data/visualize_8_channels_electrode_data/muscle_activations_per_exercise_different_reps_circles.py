from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt

from Process_EMG_data.helpers.mvc_processing import (
    calculate_mvc_for_each_channel,
    plot_mvc_mapping_table,
    use_automatic,
)
from Process_EMG_data.helpers.apply_processing_pipeline import normalize_signal
from Process_EMG_data.helpers.amplifier_config import (
    sampling_frequency,
    get_channel_names,
)
from Process_EMG_data.helpers.utilis import (
    get_mat_filenames,
    get_partecipant_type,
    get_exercise_name,
)

import plotly.graph_objects as go


def plot_muscle_activation_per_exercise_different_reps(
    activations,
    channel_names,
    exercise_name,
    participant_type,
    save_directory,
):
    # Checks for empty reps and activations
    for reps, channel in zip(activations, channel_names):
        if len(reps) == 0:
            print(f"Empty reps for Exercise: {exercise_name}, Channel: {channel}")
        for rep_num, rep in enumerate(reps, start=1):
            if len(rep) == 0:
                print(
                    f"Empty rep #{rep_num} in Exercise: {exercise_name}, Channel: {channel}"
                )

    # Get the number of reps for the first channel
    num_reps = len(activations[0])

    # Calculate mean activations for the entire exercise
    mean_activations = [np.mean([np.mean(rep) for rep in reps]) for reps in activations]

    # Convert channel positions to degrees for polar plotting
    theta = np.linspace(0.0, 360, len(channel_names), endpoint=False)
    theta = np.append(theta, 0)  # Close the circle by adding the starting point again

    fig = go.Figure()

    # Plot average activation with dotted lines
    fig.add_trace(
        go.Scatterpolar(
            r=mean_activations + [mean_activations[0]],
            theta=theta,
            mode="lines",
            name="Mean Activation",
            line=dict(color="black", dash="dash"),
        )
    )

    # Colors for repetitions. If more repetitions are present, consider expanding this list or generating it programmatically.
    colors = plt.cm.tab10(np.linspace(0, 1, num_reps))
    # Plot lines connecting the mean activation for each repetition across channels
    for rep_index in range(num_reps):
        activations_for_rep = [
            np.mean(activations[channel][rep_index])
            if len(activations[channel]) > rep_index
            else 0
            for channel in range(len(channel_names))
        ]

        fig.add_trace(
            go.Scatterpolar(
                r=activations_for_rep + [activations_for_rep[0]],
                theta=theta,
                mode="lines+markers",
                name=f"Rep {rep_index + 1}",
                line=dict(color="rgba({},{},{},{})".format(*colors[rep_index], 1)),
            )
        )

    fig.update_layout(
        title=f"{participant_type} - {exercise_name}",
        polar=dict(
            radialaxis=dict(visible=True),
            angularaxis=dict(
                tickvals=np.linspace(0, 360, len(channel_names), endpoint=False),
                ticktext=channel_names,
            ),
        ),
    )

    # Save the plot as an interactive HTML
    plot_filename = os.path.join(
        save_directory, f"{participant_type} - {exercise_name}.html"
    )
    fig.write_html(plot_filename)


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

    parent_directory_path = filedialog.askdirectory(title="Select parent directory")

    # List all directories in the selected parent directory
    all_directories = [
        d
        for d in os.listdir(parent_directory_path)
        if os.path.isdir(os.path.join(parent_directory_path, d))
    ]

    # Filter to only include directories ending with '_MAT'
    mat_directories = [d for d in all_directories if d.endswith("_MAT")]

    # Main save directory
    parent_basename = os.path.basename(parent_directory_path)
    main_save_directory = os.path.join(
        os.getcwd(), "Visualized_EMG_data", parent_basename
    )
    os.makedirs(main_save_directory, exist_ok=True)

    for directory in mat_directories:
        directory_path = os.path.join(parent_directory_path, directory)

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

        # Define the save directory for the current MAT directory
        current_save_directory = os.path.join(
            main_save_directory, os.path.basename(directory_path)
        )
        os.makedirs(current_save_directory, exist_ok=True)

        # After selecting the directory_path and before plotting:
        save_suffix = "_automatic" if use_automatic else "_fixed"
        save_directory = os.path.join(
            current_save_directory,
            f"figures_muscle_activation_per_exercise_circles{save_suffix}",
        )
        os.makedirs(save_directory, exist_ok=True)

        plot_mvc_mapping_table(
            channel_names,
            max_mvc_filenames,
            mvc_values,
            participant_type,
            save_directory,
        )

        for exercise_name, activations in activations_per_exercise.items():
            plot_muscle_activation_per_exercise_different_reps(
                activations,
                channel_names,
                exercise_name,
                participant_type,
                save_directory,
            )
