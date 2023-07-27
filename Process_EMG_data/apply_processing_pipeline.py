# Add all the necessary import statements at the beginning
from load_data import load_data
from filtering import butter_bandpass_filter, find_filter_values
from fft_processing import compute_fft
from low_pass_filtering import rectify_signal, butter_lowpass_filter
from mvc_processing import calculate_mvc_for_each_channel
from normalize_signal import normalize_signal
import numpy as np
import matplotlib.pyplot as plt

from global_variables import num_channels_to_plot


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
    filtered_data_all_channels = np.zeros_like(data, dtype=float)
    for i in range(num_channels_to_plot):
        xf, yf = compute_fft(data[i, :], sampling_frequency)
        highcut, lowcut = find_filter_values(yf)
        filtered_data_all_channels[i, :] = butter_bandpass_filter(
            data[i, :], lowcut, highcut, sampling_frequency
        )

    # Rectify the filtered signal and extract the envelope
    envelopes = np.zeros_like(filtered_data_all_channels, dtype=float)
    for i in range(num_channels_to_plot):
        rectified_data = rectify_signal(filtered_data_all_channels[i, :])
        envelopes[i, :] = butter_lowpass_filter(
            rectified_data, cutoff=5, sampling_frequency=sampling_frequency
        )

    # Normalize the signal using MVC
    normalized_signal = np.zeros_like(envelopes, dtype=float)
    for i in range(num_channels_to_plot):
        # print(f"mvc: {mvc[i]}")
        # print average envelope value
        # print(f"average envelope value: {np.mean(envelopes[i, :])}")

        # # visualize the envelope
        # plt.plot(envelopes[i, :])
        # plt.title(f"Envelope signal")
        # plt.show()
        # plt.show()

        # print type of envelopes
        # normalized_signal[i, :] = envelopes[i, :] / mvc[i]
        if mvc[i] != 0:
            normalized_signal[i, :] = envelopes[i, :] / mvc[i]
        else:
            raise ValueError(f"Error: Division by zero encountered at index {i}")

        # visualize the normalized signal add title

        # plt.plot(normalized_signal[i, :])
        # plt.title(f"Normalized signal")
        # plt.show()
        # print(f"average normalized signal: {np.mean(normalized_signal[i, :])}")

    return normalized_signal
