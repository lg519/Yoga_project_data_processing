# Overview

This repository is structured to process EMG (Electromyography) data through various utilities and visualizations. The repository has been structured into folders each catering to specific functionalities as detailed [here](#repository-structure). If you are unfamiliar with programming, the [getting started guide](#getting-started) will enable you to download the necessary files, install the required libraries and start running the various scripts for processing the data.

# Getting Started

## Cloning the `Yoga_project_data_processing` Directory to Your Laptop

**What is "cloning"?**  
Cloning means copying a folder from the internet to your computer. In this case, we're copying the `Yoga_project_data_processing` directory.

### Step 1: Install Git

Before cloning, you need a tool called "Git."

1. Visit the [official Git download page](https://git-scm.com/downloads).
2. Select the version for your operating system (Windows, Mac, Linux).
3. Download and run the installer. Follow the on-screen instructions. You can stick with the default options during installation.

### Step 2: Clone the Directory

1. Open the location where you want the `Yoga_project_data_processing` directory using File Explorer (for Windows) or Finder (for Mac).
2. Right-click (or Ctrl-click on Mac) in the folder. If you see an option like "Git Bash Here" (Windows) or "Open Terminal" (Mac), choose it. This opens a black window called a "terminal" or "command prompt."
3. In the terminal, type: 
    ```bash 
    git clone https://github.com/lg519/Yoga_project_data_processing.git
    ```
4. Press `Enter`.
5. Wait a bit. Git will now clone the directory to your laptop.
6. After it's done, you'll find a new folder named `Yoga_project_data_processing` in your chosen location. This folder has all the online directory's files and subfolders.


## Installing Necessary Libraries using `requirements.txt`

The `requirements.txt` file is a simple way to list all the special tools (or "libraries") that your project needs. By following these steps, you can install all these tools in one go!

### Step 1: Ensure you have Python and `pip` installed:

Before you start, you must have Python and `pip` (a tool that helps install Python libraries) on your computer.

**Checking if you have Python:**

1. Open a terminal:
   - **Windows**: Search for `cmd` or `Command Prompt` in the Start Menu and open it.
   - **Mac**: Search for `Terminal` in Spotlight (Cmd + Space) and open it.
   - **Linux**: Usually, it's either in the Applications menu or you can access it via a shortcut like Ctrl + Alt + T.

2. In the terminal, type `python --version` (or `python3 --version` if `python` doesn't work) and press `Enter`.

You should see a version number. This means Python is installed. If not, you'll need to [install Python](https://www.python.org/downloads/).

**Checking if you have `pip`:**

In the same terminal, type `pip --version` and press `Enter`.

If you see a version number, you're good to go! If not, Python might have been installed without `pip`. But usually, `pip` is included with Python installations from Python 2.7.9 onwards.

### Step 2: Navigate to the Project Folder:

In the terminal, navigate to the directory where you've cloned the `Yoga_project_data_processing` repository.

Use the `cd` command followed by the path of your directory. For example:
```bash
cd path/to/Yoga_project_data_processing
```

### Step 3: Install the Libraries:

Now that you're in the project directory, type the following command to install all necessary libraries:
```bash
pip install -r requirements.txt
```
Then press `Enter`.

This command tells `pip` to install all the libraries listed in the `requirements.txt` file. Wait for the process to complete. It may take a few minutes.


## Running the Scripts

1. **Open your command line or terminal**:
   - **Windows**: Search for `cmd` or `Command Prompt` in the Start Menu and open it.
   - **Mac**: Search for `Terminal` in Spotlight (Cmd + Space) and open it.
   - **Linux**: It's often in the Applications menu, or you can use a shortcut like Ctrl + Alt + T.

2. **Go to the project's folder**:
   Use the command `cd` followed by the location (or "path") of the `Yoga_project_data_processing` folder. For instance:
   ```bash
   cd path/to/Yoga_project_data_processing
   ```
   Don't forget to replace path/to/Yoga_project_data_processing with the actual location on your computer!

3. **Run the script**:
    Whenever you want to run a script, use the following format:
    ```bash
   /bin/python3 -m FolderName.SubfolderName.ScriptName
   ```
   Let's break it down:
   - /bin/python3 is just telling your computer to use Python.
   - -m is a special command that tells Python to look for a module or script.
   - FolderName.SubfolderName.ScriptName is the path to the script you want to run, but with dots instead of slashes and without the .py at the end.

    Here's a real-life example: Let's say you want to run a script called visualize_data_processing_stages_64_channels.py which is inside the Process_EMG_data\visualize_high_density_electrodes_data folder. You would type:
    ```bash
    /bin/python3 -m Process_EMG_data.visualize_high_density_electrodes_data.visualize_data_processing_stages_64_channels
    ```
    And press Enter.

4.  **Wait for it**:
    Once you press Enter, the script will start running. Depending on the script, it might take a few seconds to a few minutes. Just be patient!


# Repository Structure

In the `Yoga_Project_Data_Processing` repository, there are four primary folders, each serving a unique purpose in the process of extracting, processing, and visualizing EMG data:

1. **EMG_data**: 
   - **Purpose**: This is the storage point for all the raw data. 
   - **What you'll find here**: All the initial recordings directly from the amplifier, which will be converted and processed by the scripts in our other folders.

2. **Extract_EMG_Readings**: 
   - **Purpose**: This folder contains scripts to transform the raw recordings taken from the amplifier (which are in `.otb` format) into MATLAB files. 
   - **Why it's important**: By converting our data into MATLAB files, we can process them in the subsequent stages.

3. **Process_EMG_Data**: 
   - **Purpose**: Once we have our MATLAB files, this folder comes into action. It contains scripts that process the data in various ways, from filtering to extracting specific metrics.
   - **Outcome**: After processing, the results are visualized and those visualizations are saved in the `Visualized_EMG_Data` folder.

4. **Visualized_EMG_Data**:
   - **Purpose**: All the visualizations created by the `Process_EMG_Data` scripts are saved here.
   - **Note**: There's an exception for visualizations related to high density electrodes. Instead of this folder, they are saved within subfolders inside the `EMG_data` folder.


## Folder: EMG_data
This folder is split in 3 subdirectories:
- `trial_sessions`: a folder containing the data that we collected at the beginning of the project for exploratory porpuses.
- `actual_testing`: a folder containing the data collected for the study. All the recordings on this folder are on the 8 muscles selected for the study.
- `high_density_electrodes`: a folder containing the data collected using the three 64 channel grids rather than the usual bipolar electrodes.

Each subfolder in any of these folders corresponds to a specific recording session for a given partecipant.

The naming convention for these directories is to start with the participant type (for example, `YP1` for the first participant of type `YP`), followed by an underscore, and then a description (like `testing`) followed by an underscore and then the session number.

Additionally, for each folder there is an additionalfolder named after the original folder, but with the addition of the `_MAT` suffix. These additional folders are generated by the scripts in Extract_EMG_Readings, and contain the raw data converted to a format suitable for processing.

Here is an example of how the `EMG_data` folder looks like:

```
EMG_data
├── actual_testing
│ ├── YP2_actual_testing_1
│ ├── YP2_actual_testing_1_MAT
│ ├── YP3_actual_testing_1
│ ├── ...
│ ├── YT8_actual_testing_1
│ └── YT9_actual_testing_1_MAT
├── high_density_electrodes
│ ├── YT1_testing_6
│ ├── YT1_testing_6_MAT
│ ├── ...
│ └── YT1_testing_7_MAT
└── trial_sessions
├── YP1_testing_1
├── YP1_testing_1_MAT
├── ...
└── YT1_testing_6
```


## Folder: Extract_EMG_Readings 

The `Extract_EMG_Readings` folder is a pivotal starting point in the `Yoga_Project_Data_Processing` repository. It contains scripts dedicated to preparing and converting raw EMG data to a more usable format. The scripts in this directory should be executed **sequentially**; begin with `rename_otb_files.py` and then proceed with `convert_otb_to_mat_files.m`. Let's delve into the specifics of the two main scripts inside this folder:

### 🚨 Warning 🚨
> ⚠️ **Ensure the order of raw data files (`.otb` files) matches the sequence in `yoga.txt`**. The first pose in `yoga.txt` should correspond to the first recording in alphanumeric order, and so on. Disruptions like accidental file renames or amplifier disconnections can disturb this order. If such situations arise, inspect and correct the data manually to preserve the integrity of the dataset. 

> 🔥 **Always make a backup of your data before running any script in this folder**. Mistakes can happen, and as these scripts act on the raw recordings, having a backup ensures that your original data remains safe.

### 1. `rename_otb_files.py`

**What it does**: 
- This Python script automates the renaming process of raw `.otb+` files from the amplifier. It accomplishes this by moving these files to a new folder named after the original folder, but with the addition of the `_MAT` suffix.
- Files are renamed based on participant type, yoga pose name, and repetition number.
- The script also ensures that files which do not have the `.otb+` extension are copied to a designated folder without renaming.

**How to use it**: 
- Simply run the script. Upon execution, a dialog window will appear asking you to select the source folder that contains the `.otb+` files.
- Ensure that there's a `yoga.txt` file in the source folder which lists all yoga poses in the sequence they were performed. This will be used to determine the yoga pose names for renaming.

**What the script expects**:
- The source folder name should contain the participant type as its prefix, separated by an underscore (e.g., `ParticipantType_RestOfFolderName`).

### 2. `convert_otb_to_mat_files.m`

**What it does**: 
- This MATLAB script converts the renamed `.otb+` files into MATLAB `.mat` files, making them ready for subsequent processing.

**How to use it**:
- This is a MATLAB script, and it's run differently from Python scripts.
- Before running, ensure that you have MATLAB installed and set up on your computer.
- Open MATLAB and navigate to the directory containing `convert_otb_to_mat_files.m`.
- Once inside that directory in the MATLAB environment, you can run the script by simply typing `convert_otb_to_mat_files` in the MATLAB command window and pressing enter.
- The script will process the `.otb+` files in the directory and convert them to `.mat` format.

🚫 **Caution**: Running `convert_otb_to_mat_files.m` on the raw data folder risks deleting the recordings. Always ensure you're operating on the folder generated by `rename_otb_files.py`.

**Data expectations**: 
- The script expects to find `.otb+` files (those renamed by the previous script) in the directory where it's executed.

## Folder: Process_EMG_data

This folder is dedicated to the processing and visualization of EMG recordings, after they have been converted in `.mat` files.

### Process_EMG_data folder Structure:

1. **helpers**
    - This directory contains utility functions and scripts that aid in the processing of the EMG data.
    - **amplifier_config.py**: Contains configuration details for the amplifier used.
    - **apply_processing_pipeline.py**: Contains functions to apply the signal processing pipeline on the EMG data.
    - **filtering.py**: Contains various filters implementaition used for signal processing.
    - **mvc_processing.py**: Contains functions to calculate the MVC (Maximum Voluntary Contraction) for the recordings.
    - **rectify_signal.py**: Rectifies the EMG signal.
    - **similarity_metrics.py**: Contains metrics to measure similarity (Pearson correlation, ICC, Cosine similarity) in processed data.
    - **utils.py**: Contains general utilities to extract information form the files.

2. **images**
    - Contains image files used for high density electrodes visualization.
3. **real_time_processing**
    - Contains scripts related to real-time processing of EMG data.
    - **find_minimum_window.py**: Identifies the minimum time window for processing using standard deviation.

4. **visualize_8_channels_electrode_data**
    - Contains visualization scripts specifically for data from 8-channel electrodes.
    - Contains various visualization methods to understand muscle activations and other relevant data features.

5. **visualize_high_density_electrodes_data**
    - Contains visualization scripts for high-density electrode data.
    - Scripts in this directory are focused on visualizing muscle activation heat maps for 64 channels.
    - Contains scripts to visualize the data processing stages (envelope of the signal, FFT, filtered signal...) of the high density data. As my laptop did not have enough processing power the script prompts to select how many files to process and the file to start the processing from. This feature is helpful as it enables users to segment the processing into manageable chunks, thus avoiding system overloads.



