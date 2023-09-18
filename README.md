# Overview

This repository is structured to process EMG (Electromyography) data through various utilities and visualizations. The repository has been structured into folders each catering to specific functionalities as detailed below.

### Running the Files:

When running any of the python scripts from this repository, use the following format:

```bash
/bin/python3 -m <PATH_TO_SCRIPT_WITHOUT_PY_EXTENSION_INTERLEAVED_BY_DOTS>
```

For example, if you want to run visualize_data_processing_stages_64_channels.py from the visualize_high_density_electrodes_data directory, navigate to the repository root and use:

```bash
/bin/python3 -m Process_EMG_data.visualize_high_density_electrodes_data.visualize_data_processing_stages_64_channels
```

## Folder: Process_EMG_data

### Directory Structure and Roles:

1. **helpers**
    - This directory contains utility functions and scripts that aid in the processing of the EMG data.
    - **amplifier_config.py**: Configuration for the amplifier used.
    - **apply_processing_pipeline.py**: Applies the entire processing pipeline on the EMG data.
    - **filtering.py**: Filters the EMG data.
    - **mvc_processing.py**: Processes MVC (Maximum Voluntary Contraction) data.
    - **rectify_signal.py**: Rectifies the EMG signal.
    - **similarity_metrics.py**: Contains metrics to measure similarity in processed data.
    - **utils.py**: Contains general utilities.

2. **images**
    - Houses image files.
    - **Human_Body_Diagram.jpg**: Image showing a human body diagram.
    - **YT1_back.jpg**: An image related to the project (likely showing a back view).

3. **real_time_processing**
    - Contains scripts related to real-time processing of EMG data.
    - **find_minimum_window.py**: Identifies the minimum time window for processing.

4. **visualize_8_channels_electrode_data**
    - Contains visualization scripts specifically for data from 8-channel electrodes.
    - Contains various visualization methods to understand muscle activations and other relevant data features.

5. **visualize_high_density_electrodes_data**
    - Contains visualization scripts for high-density electrode data.
    - Scripts in this directory are focused on visualizing muscle activation heat maps and processing stages for 64 channels, among others.

### Running the Files:

When running any of the python scripts from this repository, use the following format:

```bash
/bin/python3 -m <PATH_TO_SCRIPT_WITHOUT_PY_EXTENSION>
