from pathlib import Path
import re

# Regex patterns for animation frames and pixel coordinates
FRAME_PATTERN = re.compile(r"^\s*(\d+(?:\.\d+)?)%\s*\{\s*$")
PIXEL_PATTERN = re.compile(r"^\s*(\d+)px\s+(\d+)px\s+\$(\w+)[,;]?\s*$")

def load_frames(scss_file):
    """Reading the scss file and mke the coordinates"""
    scss_text = Path(scss_file).read_text(encoding="utf-8")

    frames = {}
    current_frame = None

    for line in scss_text.splitlines():

        frame_match = FRAME_PATTERN.match(line)

        if frame_match:
            current_frame = float(frame_match.group(1))
            frames[current_frame] = []
            continue

        pixel_match = PIXEL_PATTERN.match(line)

        if pixel_match and current_frame is not None:
            x = int(pixel_match.group(1))
            y = int(pixel_match.group(2))
            color = pixel_match.group(3)

            frames[current_frame].append((x, y, color))

    return frames