import numpy as np


def generate_signal_function(spec, days, slots):
    """
    Generate a work/rest signal array based on specification.

    Parameters:
      spec (dict): Dictionary with keys:
        - type: 'day', 'night', or 'shift_weekend'
        - start, end: integer indices for start/end when applicable
      days (int): Number of days
      slots (int): Time slots per day (e.g., hours)

    Returns:
      np.ndarray: 1D array of length days*slots with values:
        1 for active, -1 for rest, 0 for neutral
    """
    total = days * slots
    sig = np.zeros(total, dtype=int)

    if spec['type'] == 'day':
        sig.fill(-1)
        for d in range(days):
            start = d * slots + spec['start']
            end = d * slots + spec['end'] + 1
            sig[start:end] = 1

    elif spec['type'] == 'night':
        sig.fill(-1)
        for d in range(days):
            base = d * slots
            # evening
            sig[base + spec['start']: base + slots] = 1
            # early morning next day
            next_end = spec['end']
            sig[base: base + next_end] = 1

    elif spec['type'] == 'shift_weekend':
        for d in range(days):
            base = d * slots
            weekday = d % 7
            if weekday < 3:
                sig[base + 6: base + 12] = 1
                sig[base: base + 6] = -1
                sig[base + 12: base + 24] = -1
            elif weekday < 5:
                sig[base + 12: base + 18] = 1
                sig[base: base + 12] = -1
                sig[base + 18: base + 24] = -1
            else:
                sig[base: base + 24] = 0

    else:
        raise ValueError(f"Unknown type: {spec['type']}")

    return sig