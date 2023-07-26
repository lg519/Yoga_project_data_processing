import numpy as np
import matplotlib.pyplot as plt

from global_variables import (
    num_channels_to_plot,
    channel_names,
    sampling_frequency,
)

from load_data import load_data
from fft_processing import compute_fft, plot_fft
from filtering import (
    find_filter_values,
    butter_bandpass_filter,
    plot_signal_comparison_in_time_domain,
    plot_fft_with_filter_values,
)
from rms_envelope import compute_rms_envelope, rectify_signal, plot_signal_and_envelope


def main():
    # Step 1: Load data
    data, participant_type, yoga_position, filename = load_data()

    # Step 2: Apply FFT and visualize it
    fig1, axs1 = plt.subplots(
        num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot)
    )
    fig1.suptitle(
        f"FFT and Filters - {participant_type} - {yoga_position}",
        fontsize=14,
        weight="bold",
    )

    for i in range(num_channels_to_plot):
        xf, yf = compute_fft(data[i, :], sampling_frequency)
        highcut, lowcut = find_filter_values(yf)
        plot_fft_with_filter_values(xf, yf, highcut, lowcut, axs1, i)

    # Step 3: Apply bandpass filter and visualize results in both time and frequency domain
    fig2, axs2 = plt.subplots(
        num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot)
    )
    fig2.suptitle(
        f"Raw vs Filtered Data - {participant_type} - {yoga_position}",
        fontsize=14,
        weight="bold",
    )

    for i in range(num_channels_to_plot):
        highcut, lowcut = find_filter_values(yf)
        filtered_data = butter_bandpass_filter(
            data[i, :], lowcut, highcut, sampling_frequency
        )
        time = np.arange(0, len(data[i, :])) / sampling_frequency
        plot_signal_comparison_in_time_domain(time, data[i, :], filtered_data, axs2, i)

    # Step 4: Apply RMS envelope to the filtered signal
    fig3, axs3 = plt.subplots(
        num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot)
    )
    fig3.suptitle(
        f"Rectified Signal and RMS Envelope - {participant_type} - {yoga_position}",
        fontsize=14,
        weight="bold",
    )

    for i in range(num_channels_to_plot):
        rectified_signal = rectify_signal(filtered_data)
        rms_envelope = compute_rms_envelope(rectified_signal, window_size=int(50))
        plot_signal_and_envelope(time, rectified_signal, rms_envelope, axs3, i)

    plt.show()


if __name__ == "__main__":
    main()
