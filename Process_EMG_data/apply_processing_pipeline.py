# Add all the necessary import statements at the beginning

from filtering import butter_bandpass_filter, butter_lowpass_filter
from rectify_signal import rectify_signal
from mvc_processing import calculate_mvc_for_each_channel
from normalize_signal import normalize_signal
import numpy as np
import matplotlib.pyplot as plt

from global_variables import num_channels_to_plot, highcut, lowcut


def apply_processing_pipeline(data, sampling_frequency, mvc):
    """
    Process the raw EMG data and return the normalized signal for each channel.

    Args:
        data (np.array): The raw EMG data. The first dimension is channels, and the second is time.
        sampling_frequency (int): The sampling frequency of the signal.
        mvc (array): The MVC values for each channel.

    Returns:
        normalized_signal (np.array): The normalized signal for each channel.
    """

    # Apply the bandpass filter
    filtered_data = np.zeros_like(data, dtype=float)
    for i in range(num_channels_to_plot):
        filtered_data[i, :] = butter_bandpass_filter(
            data[i, :], lowcut, highcut, sampling_frequency
        )

    # Rectify the filtered signal and extract the envelope
    envelopes = np.zeros_like(filtered_data, dtype=float)
    for i in range(num_channels_to_plot):
        rectified_data = rectify_signal(filtered_data[i, :])
        envelopes[i, :] = butter_lowpass_filter(
            rectified_data, cutoff=5, sampling_frequency=sampling_frequency
        )

    # Normalize the signal using MVC
    normalized_signal = np.zeros_like(envelopes, dtype=float)
    for i in range(num_channels_to_plot):
        if mvc[i] != 0:
            normalized_signal[i, :] = envelopes[i, :] / mvc[i]
        else:
            raise ValueError(f"Error: Division by zero encountered at index {i}")
    return normalized_signal
