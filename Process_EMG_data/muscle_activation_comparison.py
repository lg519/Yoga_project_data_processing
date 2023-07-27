import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import Tk
import os
import re
from collections import defaultdict
from mvc_processing import calculate_mvc_for_each_channel
from apply_processing_pipeline import apply_processing_pipeline
from global_variables import sampling_frequency


def plot_data(activation_means, exercise_names, channel_name, participant_type):
    # Sort the data by exercise names
    sort_indices = np.argsort(exercise_names)
    sorted_exercise_names = np.array(exercise_names)[sort_indices]
    sorted_activation_means = np.array(activation_means)[sort_indices]

    # Generate a bar graph of the average muscle activation
    plt.bar(np.arange(len(sorted_exercise_names)), sorted_activation_means)

    # Label the bars with the exercise names
    plt.xticks(
        np.arange(len(sorted_exercise_names)),
        sorted_exercise_names,
        rotation="vertical",
    )

    # Set the y-axis label
    plt.ylabel("Muscle activation (% of MVC)")

    # Set the title
    plt.title(f"Participant Type: {participant_type}, Channel: {channel_name}")

    # Show the plot
    plt.tight_layout()
    plt.show()


# Define channel names
channel_names = [
    "Upper Trap (Right side)",
    "Middle Trap (Right side)",
    "Lower Trap (Right side)",
    "Serratus Anterior (Right side)",
]

# Hide the main tkinter window
root = Tk()
root.withdraw()

# Open a directory dialog
directory_path = filedialog.askdirectory(title="Select directory with exercise data")


# Calculate the MVC value for each channel
mvc_values = calculate_mvc_for_each_channel()


# Initialize list to store filenames
filenames = []

# Iterate over files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".mat"):
        # Append filename to the list
        filenames.append(os.path.join(directory_path, filename))

# For each channel, compute the mean activation for each exercise and plot
for channel_index, channel_name in enumerate(channel_names):
    # Initialize dictionary to store mean muscle activation values per exercise
    activation_means_dict = defaultdict(list)
    participant_type = ""

    for filename in filenames:
        # Load the data from the .mat file
        mat = loadmat(filename)

        # Extract the data
        data = mat["data"]

        # Process the EMG data
        processed_data = apply_processing_pipeline(data, sampling_frequency, mvc_values)

        # Compute the mean muscle activation for the selected channel
        mean_activation = np.mean(processed_data[channel_index, :])

        # Extract the exercise name from the filename and store for labeling
        filename = os.path.basename(filename)
        match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
        if match:
            # Split the filename into parts before and after the date
            parts = filename.split(match.group())
            participant_type = parts[0].split("_")[0]
            yoga_position = "_".join(parts[0].split("_")[1:]).rstrip("_")

            # Skip this file if the yoga position is MVC
            if "MVC" in yoga_position:
                continue

            activation_means_dict[yoga_position].append(mean_activation)

    # Compute the mean of means for each exercise
    exercise_names = list(activation_means_dict.keys())
    activation_means = [np.mean(means) for means in activation_means_dict.values()]

    # Plot the data for the current channel
    plot_data(activation_means, exercise_names, channel_name, participant_type)