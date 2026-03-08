import re

from .models import TargetReport

_MESSAGE_PATTERN = re.compile(
    r"^\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(.+?)\s*$"
)


def parse_target_message(text: str) -> TargetReport:
    match = _MESSAGE_PATTERN.match(text)
    if not match:
        raise ValueError(
            "Invalid format. Expected: <latitude> <longitude> <description>"
        )

    lat = float(match.group(1))
    lon = float(match.group(2))
    description = match.group(3)

    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")

    return TargetReport(latitude=lat, longitude=lon, description=description)
