import math


def nice_axis_scale(values, target_intervals=6, padding=1.05):
    """Return a rounded zero-based maximum and tick step for positive values."""
    finite_values = [
        float(value) for value in values if math.isfinite(float(value))
    ]
    maximum = max(finite_values, default=0.0)
    if maximum <= 0:
        return 1.0, 0.2

    rough_step = maximum * padding / target_intervals
    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized = rough_step / magnitude
    multiplier = next(
        candidate for candidate in (1, 2, 2.5, 5, 10)
        if normalized <= candidate
    )
    step = multiplier * magnitude
    axis_maximum = math.ceil(maximum * padding / step) * step
    return axis_maximum, step


def compact_number(value):
    """Format axis values compactly using Dutch decimal punctuation."""
    if value == 0:
        return "0"
    if abs(value) >= 1_000_000:
        formatted = f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return formatted.replace(".", ",") + "M"
    if abs(value) >= 1_000:
        formatted = f"{value / 1_000:.1f}".rstrip("0").rstrip(".")
        return formatted.replace(".", ",") + "k"
    return f"{value:g}".replace(".", ",")


def confirmed_dominance(candidates, required_observations=2):
    """Only confirm a candidate after consecutive qualifying observations."""
    result = []
    previous = None
    streak = 0
    for candidate in candidates:
        if candidate and candidate == previous:
            streak += 1
        elif candidate:
            previous = candidate
            streak = 1
        else:
            previous = None
            streak = 0
        result.append(candidate if streak >= required_observations else "")
    return result
