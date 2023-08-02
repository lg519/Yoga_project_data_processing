from filtering import butter_bandpass_filter, butter_lowpass_filter
from rectify_signal import rectify_signal
import numpy as np

from amplifier_config import highcut, lowcut


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
    filtered_data = butter_bandpass_filter(data, lowcut, highcut, sampling_frequency)

    # Rectify the filtered signal and extract the envelope
    envelope = np.zeros_like(filtered_data, dtype=float)
    rectified_data = rectify_signal(filtered_data)
    envelope = butter_lowpass_filter(
        rectified_data, cutoff=5, sampling_frequency=sampling_frequency
    )

    # Normalize the signal using MVC
    normalized_signal = np.zeros_like(envelope, dtype=float)
    if mvc != 0:
        normalized_signal = envelope / mvc
    else:
        raise ValueError(f"Error: Division by zero")
    return normalized_signal
