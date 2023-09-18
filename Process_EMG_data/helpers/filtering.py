from scipy.signal import butter, lfilter, iirnotch
import numpy as np
import matplotlib.pyplot as plt


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


def notch_mains_interference(data, mains_freq, sampling_frequency, quality_factor=30):
    nyquist = 0.5 * sampling_frequency
    freq = mains_freq / nyquist
    b, a = iirnotch(freq, Q=quality_factor)
    filtered_data = lfilter(b, a, data)
    return filtered_data
