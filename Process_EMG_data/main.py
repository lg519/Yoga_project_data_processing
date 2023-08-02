# import numpy as np
# import matplotlib.pyplot as plt

# from Process_EMG_data.amplifier_config import (
#     num_channels,
#     channel_names,
#     sampling_frequency,
# )

# from load_data import load_data
# from fft_processing import compute_fft, plot_fft
# from filtering import (
#     find_filter_values,
#     butter_bandpass_filter,
#     plot_raw_signal_vs_filtered_signal,
#     plot_fft_with_filter_values,
# )
# from rectify_signal import (
#     butter_lowpass_filter,
#     plot_rectified_signal_vs_envelope,
# )
# from mvc_processing import (
#     calculate_mvc_for_each_channel,
#     choose_mvc_file,
#     calculate_mvc,
# )


# def plot_normalized_signal(time, normalized_signal, axs, channel_index):
#     """
#     Plot the normalized signal.

#     Args:
#         time (np.array): Time vector.
#         normalized_signal (np.array): The normalized signal to plot.
#         axs (matplotlib.axes.Axes): The Axes instance to plot on.
#         channel_index (int): The index of the current channel.

#     """
#     axs[channel_index].plot(time, normalized_signal)
#     axs[channel_index].set_xlabel("Time (s)")
#     axs[channel_index].set_ylabel("Normalized Amplitude")
#     axs[channel_index].set_title(
#         f"Channel {channel_index + 1} - {channel_names[channel_index]} - Normalized Signal"
#     )


# def main():
#     # Step 1: Load data
#     data, participant_type, yoga_position, filename = load_data()

#     # Step 1.5: Choose MVC file and calculate MVC
#     mvc = calculate_mvc_for_each_channel()
#     print(f"mvc: {mvc}")

#     # Step 2: Apply FFT and visualize it
#     fig1, axs1 = plt.subplots(num_channels, 1, figsize=(10, 2 * num_channels))
#     fig1.suptitle(
#         f"FFT and Filters - {participant_type} - {yoga_position}",
#         fontsize=14,
#         weight="bold",
#     )

#     for i in range(num_channels):
#         xf, yf = compute_fft(data[i, :], sampling_frequency)
#         highcut, lowcut = find_filter_values(yf)
#         plot_fft_with_filter_values(xf, yf, highcut, lowcut, axs1, i)

#     # Step 3: Apply bandpass filter and visualize results in both time and frequency domain
#     fig2, axs2 = plt.subplots(num_channels, 1, figsize=(10, 2 * num_channels))
#     fig2.suptitle(
#         f"Raw vs Filtered Data - {participant_type} - {yoga_position}",
#         fontsize=14,
#         weight="bold",
#     )

#     # Initialize an array to store filtered data for each channel
#     filtered_data = np.zeros((num_channels, len(data[0, :])))

#     for i in range(num_channels):
#         highcut, lowcut = find_filter_values(yf)
#         filtered_channel_data = butter_bandpass_filter(
#             data[i, :], lowcut, highcut, sampling_frequency
#         )
#         filtered_data[i, :] = filtered_channel_data
#         time = np.arange(0, len(data[i, :])) / sampling_frequency
#         plot_raw_signal_vs_filtered_signal(
#             time, data[i, :], filtered_channel_data, axs2, i
#         )

#     # Step 4: Rectify the filtered signal and apply low-pass filter to extract the envelope
#     fig3, axs3 = plt.subplots(num_channels, 1, figsize=(10, 2 * num_channels))
#     fig3.suptitle(
#         f"Filtered Signal and Envelope - {participant_type} - {yoga_position}",
#         fontsize=14,
#         weight="bold",
#     )

#     # Initialize an array to store envelopes
#     envelopes = np.zeros((num_channels, len(filtered_channel_data)))

#     for i in range(num_channels):
#         rectified_data = rectify_signal(filtered_data[i, :])
#         envelope = butter_lowpass_filter(
#             rectified_data, cutoff=5, sampling_frequency=sampling_frequency
#         )
#         # Store the generated envelope in the array
#         envelopes[i, :] = envelope

#         plot_rectified_signal_vs_envelope(time, rectified_data, envelope, axs3, i)

#     # Step 5: Normalize using MVC and visualize normalized signal
#     fig4, axs4 = plt.subplots(num_channels, 1, figsize=(10, 2 * num_channels))
#     fig4.suptitle(
#         f"Normalized Signal - {participant_type} - {yoga_position}",
#         fontsize=14,
#         weight="bold",
#     )

#     for i in range(num_channels):
#         normalized_signal = envelopes[i, :] / mvc[i]
#         plot_normalized_signal(time, normalized_signal, axs4, i)

#     plt.show()


# if __name__ == "__main__":
#     main()
