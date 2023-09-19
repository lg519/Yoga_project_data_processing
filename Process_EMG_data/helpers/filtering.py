from scipy.signal import butter, lfilter, iirnotch
import numpy as np
import matplotlib.pyplot as plt


def butter_bandpass_filter(data, lowcut, highcut, sampling_frequency, order=5):
    """
    Apply a bandpass filter to the given data using the Butterworth filter design.

    Args:
        data (ndarray): Input data to be filtered.
        lowcut (float): Low frequency (in Hz) edge of the passband.
        highcut (float): High frequency (in Hz) edge of the passband.
        sampling_frequency (float): Sampling frequency of the data (in Hz).
        order (int, optional): Order of the filter. Default is 5.

    Returns:
        ndarray: Filtered data.
    """
    nyquist = 0.5 * sampling_frequency
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    filtered_data = lfilter(b, a, data)
    return filtered_data


def butter_lowpass_filter(data, cutoff, sampling_frequency, order=5):
    """
    Apply a lowpass filter to the given data using the Butterworth filter design.

    Args:
        data (ndarray): Input data to be filtered.
        cutoff (float): Frequency (in Hz) below which signal remains unaffected.
        sampling_frequency (float): Sampling frequency of the data (in Hz).
        order (int, optional): Order of the filter. Default is 5.

    Returns:
        ndarray: Filtered data.
    """
    nyquist = 0.5 * sampling_frequency
    cutoff_norm = cutoff / nyquist
    b, a = butter(order, cutoff_norm, btype="low", analog=False)
    filtered_data = lfilter(b, a, data)
    return filtered_data


def notch_mains_interference(data, mains_freq, sampling_frequency, quality_factor=30):
    """
    Apply a notch filter to remove mains interference from the given data.

    Args:
        data (ndarray): Input data to be filtered.
        mains_freq (float): Frequency (in Hz) of the mains interference, usually 50 or 60 Hz.
        sampling_frequency (float): Sampling frequency of the data (in Hz).
        quality_factor (float, optional): Quality factor for the notch filter, determining the bandwidth of the notch. Default is 30.

    Returns:
        ndarray: Filtered data with the mains interference removed.
    """
    nyquist = 0.5 * sampling_frequency
    freq = mains_freq / nyquist
    b, a = iirnotch(freq, Q=quality_factor)
    filtered_data = lfilter(b, a, data)
    return filtered_data
