from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import numpy as np


def rectify_signal(signal):
    """Rectify the given signal (take absolute value)."""
    return np.abs(signal)
