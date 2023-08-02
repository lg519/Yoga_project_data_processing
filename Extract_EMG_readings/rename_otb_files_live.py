from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict
import time
import os
import shutil
import re
from tkinter import Tk
from tkinter.filedialog import askdirectory


class MyHandler(FileSystemEventHandler):
    def __init__(self, src_folder, dest_folder, yoga_poses, participant_type):
        self.src_folder = src_folder
        self.dest_folder = dest_folder
        self.yoga_poses = yoga_poses
        self.participant_type = participant_type
        self.pose_counter = defaultdict(int)

    def on_created(self, event):
        if event.is_directory:
            return None

        if event.src_path.endswith(".otb+"):
            self.rename_file(event.src_path)

    def rename_file(self, filepath):
        filename = os.path.basename(filepath)
        filename_without_number = re.sub(r"_\d+\.", ".", filename)
        date_time = filename_without_number[-19:-5]

        formatted_date = "_".join([date_time[6:8], date_time[4:6], date_time[0:4]])
        formatted_time = "_".join([date_time[8:10], date_time[10:12], date_time[12:]])

        current_pose = self.yoga_poses.pop(0)
        self.pose_counter[current_pose] += 1

        new_filename = "{}_{}_{}_{}_rep{}.otb+".format(
            self.participant_type,
            current_pose,
            formatted_date,
            formatted_time,
            self.pose_counter[current_pose],
        )

        shutil.copy(filepath, os.path.join(self.dest_folder, new_filename))


def watch_folder():
    Tk().withdraw()

    src_folder = askdirectory(title="Select the Source Folder with .otb+ files")
    src_folder_basename = os.path.basename(src_folder)
    participant_type = os.path.basename(src_folder).split("_")[0]
    parent_folder = os.path.dirname(src_folder)
    dest_folder = os.path.join(parent_folder, src_folder_basename + "_MAT")
    os.makedirs(dest_folder, exist_ok=True)
    txt_file = os.path.join(src_folder, "yoga.txt")

    with open(txt_file, "r") as f:
        yoga_poses = f.read().splitlines()

    event_handler = MyHandler(src_folder, dest_folder, yoga_poses, participant_type)
    observer = Observer()
    observer.schedule(event_handler, path=src_folder, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    watch_folder()
