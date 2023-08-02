# Define channel names
# channel_names = [
#     "Upper Trap (Right side)",
#     "Middle Trap (Right side)",
#     "Lower Trap (Right side)",
#     "Serratus Anterior (Right side)",
#     "Upper Trap (Left side)",
#     "Middle Trap (Left side)",
#     "Lower Trap (Left side)",
#     "Serratus Anterior (Left side)",
# ]
# channel_names = [
#     "Glute Max (Left side)",
#     "Glute Max (Right side)",
#     "Lower Rectus (Left side)",
#     "Lower Rectus (Right side)",
#     "lower trap (Left side)",
#     "lower trap (Right side)",
# ]
# channel_names = [
#     "Upper Trap (Right side)",
#     "Middle Trap (Right side)",
#     "Lower Trap (Right side)",
#     "Serratus Anterior (Right side)",
# ]

import os


def get_channel_config(directory_path):
    with open(os.path.join(directory_path, "channel_config.txt"), "r") as file:
        lines = file.readlines()

    # strip newline characters
    channel_names = [line.strip() for line in lines]
    return channel_names


# Create time array for x-axis, considering sampling frequency
sampling_frequency = 2000  # Hz

# Set values for bandpass filter
highcut = 450
lowcut = 20
