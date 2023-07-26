from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import numpy as np

from global_variables import (
    num_channels_to_plot,
    channel_names,
    sampling_frequency,
)


def butter_lowpass_filter(data, cutoff, sampling_frequency, order=5):
    nyquist = 0.5 * sampling_frequency
    cutoff_norm = cutoff / nyquist
    b, a = butter(order, cutoff_norm, btype="low", analog=False)
    filtered_data = lfilter(b, a, data)
    return filtered_data


def plot_signal_with_envelope(time, data, envelope, axs, channel):
    """Plot the given signal and its envelope."""
    axs[channel].plot(time, data, label="Filtered Signal")
    axs[channel].plot(time, envelope, label="Envelope (low-pass 5Hz)")
    axs[channel].set_title(f"Channel {channel+1} - {channel_names[channel]}")
    axs[channel].set_xlabel("Time (s)")
    axs[channel].set_ylabel("Amplitude (mV)")
    axs[channel].legend()
