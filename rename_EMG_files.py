import os
import shutil
from collections import defaultdict
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename

def rename_files():
    Tk().withdraw() # to hide the small tk window

    # open the dialog to select text file and folders
    txt_file = askopenfilename(title = "Select the .txt file containing the list of yoga poses")
    src_folder = askdirectory(title = "Select the Source Folder with .otb+ files")
    dest_folder = askdirectory(title = "Select the Destination Folder to save renamed files")

    # Extract the participant type from the source folder's name
    participant_type = os.path.basename(src_folder).split('_')[0]

    # Read the yoga poses from the text file
    with open(txt_file, 'r') as f:
        yoga_poses = f.read().splitlines()

    # Get the list of EMG recording files
    files = [f for f in os.listdir(src_folder) if os.path.isfile(os.path.join(src_folder, f))]
    print(files)

    # Perform a sanity check
    if len(yoga_poses) != len(files):
        print("len(yoga_poses) = ", len(yoga_poses))
        print("len(files) = ", len(files))
        print("The number of yoga poses does not match the number of files.")
        return

    # Track the repetition of each pose
    pose_counter = defaultdict(int)

    # Sort files based on date and time
    files.sort(key=lambda x: x[-19:-5])

    # Iterate through each file and rename
    for i, filename in enumerate(files):
        # Extract the date and time from the original filename
        date_time = filename[-19:-5]  # year (4 digits), month (2 digits), day (2 digits), hour (2 digits), minutes (2 digits), seconds (2 digits)

        # Format the date and time
        formatted_date = "_".join([date_time[6:8], date_time[4:6], date_time[0:4]])
        formatted_time = "_".join([date_time[8:10], date_time[10:12], date_time[12:]])

        # Get the current pose and increase its counter
        current_pose = yoga_poses[i]
        pose_counter[current_pose] += 1

        # Create the new filename
        new_filename = "{}_{}_{}_{}_rep{}.otb+".format(participant_type, current_pose, formatted_date, formatted_time, pose_counter[current_pose])

        # Copy the file with the new name to the destination folder
        shutil.copy(os.path.join(src_folder, filename), os.path.join(dest_folder, new_filename))

# Use the function
rename_files()
