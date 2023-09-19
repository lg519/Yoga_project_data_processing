from tkinter import Tk

import numpy as np
from scipy.io import loadmat
from tkinter import filedialog
from Process_EMG_data.helpers.rectify_signal import rectify_signal
from Process_EMG_data.helpers.amplifier_config import (
    sampling_frequency,
    lowcut,
    highcut,
)
import matplotlib.pyplot as plt
import fnmatch
import os
from Process_EMG_data.helpers.utilis import get_exercise_name, get_channel_names
from Process_EMG_data.helpers.apply_processing_pipeline import extract_envelope
import tkinter as tk


def process_mvc_data_for_channel(channel_data):
    """
    Process raw MVC data for a specific channel and return the computed MVC value.

    Args:
        channel_data (ndarray): Raw MVC data for a specific channel.

    Returns:
        float: The computed MVC value for the channel.
    """

    mvc_envelope = extract_envelope(channel_data, sampling_frequency)

    # Calculate the MVC value for the channel
    return calculate_mvc_for_channel(mvc_envelope, sampling_frequency)


def get_mvc_files(directory_path):
    """
    Retrieve all the .mat files containing MVCs from a specified directory.

    Args:
        directory_path (str): Path to the directory containing MVC files.

    Returns:
        tuple: A tuple containing two lists: one with the raw data recordings (to be searched for MVC values) and one with their corresponding filenames.
    """
    mvc_files = []
    mvc_filenames = []
    for filename in os.listdir(directory_path):
        if fnmatch.fnmatch(filename, "*.mat"):
            filepath = os.path.join(directory_path, filename)
            mat = loadmat(filepath)
            data = mat["data"]
            mvc_files.append(data)
            mvc_filenames.append(filename)
    # print(f"MVC filenames:{mvc_filenames}")
    return mvc_files, mvc_filenames


def calculate_mvc_for_channel(data, sampling_frequency, window_duration=0.5):
    """
    Calculate the MVC value for a given channel by averaging the data over a specified window duration and
    finding the maximum mean value.

    Args:
        data (list or ndarray): Raw MVC data for a channel.
        sampling_frequency (int): The sampling frequency of the data.
        window_duration (float, optional): Duration (in seconds) of the window over which to average the data. Default is 0.5 seconds.

    Returns:
        float: Maximum mean value (MVC value) for the channel.
    """
    window_size = int(window_duration * sampling_frequency)
    max_mean_value = float("-inf")

    for start_index in range(0, len(data) - window_size):
        end_index = start_index + window_size
        windowed_data = data[start_index:end_index]
        mean_value = np.mean(windowed_data)
        if mean_value > max_mean_value:
            max_mean_value = mean_value
    return max_mean_value


def _calculate_mvc_for_each_channel_fixed(directory_path):
    """
    Calculate MVC values for each channel using a fixed selection of files.

    Args:
        directory_path (str): Path to the directory containing MVC files.

    Returns:
        tuple: A tuple containing an array of MVC values for each channel and a list of selected file paths.
    """
    selected_file_paths = auto_select_files_for_channels(directory_path)
    channel_names = get_channel_names(directory_path)

    max_mvc_values = []

    for i, channel_name in enumerate(channel_names):
        filepath = os.path.join(directory_path, selected_file_paths[i])
        mat = loadmat(filepath)
        data = mat["data"]
        channel_data = data[i, :]
        mvc_value = process_mvc_data_for_channel(channel_data)
        max_mvc_values.append(mvc_value)

    return np.array(max_mvc_values), selected_file_paths


def _calculate_mvc_for_each_channel_automatic(directory_path):
    """
    Calculate MVC values for each channel using an automatic selection of files.
    The files are selected based on which ones have the highest MVC values for a given channel.

    Args:
        directory_path (str): Path to the directory containing MVC files.

    Returns:
        tuple: A tuple containing an array of MVC values for each channel and a list of exercise names corresponding to each value.
    """
    mvc_datas, mvc_filenames = get_mvc_files(directory_path)
    channel_names = get_channel_names(directory_path)

    max_mvc_values = []
    mvc_exercise_names_for_channels = []

    for i, channel_name in enumerate(channel_names):
        max_mvc_value = float("-inf")
        max_mvc_value_index = 0

        for j, mvc_data in enumerate(mvc_datas):
            channel_data = mvc_data[i, :]
            mvc_value = process_mvc_data_for_channel(channel_data)

            if mvc_value > max_mvc_value:
                max_mvc_value = mvc_value
                max_mvc_value_index = j

        max_mvc_values.append(max_mvc_value)
        mvc_exercise_names_for_channels.append(
            get_exercise_name(mvc_filenames[max_mvc_value_index])
        )

    return np.array(max_mvc_values), mvc_exercise_names_for_channels


use_automatic = False  # Set to False to use the "fixed" version. You can change this based on your preference.


def calculate_mvc_for_each_channel(directory_path, use_automatic=False):
    """
    Calculate MVC values for each channel, either using a fixed or automatic file selection.

    Args:
        directory_path (str): Path to the directory containing MVC files.
        use_automatic (bool, optional): If True, uses automatic file selection. Default is False for fixed file selection.

    Returns:
        tuple: MVC values for each channel and corresponding file paths or exercise names.
    """
    if use_automatic:
        return _calculate_mvc_for_each_channel_automatic(directory_path)
    else:
        return _calculate_mvc_for_each_channel_fixed(directory_path)


def select_files_for_channels_gui(directory_path):
    """
    Prompt the user via a GUI to select specific files for each channel.

    Args:
        directory_path (str): Path to the directory containing MVC files.

    Returns:
        list: A list of selected filenames for each channel.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    channel_names = get_channel_names(directory_path)
    selected_files = []

    for channel_name in channel_names:
        filepath = filedialog.askopenfilename(
            initialdir=directory_path,
            title=f"Select a file for {channel_name}",
            filetypes=(("MAT files", "*.mat"), ("all files", "*.*")),
        )
        if filepath:  # If user didn't cancel the dialog
            filename = os.path.basename(filepath)
            selected_files.append(filename)
        else:
            print(f"No file selected for {channel_name}. Exiting.")
            return []

    return selected_files


def auto_select_files_for_channels(directory_path):
    """
    Automatically select files for each channel based on pose names.

    Args:
        directory_path (str): Path to the directory containing MVC files.

    Returns:
        list: A list of selected filenames for each pose.
    """

    # pose_names = [
    #     "Dolphin",
    #     "chaturanga",
    #     "Crow",
    #     "Locust",
    #     "Dolphin",
    #     "Parivrita_Parsvakonasana_left",
    #     "Uttitahasta_Padangustasana_b_right",
    #     "Childs_pose",
    # ]

    pose_names = [
        "tadasana",
        "tadasana",
        "tadasana",
        "tadasana",
        "tadasana",
        "tadasana",
        "tadasana",
        "tadasana",
    ]

    all_files = [f for f in os.listdir(directory_path) if f.endswith(".mat")]

    selected_files = []

    for pose_name in pose_names:
        matched_files = [f for f in all_files if pose_name in f and "_rep1" in f]

        # If multiple matches are found for the same pose, you might want to add additional logic to select the desired one.
        # Here, I'm simply taking the first match.
        if matched_files:
            selected_files.append(matched_files[0])
        else:
            print(f"No file found for pose: {pose_name} with _rep1. Exiting.")
            return []

    return selected_files


def plot_mvc_mapping_table(
    channel_names, max_mvc_filenames, mvc_values, participant_type, save_directory
):
    """
    Create and save a table mapping MVC values and filenames to channels.

    Args:
        channel_names (list): List of channel names.
        max_mvc_filenames (list): List of filenames containing the maximum MVC values for each channel.
        mvc_values (list or ndarray): List of MVC values.
        participant_type (str): Type of the participant (e.g., "Beginner", "Expert").
        save_directory (str): Directory where the table should be saved.

    Returns:
        None: The table is saved to the specified directory and not returned.
    """

    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust figsize for an extra column
    stripped_mvc_filenames = [os.path.basename(f) for f in max_mvc_filenames]
    rows = list(zip(channel_names, stripped_mvc_filenames, mvc_values))
    table_data = [["Channel Name", "MVC File", "MVC Value"]] + rows

    ax.axis("off")
    table = ax.table(
        cellText=table_data,
        cellLoc="center",
        loc="center",
        colWidths=[0.4, 0.4, 0.2],  # Adjusted colWidths for equal spacing
    )

    # Increase the font size for the whole table
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # Bold the header
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_text_props(fontweight="bold")

    plt.title(f"{participant_type} - MVC File Mapping")

    # Save the table
    table_filename = os.path.join(
        save_directory, f"{participant_type} - MVC File Mapping.png"
    )
    plt.savefig(table_filename)
    plt.close()


if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the main window
    directory_path = filedialog.askdirectory(title="Select MVC Files directory")
    root.destroy()

    max_mvc_values, mvc_exercise_names_for_channels = calculate_mvc_for_each_channel(
        directory_path
    )

    channel_names = get_channel_names(directory_path)
    print("Max MVC Values and Filenames for Each Channel:")
    for i, (value, filename) in enumerate(
        zip(max_mvc_values, mvc_exercise_names_for_channels)
    ):
        channel_name = channel_names[i]
        print(f"{channel_name}: Max Value = {value}, Filename = {filename}")

    print("\nAll MVC Values Calculated:")
    mvc_datas, mvc_filenames = get_mvc_files(directory_path)
    for i, channel_name in enumerate(channel_names):
        print(f"{channel_name}:")
        for j, mvc_data in enumerate(mvc_datas):
            channel_data = mvc_data[i, :]
            mvc_value = process_mvc_data_for_channel(channel_data)
            print(f"  File {j+1} ({mvc_filenames[j]}): {mvc_value}")
