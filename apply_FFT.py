import numpy as np
import matplotlib.pyplot as plt
from visualize_MAT_file import (
    num_channels_to_plot,
    channel_names,
    data,
    sampling_frequency,
    participant_type,
    yoga_position,
)
from scipy.fftpack import fft


def fft_and_plot(data, sampling_frequency, axs, channel):
    # Perform FFT
    fft_result = fft(data)
    n = len(data)
    T = 1.0 / sampling_frequency
    xf = np.linspace(0.0, 1.0 / (2.0 * T), n // 2)
    axs[channel].plot(xf, 2.0 / n * np.abs(fft_result[: n // 2]))
    axs[channel].set_title(f"FFT - Channel {channel+1} - {channel_names[channel]}")
    axs[channel].set_xlabel("Frequency (Hz)")
    axs[channel].set_ylabel("Magnitude")


fig, axs = plt.subplots(num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot))
fig.suptitle(f"FFT - {participant_type} - {yoga_position}", fontsize=14, weight="bold")

for i in range(num_channels_to_plot):
    fft_and_plot(data[i, :], sampling_frequency, axs, i)

plt.tight_layout()
plt.show()
