def filter_and_plot(data, high_pass, low_pass, sampling_frequency, axs, channel):
    # Create filters
    nyquist = 0.5 * sampling_frequency
    high = high_pass / nyquist
    low = low_pass / nyquist
    b, a = butter(1, [high, low], btype="band")

    # Apply filters
    filtered_data = filtfilt(b, a, data)

    # Plot filtered data
    axs[channel].plot(filtered_data)
    axs[channel].set_title(f"Filtered - Channel {channel+1} - {channel_names[channel]}")
    axs[channel].set_xlabel("Time (s)")
    axs[channel].set_ylabel("Amplitude")


fig, axs = plt.subplots(num_channels_to_plot, 1, figsize=(10, 2 * num_channels_to_plot))
fig.suptitle(
    f"Filtered - {participant_type} - {yoga_position}", fontsize=14, weight="bold"
)

for i in range(num_channels_to_plot):
    fft_result = fft(data[i, :])
    high_pass, low_pass = find_filter_values(fft_result)
    filter_and_plot(data[i, :], high_pass, low_pass, sampling_frequency, axs, i)

plt.tight_layout()
plt.show()
