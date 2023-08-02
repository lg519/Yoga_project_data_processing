from scipy.signal import butter, lfilter
import numpy as np


def butter_bandpass_filter(data, lowcut, highcut, sampling_frequency, order=5):
    nyquist = 0.5 * sampling_frequency
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    filtered_data = lfilter(b, a, data)
    return filtered_data


def butter_lowpass_filter(data, cutoff, sampling_frequency, order=5):
    nyquist = 0.5 * sampling_frequency
    cutoff_norm = cutoff / nyquist
    b, a = butter(order, cutoff_norm, btype="low", analog=False)
    filtered_data = lfilter(b, a, data)
    return filtered_data
