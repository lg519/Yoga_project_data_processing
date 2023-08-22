import os
import re
import numpy as np
from scipy.io import loadmat, savemat
from tkinter import filedialog, Tk


def get_exercise_name(filename):
    """
    Extracts the exercise name (including the repetition) from the filename.
    """
    filename = os.path.basename(filename)
    match = re.search(r"\d{2}_\d{2}_\d{4}", filename)
    if match:
        parts = filename.split(match.group())
        yoga_position = "_".join(parts[0].split("_")[1:-1]).rstrip("_")
        rep = get_repetition(filename)
        return f"{yoga_position}_{rep}"

    raise ValueError(
        f"Could not find the expected date pattern in the filename. Filename is {filename}"
    )


def get_repetition(filename):
    """
    Extracts the repetition from the filename.
    """
    match = re.search(r"rep\d+", filename)
    if match:
        return match.group()
    else:
        raise ValueError(
            f"Could not find the expected repetition pattern in the filename. Filename is {filename}"
        )


def merge_files(directory1, directory2, save_directory):
    # Mapping of exercise name to filename
    dir1_exercise_to_file = {
        get_exercise_name(f): f for f in os.listdir(directory1) if f.endswith(".mat")
    }
    dir2_exercise_to_file = {
        get_exercise_name(f): f for f in os.listdir(directory2) if f.endswith(".mat")
    }

    # All unique exercise names
    all_exercises = set(dir1_exercise_to_file.keys()) | set(
        dir2_exercise_to_file.keys()
    )

    for exercise in all_exercises:
        file1 = dir1_exercise_to_file.get(exercise)
        file2 = dir2_exercise_to_file.get(exercise)

        if file1 and file2:  # If the exercise exists in both directories
            dir1_data = loadmat(os.path.join(directory1, file1))["data"]
            dir2_data = loadmat(os.path.join(directory2, file2))["data"]

            # Determine minimum length across both datasets
            min_len = min(dir1_data.shape[1], dir2_data.shape[1])

            merged_data = {
                "data": np.vstack((dir1_data[0:6, :min_len], dir2_data[4:6, :min_len]))
            }

            savemat(os.path.join(save_directory, file1), merged_data)

        elif file1:  # Exercise only in directory 1
            data = loadmat(os.path.join(directory1, file1))["data"]

            new_data = np.vstack(
                (
                    data[0:6, :],
                    np.zeros_like(data[0:2, :]),  # Zero padding for channels 7 and 8
                )
            )

            savemat(os.path.join(save_directory, file1), {"data": new_data})

        elif file2:  # Exercise only in directory 2
            data = loadmat(os.path.join(directory2, file2))["data"]

            new_data = np.vstack(
                (
                    np.zeros_like(data[0:4, :]),  # Zero padding for channels 1 to 4
                    data[4:6, :],
                    np.zeros_like(data[0:2, :]),  # Zero padding for channels 7 and 8
                )
            )

            savemat(os.path.join(save_directory, file2), {"data": new_data})


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    # Let user select directories
    directory1 = filedialog.askdirectory(title="Select Directory 1 with exercise data")
    directory2 = filedialog.askdirectory(title="Select Directory 2 with exercise data")
    save_directory = filedialog.askdirectory(
        title="Select Directory to save merged files"
    )

    # Merge files
    merge_files(directory1, directory2, save_directory)
