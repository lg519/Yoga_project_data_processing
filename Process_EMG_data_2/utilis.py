import os
import re


def get_mat_filenames(directory_path):
    """
    Goes through the given directory and creates a list of all filenames
    that end with the '.mat' extension.

    Args:
    directory_path (str): The directory path where the '.mat' files are located.

    Returns:
    filenames (list): A list of '.mat' filenames with their full paths.
    """
    filenames = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".mat"):
            filenames.append(os.path.join(directory_path, filename))
    return filenames


def get_partecipant_type(filename):
    """
    Extracts the partecipant type from the filename.

    The function expects the filename to contain a date pattern in the format "\d{2}_\d{2}_\d{4}".
    The exercise name (yoga position) is extracted from the portion after this date.

    Args:
    filename (str): The filename from which to extract the exercise name.

    Returns:
    string: The partecipant type (e.g. YT1)

    Raises:
    ValueError: If the date pattern is not found in the filename.
    """

    # TODO: add sanity check going through all the filenames  and making sure the partecipant type is the same.
    # If not raise an error

    filename = os.path.basename(filename)
    match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
    if match:
        # Split the filename into parts before and after the date
        parts = filename.split(match.group())
        participant_type = parts[0].split("_")[0]
        return participant_type

    raise ValueError("Could not find the expected date pattern in the filename.")


def get_exercise_name(filename):
    """
    Extracts the exercise name from the filename.

    The function expects the filename to contain a date pattern in the format "\d{2}_\d{2}_\d{4}".
    The exercise name (yoga position) is extracted from the portion after this date.

    Args:
    filename (str): The filename from which to extract the exercise name.

    Returns:
    string: The name of the exercise

    Raises:
    ValueError: If the date pattern is not found in the filename.
    """
    filename = os.path.basename(filename)
    match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
    if match:
        # Split the filename into parts before and after the date
        parts = filename.split(match.group())
        participant_type = parts[0].split("_")[0]
        yoga_position = "_".join(parts[0].split("_")[1:]).rstrip("_")

        return yoga_position

    raise ValueError(
        f"Could not find the expected date pattern in the filename. Filename is {filename}"
    )
