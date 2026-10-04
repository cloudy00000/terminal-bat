import shutil


COLORS = {
    "a": "\033[38;2;95;100;115m",
    "b": "\033[38;2;255;255;255m",
    "c": "\033[38;2;95;100;115m",
}

RESET = "\033[0m"


BRAILLE_DOTS = {
    (0, 0): 0,
    (0, 1): 1,
    (0, 2): 2,
    (1, 0): 3,
    (1, 1): 4,
    (1, 2): 5,
    (0, 3): 6,
    (1, 3): 7,
}


def render_braille(pixels, flip=False, shrink=1):
    '''Using braille as pixels'''
    # shrink=2 is used for the smaller swarm bats
    reduced = [(x // shrink, y // shrink, color)
        for x, y, color in pixels]

    # Remove unused empty space around the original sprite
    min_x = min(x for x, y, color in reduced)
    min_y = min(y for x, y, color in reduced)

    normalized = [ (x - min_x, y - min_y, color)
        for x, y, color in reduced]

    max_x = max(x for x, y, color in normalized)
    max_y = max(y for x, y, color in normalized)

    pixel_colors = {}
    for x, y, color in normalized:

        # Original sprite faces left, so flipping makes it face right
        if flip:
            x = max_x - x

        position = (x, y)
        previous = pixel_colors.get(position)

        # Preserve useful color information if shrinking merges pixels
        if previous is None or color == "c" or (color == "a" and previous == "b"):
            pixel_colors[position] = color

    rows = []

    for y in range(0, max_y + 1, 4):
        row = []
        for x in range(0, max_x + 1, 2):
            pattern = 0
            cell_colors = []

            for (dx, dy), bit in BRAILLE_DOTS.items():
                position = (x + dx, y + dy)

                if position in pixel_colors:
                    pattern |= 1 << bit
                    cell_colors.append(pixel_colors[position])

            if pattern == 0:
                row.append((" ", None))
                continue

            character = chr(0x2800 + pattern)
            if "c" in cell_colors:
                chosen_color = "c"
            else:
                chosen_color = max(set(cell_colors), key=cell_colors.count)
            row.append((character, chosen_color))
        rows.append(row)

    return rows

def render_frames(frames, flip=False, shrink=1):
    """Render every animation frame in chronological order."""
    return [render_braille(
            frames[frame_number],
            flip=flip,
            shrink=shrink
        )
        for frame_number in sorted(frames)]


def format_cells(cells):
    text = ""
    for character, color in cells:
        if color is None:
            text += character
        else:
            text += COLORS[color] + character + RESET
    return text


def draw_bat(frame, x, y, terminal_width, terminal_height):
    ''' Draw only the visible portion so the bat can enter/exit off-screen'''
    for row_number, row in enumerate(frame):
        screen_y = y + row_number
        if not 0 <= screen_y < terminal_height:
            continue

        start = max(0, -x)
        end = min(len(row), terminal_width - x)

        if start >= end:
            continue

        screen_x = max(0, x)

        visible_cells = row[start:end]

        print(
            f"\033[{screen_y + 1};{screen_x + 1}H"
            f"{format_cells(visible_cells)}",
            end=""
        )


def clear_screen():
    print("\033[2J\033[H", end="")

def terminal_size():
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines


