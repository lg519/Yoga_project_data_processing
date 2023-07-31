from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import numpy as np

from global_variables import (
    num_channels_to_plot,
    channel_names,
    sampling_frequency,
)


def rectify_signal(signal):
    """Rectify the given signal (take absolute value)."""
    return np.abs(signal)


def plot_signal_with_envelope(time, data, envelope, axs, channel):
    """Plot the given signal and its envelope."""
    axs[channel].plot(time, data, label="Rectified Signal")
    axs[channel].plot(time, envelope, label="Envelope (low-pass 5Hz)")
    axs[channel].set_title(f"Channel {channel+1} - {channel_names[channel]}")
    axs[channel].set_xlabel("Time (s)")
    axs[channel].set_ylabel("Amplitude (mV)")
    axs[channel].legend()
