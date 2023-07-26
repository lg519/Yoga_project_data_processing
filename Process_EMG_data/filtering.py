from scipy.signal import butter, lfilter
import numpy as np
import matplotlib.pyplot as plt

from global_variables import (
    num_channels_to_plot,
    channel_names,
    sampling_frequency,
)
from load_data import load_data
from fft_processing import compute_fft, plot_fft


def find_filter_values(fft_data, threshold=0.1):
    # Find where the FFT magnitude drops below the threshold
    # high_pass = np.argmax(np.abs(fft_data) > threshold)
    # low_pass = len(fft_data) - np.argmax(np.abs(fft_data[::-1]) > threshold)
    high_pass = 450
    low_pass = 20
    return high_pass, low_pass


def butter_bandpass_filter(data, lowcut, highcut, sampling_frequency, order=5):
    nyquist = 0.5 * sampling_frequency
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    filtered_data = lfilter(b, a, data)
    return filtered_data


def plot_signal_comparison_in_time_domain(time, data, filtered_data, axs, channel):
    axs[channel].plot(time, data, label="Raw data")
    axs[channel].plot(time, filtered_data, label="Filtered data")
    axs[channel].set_title(f"Channel {channel+1} - {channel_names[channel]}")
    axs[channel].set_xlabel("Time (s)")
    axs[channel].set_ylabel("Amplitude (mV)")
    axs[channel].legend()


def plot_fft_with_filter_values(xf, yf, highcut, lowcut, axs, channel):
    # Plot the original FFT
    plot_fft(xf, yf, axs, channel)

    # Add vertical lines for the cutoff frequencies
    axs[channel].axvline(x=highcut, color="r", linestyle="--")
    axs[channel].axvline(x=lowcut, color="r", linestyle="--")
    axs[channel].legend(["FFT", "Cutoff Frequencies"])


if __name__ == "__main__":
    data, participant_type, yoga_position, filename = load_data()

    fig1, axs1 = plt.subplots(
        num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot)
    )
    fig1.suptitle(
        f"FFT and Filters - {participant_type} - {yoga_position}",
        fontsize=14,
        weight="bold",
    )

    fig2, axs2 = plt.subplots(
        num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot)
    )
    fig2.suptitle(
        f"Raw vs Filtered Data - {participant_type} - {yoga_position}",
        fontsize=14,
        weight="bold",
    )

    for i in range(num_channels_to_plot):
        xf, yf = compute_fft(data[i, :], sampling_frequency)
        highcut, lowcut = find_filter_values(yf)
        plot_fft_with_filter_values(xf, yf, highcut, lowcut, axs1, i)

        filtered_data = butter_bandpass_filter(
            data[i, :], lowcut, highcut, sampling_frequency
        )
        time = np.arange(0, len(data[i, :])) / sampling_frequency
        plot_signal_comparison_in_time_domain(time, data[i, :], filtered_data, axs2, i)

    plt.show()
