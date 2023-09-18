from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import pandas as pd

from Process_EMG_data.helpers.mvc_processing import calculate_mvc_for_each_channel
from Process_EMG_data.helpers.apply_processing_pipeline import normalize_signal
from Process_EMG_data.helpers.amplifier_config import sampling_frequency
from Process_EMG_data.helpers.utilis import (
    get_mat_filenames,
    get_partecipant_type,
    get_exercise_name,
)

from matplotlib import pyplot as plt
from Process_EMG_data.helpers.amplifier_config import (
    sampling_frequency,
    get_channel_names,
)


def std_of_sliding_window(data, window_size):
    """
    Calculate the standard deviation for each sliding window of a given size.
    """
    n = len(data)
    std_values = []

    for start in range(n - window_size + 1):
        end = start + window_size
        window_data = data[start:end]
        std_values.append(np.std(window_data))
        print(f"Window {start}-{end}: {np.std(window_data)}")

    return std_values


def minimum_window_for_constant_std(data, relative_tolerance=1e-1):
    """
    Find the minimum window size where standard deviation stays constant for all windows.
    """
    for window_size in range(2, len(data) + 1, 100):
        std_values = std_of_sliding_window(data, window_size)

        # Calculate the mean of the standard deviations
        mean_std = np.mean(std_values)

        # Check if all standard deviations are close to the mean
        if np.all(np.isclose(std_values, mean_std, rtol=relative_tolerance)):
            return window_size
    return None


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

    mvc_values, _ = calculate_mvc_for_each_channel(directory_path)
    channel_names = get_channel_names(directory_path)

    filenames = get_mat_filenames(directory_path)

    activations_per_exercise = compute_exercise_activations(
        filenames, range(len(channel_names)), mvc_values
    )

    results = defaultdict(dict)

    for exercise_name, activations in activations_per_exercise.items():
        print(f"Processing {exercise_name}")
        for idx, channel_data in enumerate(activations):
            for rep, data in enumerate(channel_data):
                min_window = minimum_window_for_constant_std(data)
                if min_window:
                    results[exercise_name][f"Channel_{idx}_Rep_{rep}"] = (
                        min_window / sampling_frequency
                    )  # Convert to seconds

    # Convert results to DataFrame and save to Excel
    df = pd.DataFrame(results).T
    df.to_excel(os.path.join(directory_path, "constant_std_windows.xlsx"))
