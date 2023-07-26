from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt

from global_variables import (
    num_channels_to_plot,
    channel_names,
    sampling_frequency,
)
from load_data import load_data


def compute_fft(data, sampling_frequency):
    # Perform FFT
    fft_result = fft(data)
    n = len(data)
    T = 1.0 / sampling_frequency
    xf = np.linspace(0.0, 1.0 / (2.0 * T), n // 2)
    yf = 2.0 / n * np.abs(fft_result[: n // 2])
    return xf, yf


def plot_fft(xf, yf, axs, channel):
    axs[channel].plot(xf, yf)
    axs[channel].set_title(f"FFT - Channel {channel+1} - {channel_names[channel]}")
    axs[channel].set_xlabel("Frequency (Hz)")
    axs[channel].set_ylabel("Magnitude")


if __name__ == "__main__":
    data, participant_type, yoga_position, filename = load_data()
    fig, axs = plt.subplots(
        num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot)
    )
    fig.suptitle(
        f"FFT - {participant_type} - {yoga_position}", fontsize=14, weight="bold"
    )

    for i in range(num_channels_to_plot):
        xf, yf = compute_fft(data[i, :], sampling_frequency)
        plot_fft(xf, yf, axs, i)

    plt.tight_layout()
    plt.show()
