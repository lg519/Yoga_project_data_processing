import os


def get_channel_names(directory_path):
    """
    Reads the channel configuration from a text file in the given directory, and returns the channel names.

    Args:
    directory_path (str): The directory path where the 'channel_config.txt' file is located.

    Returns:
    channel_names (list): A list of channel names.
    """
    with open(os.path.join(directory_path, "channel_config.txt"), "r") as file:
        lines = file.readlines()

    # strip newline characters
    channel_names = [line.strip() for line in lines]
    return channel_names


sampling_frequency = 2000  # Hz
# Set values for bandpass filter
highcut = 450
lowcut = 20
