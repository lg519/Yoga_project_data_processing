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
)
from Process_EMG_data.helpers.utilis import (
    get_mat_filenames,
    get_exercise_name,
    get_channel_names,
    get_rep_number,
)

from Process_EMG_data.helpers.similarity_metrics import (
    average_pearson_coefficient_over_directories,
    compute_icc_for_exercise,
    average_cosine_similarity_over_directories,
)

import plotly.graph_objects as go
import pandas as pd


def select_multiple_directories(title="Select root directory with exercise data"):
    """
    Prompt the user to select the root directory containing the subdirectories with the MAT files.

    Args:
    - title (str): Title for the directory selection dialog.

    Returns:
    - tuple: Directories for YT, YP, and all MAT directories.
    """

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
    """
    Generate a list of distinct colors.

    Args:
    - n (int): Number of colors to generate.

    Returns:
    - list: List of distinct colors in rgba format.
    """
    colormap = plt.cm.viridis
    return [colormap(i) for i in np.linspace(0, 1, n)]


# Convert tuple color to rgba string
def tuple_to_rgba(color_tuple):
    """
    Convert a tuple-based color representation to an RGBA string.

    Args:
    - color_tuple (tuple): Color as an RGBA tuple.

    Returns:
    - str: RGBA color string.
    """
    return f"rgba({int(color_tuple[0]*255)}, {int(color_tuple[1]*255)}, {int(color_tuple[2]*255)}, {color_tuple[3]})"


def is_outlier(value, mean, std_dev, multiplier=2):
    """
    Determine if a value is an outlier based on standard deviations.

    Parameters:
    - value (float): The value to be checked.
    - mean (float): The mean of the dataset.
    - std_dev (float): The standard deviation of the dataset.
    - multiplier (float, optional): The multiplier for the standard deviation. Determines the range outside
      of which values are considered outliers. Default is 2.

    Returns:
    - bool: True if the value is an outlier, otherwise False.

    Example:
    >>> is_outlier(10, 5, 2)
    False
    >>> is_outlier(10, 5, 1)
    True
    """

    lower_bound = mean - multiplier * std_dev
    upper_bound = mean + multiplier * std_dev

    return value < lower_bound or value > upper_bound


def plot_muscle_activation_per_exercise_different_reps(
    overall_activations_by_exercise,
    channel_names,
    exercise_name,
    participant_type,
    save_directory,
    colors_by_directory,
):
    """
    Create a plotly figure representing muscle activation for different reps.

    Args:
    - overall_activations_by_exercise (dict): Nested dictionary of activations.
    - channel_names (list): List of channel names.
    - exercise_name (str): Name of the exercise to visualize.
    - participant_type (str): Type of the participant (e.g., YT, YP).
    - save_directory (str): Directory path to save the generated figure.
    - colors_by_directory (dict): Color mapping for directories.

    Returns:
    - None: The function saves the plot to the specified directory.
    """

    # Activations for the given exercise
    activations_by_directory = overall_activations_by_exercise[exercise_name]

    fig = go.Figure()

    # Get all mean values for outlier detection
    all_mean_values = []
    for color, reps_by_color in activations_by_directory.items():
        for rep_index in range(len(reps_by_color[0])):
            for channel in range(len(channel_names)):
                if len(reps_by_color[channel]) > rep_index:
                    all_mean_values.append(np.mean(reps_by_color[channel][rep_index]))

    # Calculate mean and standard deviation
    mean_value = np.mean(all_mean_values)
    std_dev_value = np.std(all_mean_values)

    for color, reps_by_color in activations_by_directory.items():
        num_reps = len(reps_by_color[0])

        for rep_index in range(num_reps):
            activations_for_rep = [
                np.mean(reps_by_color[channel][rep_index])
                if len(reps_by_color[channel]) > rep_index
                else 0
                for channel in range(len(channel_names))
            ]

            # Check for outliers
            if any(
                is_outlier(val, mean_value, std_dev_value)
                for val in activations_for_rep
            ):
                continue  # Skip this rep if any channel has an outlier value

            # Normalize activations_for_rep by its norm
            norm = np.linalg.norm(activations_for_rep)
            activations_for_rep = [value / norm for value in activations_for_rep]

            trace_name = os.path.basename(color).split("_")[0]

            fig.add_trace(
                go.Scatterpolar(
                    r=activations_for_rep + [activations_for_rep[0]],
                    theta=channel_names + [channel_names[0]],
                    name=trace_name,
                    marker=dict(color=tuple_to_rgba(colors_by_directory[color])),
                    line=dict(color=tuple_to_rgba(colors_by_directory[color])),
                    opacity=0.55,
                )
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

    annotations = [
        dict(
            text=f"<b>Pearson Correlation: {pearson_coefficient:.2f}<br>ICC2: {icc2_value:.2f}<br>Cosine Similarity: {cosine_similarity:.2f}</b>",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=1.00,
            y=0.05,
        )
    ]

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
            )
        ),
        showlegend=True,
        title=f"{participant_type} - {exercise_name}",
        annotations=annotations,
    )

    # Save the figure
    plot_filename = os.path.join(
        save_directory, f"{participant_type} - {exercise_name}.html"
    )
    fig.write_html(plot_filename)


def compute_exercise_activations(filenames, channel_indices, mvc_values):
    """
    Compute activations for exercises.

    Args:
    - filenames (list): List of filenames containing EMG data.
    - channel_indices (list): Indices for channels.
    - mvc_values (list): Maximum voluntary contraction values for channels.

    Returns:
    - dict: Dictionary of activations for each exercise.
    """
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


def save_activations_to_excel(
    overall_activations_by_exercise, channel_names, save_directory
):
    """
    Save activations to an Excel file.

    Args:
    - overall_activations_by_exercise (dict): Nested dictionary of activations.
    - channel_names (list): List of channel names.
    - save_directory (str): Directory path to save the Excel file.

    Returns:
    - None: The function saves the data to the specified directory.
    """

    # Creating an empty DataFrame to store the final result
    result_df = pd.DataFrame()

    for (
        exercise_name,
        activations_by_directory,
    ) in overall_activations_by_exercise.items():
        exercise_data = []

        for directory, channels in activations_by_directory.items():
            participant_code = os.path.basename(directory).split("_")[0]

            for channel_idx, reps in enumerate(channels):
                muscle_name = channel_names[channel_idx]
                mean_values = []  # To store the mean values of each rep

                for rep_idx, value in enumerate(reps):
                    mean_val = (
                        value.mean() if len(value) > 0 else 0
                    )  # Mean value of current rep
                    mean_values.append(mean_val)
                    exercise_data.append(
                        {
                            "Participant": participant_code,
                            "Muscle Name": muscle_name,
                            "Rep Number": rep_idx + 1,
                            exercise_name: mean_val,
                        }
                    )

                # Compute the overall mean across the reps
                overall_mean = sum(mean_values) / len(mean_values) if mean_values else 0
                exercise_data.append(
                    {
                        "Participant": participant_code,
                        "Muscle Name": muscle_name,
                        "Rep Number": "Mean of Reps",
                        exercise_name: overall_mean,
                    }
                )

        # Convert the current exercise data to a dataframe and merge with the result
        current_df = pd.DataFrame(exercise_data)
        if result_df.empty:
            result_df = current_df
        else:
            result_df = pd.merge(
                result_df,
                current_df,
                on=["Participant", "Muscle Name", "Rep Number"],
                how="outer",
            )

    # Save to Excel
    output_path = os.path.join(save_directory, "AllExercises.xlsx")
    result_df.to_excel(output_path, index=False, engine="openpyxl")


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
        visualization_root_directory = "Visualized_EMG_data"
        main_directory = os.path.join(
            visualization_root_directory,
            f"figures_muscle_activation_per_exercise_circles_overall{save_suffix}",
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

        # Saving activations to Excel
        save_activations_to_excel(
            overall_activations_by_exercise, channel_names, save_directory
        )
