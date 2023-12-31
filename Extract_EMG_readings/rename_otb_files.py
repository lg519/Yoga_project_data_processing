import os
import shutil
from collections import defaultdict
import re
from tkinter import Tk
from tkinter.filedialog import askdirectory


def rename_files():
    Tk().withdraw()  # to hide the small tk window

    # open the dialog to select folders
    src_folder = askdirectory(title="Select the Source Folder with .otb+ files")

    # Extract the participant type from the source folder's name
    src_folder_basename = os.path.basename(src_folder)
    participant_type = os.path.basename(src_folder).split("_")[0]

    # Get parent folder of source
    parent_folder = os.path.dirname(src_folder)

    # Create a new destination folder under the parent folder
    dest_folder = os.path.join(parent_folder, src_folder_basename + "_MAT")
    os.makedirs(dest_folder, exist_ok=True)

    # Set the path for the yoga poses txt file
    txt_file = os.path.join(src_folder, "yoga.txt")

    # Read the yoga poses from the text file
    with open(txt_file, "r") as f:
        yoga_poses = f.read().splitlines()

    # Get the list of all files
    all_files = [
        f for f in os.listdir(src_folder) if os.path.isfile(os.path.join(src_folder, f))
    ]

    # Filter out the EMG recording files
    otb_files = [f for f in all_files if f.endswith(".otb+")]

    # Copy files that don't end with .otb+ to the destination folder
    for f in all_files:
        if not f.endswith(".otb+"):
            shutil.copy(os.path.join(src_folder, f), os.path.join(dest_folder, f))

    # Perform a sanity check
    if len(yoga_poses) != len(otb_files):
        print("len(yoga_poses) = ", len(yoga_poses))
        print("len(otb_files) = ", len(otb_files))
        print("The number of yoga poses does not match the number of files.")
        return

    # Track the repetition of each pose
    pose_counter = defaultdict(int)

    # Sort otb_files based on date and time
    otb_files.sort(key=lambda x: x[-19:-5])

    # Iterate through each file and rename
    for i, filename in enumerate(otb_files):
        filename_without_number = re.sub(r"_\d+\.", ".", filename)

        # Extract and format the date and time from the original filename
        date_time = filename_without_number[-19:-5]
        formatted_date = "_".join([date_time[6:8], date_time[4:6], date_time[0:4]])
        formatted_time = "_".join([date_time[8:10], date_time[10:12], date_time[12:]])

        # Get the current pose and increase its counter
        current_pose = yoga_poses[i]
        pose_counter[current_pose] += 1

        # Create the new filename
        new_filename = "{}_{}_{}_{}_rep{}.otb+".format(
            participant_type,
            current_pose,
            formatted_date,
            formatted_time,
            pose_counter[current_pose],
        )

        # Copy the otb file with the new name to the destination folder
        shutil.copy(
            os.path.join(src_folder, filename), os.path.join(dest_folder, new_filename)
        )


if __name__ == "__main__":
    rename_files()
