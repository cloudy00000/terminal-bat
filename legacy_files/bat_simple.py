from pathlib import Path
import re
import time
import shutil


# Read the SCSS file
folder = Path(__file__).parent
scss_file = folder / "bat.scss"
scss_text = scss_file.read_text(encoding="utf-8")


# Regex patterns for animation frames and pixel coordinates
frame_pattern = re.compile(r"^\s*(\d+(?:\.\d+)?)%\s*\{\s*$")

pixel_pattern = re.compile(r"^\s*(\d+)px\s+(\d+)px\s+\$(\w+)[,;]?\s*$")


# Parse SCSS into: frame percentage -> list of (x, y, color) pixels
frames = {}
current_frame = None

for line in scss_text.splitlines():

    frame_match = frame_pattern.match(line)

    if frame_match:
        current_frame = float(frame_match.group(1))
        frames[current_frame] = []
        continue

    pixel_match = pixel_pattern.match(line)

    if pixel_match and current_frame is not None:
        x = int(pixel_match.group(1))
        y = int(pixel_match.group(2))
        color = pixel_match.group(3)

        frames[current_frame].append((x, y, color))


def render_braille(pixels):

    max_x = max(x for x, y, color in pixels)
    max_y = max(y for x, y, color in pixels)

    # Terminal-friendly versions of the original SCSS colors
    colors ={
    "a": "\033[38;2;95;100;115m",    #outline
    "b": "\033[38;2;255;255;255m",   #body
    #"c": "\033[38;2;95;100;115m",  
    "c": "\033[38;2;75;80;95m"   # eyes 
}

    reset = "\033[0m"

    # Mirror the bat and retain each pixel's color
    pixel_colors = {(max_x - x, y): color
        for x, y, color in pixels}

    # Braille characters represent a 2 x 4 pixel block
    braille_dots = {
        (0, 0): 0,
        (0, 1): 1,
        (0, 2): 2,
        (1, 0): 3,
        (1, 1): 4,
        (1, 2): 5,
        (0, 3): 6,
        (1, 3): 7,
    }

    rows = []

    for y in range(0, max_y + 1, 4):
        row = ""
        for x in range(0, max_x + 1, 2):
            pattern = 0
            cell_colors = []

            for (dx, dy), bit in braille_dots.items():
                position = (x + dx, y + dy)

                if position in pixel_colors:
                    pattern |= 1 << bit
                    cell_colors.append(pixel_colors[position])

            character = chr(0x2800 + pattern)

            if cell_colors:
                # Preserve eye pixels if present
                if "c" in cell_colors:
                    chosen_color = "c"
                # Otherwise use the dominant color in this Braille cell
                else:
                    chosen_color = max(
                        set(cell_colors),
                        key=cell_colors.count
                    )
                row += colors[chosen_color] + character + reset

            else:
                row += character
        rows.append(row)

    return "\n".join(rows)


# Pre-render all frames in animation order
frame_order = sorted(frames.keys())
rendered_frames = []

for frame_number in frame_order:
    picture = render_braille(frames[frame_number])
    rendered_frames.append(picture)


# Get terminal width
terminal_width = shutil.get_terminal_size().columns


# Remove invisible ANSI color codes when measuring visible width
ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")

bat_width = max(
    len(ansi_pattern.sub("", line))
    for line in rendered_frames[0].splitlines()
)


# Enter alternate screen and hide cursor
print("\033[?1049h\033[?25l", end="")

try:

    # Move 2 terminal columns per animation frame
    for step, x_position in enumerate(
        range(0, terminal_width - bat_width, 3)):

        # Cycle through the wing frames
        frame_index = step % len(rendered_frames)
        picture = rendered_frames[frame_index]

        # Shift the whole bat horizontally
        shifted_picture = "\n".join( " " * x_position + line
            for line in picture.splitlines())

        # Clear temporary screen and redraw
        print("\033[2J\033[H", end="")
        print(shifted_picture)

        # Controls animation speed
        time.sleep(0.11)

finally:

    # Restore cursor and original terminal screen
    print("\033[?25h\033[?1049l", end="")