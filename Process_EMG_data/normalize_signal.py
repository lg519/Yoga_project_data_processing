def normalize_signal(envelope, mvc):
    """
    Normalize a signal using MVC (Maximum Voluntary Contraction).

    Args:
        envelope (np.array): The signal envelope.
        mvc (float): The MVC value.

    Returns:
        np.array: The normalized signal.
    """
    # print envelope shape
    print(f"envelope shape: {envelope.shape}")
    # print mvc
    print(f"mvc: {mvc}")
    return envelope / mvc
