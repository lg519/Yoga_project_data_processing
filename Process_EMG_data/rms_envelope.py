import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

from global_variables import (
    num_channels_to_plot,
    channel_names,
    sampling_frequency,
)
from load_data import load_data


def compute_rms_envelope(signal, window_size):
    """Compute the RMS envelope of the given signal."""
    print(f"Computing RMS envelope with window size {window_size}")
    print(f"Signal length: {len(signal)}")
    print(f"signal: {signal}")
    signal_squared = np.power(signal, 2)
    window = np.ones(window_size) / float(window_size)
    rms_envelope = np.sqrt(np.convolve(signal_squared, window, mode="valid"))
    return rms_envelope


def rectify_signal(signal):
    """Rectify the given signal (take absolute value)."""
    return np.abs(signal)


def plot_signal_and_envelope(time, signal, rms_envelope, axs, channel):
    """Plot the given signal and its RMS envelope."""
    axs[channel].plot(time, signal, label="Rectified Signal")
    envelope_time = time[: len(rms_envelope)]
    axs[channel].plot(envelope_time, rms_envelope, label="RMS Envelope")
    axs[channel].set_title(f"Channel {channel+1} - {channel_names[channel]}")
    axs[channel].set_xlabel("Time (s)")
    axs[channel].set_ylabel("Amplitude (mV)")
    axs[channel].legend()


if __name__ == "__main__":
    data, participant_type, yoga_position, filename = load_data()
    fig, axs = plt.subplots(
        num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot)
    )
    fig.suptitle(
        f"Rectified Signal and RMS Envelope - {participant_type} - {yoga_position}",
        fontsize=14,
        weight="bold",
    )

    for i in range(num_channels_to_plot):
        rectified_signal = rectify_signal(data[i, :])
        rms_envelope = compute_rms_envelope(
            rectified_signal, window_size=int(0.01 * sampling_frequency)
        )
        time = np.arange(0, len(rectified_signal)) / sampling_frequency
        plot_signal_and_envelope(time, rectified_signal, rms_envelope, axs, i)

    plt.tight_layout()
    plt.show()
