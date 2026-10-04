from pathlib import Path
import argparse
import re
import shutil
import time


# Settings
FRAME_DELAY = 0.10
MOVE_STEP = 3

COLORS = {
    "a": "\033[38;2;95;100;115m",   # outline
    "b": "\033[38;2;255;255;255m",  # body
    "c": "\033[38;2;95;100;115m",   # eyes
}

RESET = "\033[0m"


# Read the SCSS file
folder = Path(__file__).parent
scss_file = folder / "bat.scss"
scss_text = scss_file.read_text(encoding="utf-8")


# Regex patterns for animation frames and pixel coordinates
frame_pattern = re.compile(r"^\s*(\d+(?:\.\d+)?)%\s*\{\s*$")

pixel_pattern = re.compile(r"^\s*(\d+)px\s+(\d+)px\s+\$(\w+)[,;]?\s*$")


# Parse SCSS into: frame percentage -> list of (x, y, color)
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


# Braille characters represent 2 x 4 source pixels
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

# Pre-render both directions
frame_order = sorted(frames.keys())
right_frames = [render_braille(frames[number], flip=True)
    for number in frame_order]

left_frames = [render_braille(frames[number], flip=False)
    for number in frame_order]


def clear_screen():
    print("\033[2J\033[H", end="")

def terminal_size():
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines


def fly():
    '''Normal one-way flight'''
    width, height = terminal_size()
    bat_width = len(right_frames[0][0])
    bat_height = len(right_frames[0])

    y = max(0, (height - bat_height) // 2)
    for step, x in enumerate(
        range(-bat_width, width + 1, MOVE_STEP)):
        clear_screen()

        frame = right_frames[step % len(right_frames)]

        draw_bat(
            frame,
            x,
            y,
            width,
            height
        )

        print(flush=True, end="")
        time.sleep(FRAME_DELAY)



def fly_return():
    '''Fly right, turn around, come back'''
    width, height = terminal_size()
    bat_width = len(right_frames[0][0])
    bat_height = len(right_frames[0])

    y = max(0, (height - bat_height) // 2)
    step = 0

    # Outbound
    for x in range(-bat_width, width + 1, MOVE_STEP):
        clear_screen()

        frame = right_frames[step % len(right_frames)]
        draw_bat(frame, x, y, width, height)

        print(flush=True, end="")

        time.sleep(FRAME_DELAY)
        step += 1

    # Return trip
    for x in range(width,-bat_width - 1, -MOVE_STEP):
        clear_screen()

        frame = left_frames[step % len(left_frames)]
        draw_bat(frame, x, y, width, height)

        print(flush=True, end="")
        time.sleep(FRAME_DELAY)
        step += 1



def perch():
    """Fly in and stay flapping until Ctrl+C"""
    width, height = terminal_size()
    bat_width = len(right_frames[0][0])
    bat_height = len(right_frames[0])

    target_x = max(0,min(width - bat_width, int(width * 0.65)))

    y = max(0, (height - bat_height) // 2)

    step = 0

    # Fly to perch
    for x in range(-bat_width, target_x + 1, MOVE_STEP):
        clear_screen()
        frame = right_frames[step % len(right_frames)]
        draw_bat(frame, x, y, width, height)

        print(flush=True, end="")
        time.sleep(FRAME_DELAY)

        step += 1

    # Stay there
    while True:

        clear_screen()

        frame = right_frames[step % len(right_frames)]

        draw_bat(
            frame,
            target_x,
            y,
            width,
            height
        )

        print(flush=True, end="")
        time.sleep(FRAME_DELAY)

        step += 1



def swarm():
    '''Five smaller bats fly across together'''
    width, height = terminal_size()

    # Render smaller versions of all animation frames
    mini_frames = [render_braille(frames[frame_number],flip=True,shrink=2)
        for frame_number in frame_order]

    bat_width = len(mini_frames[0][0])
    bat_height = len(mini_frames[0])

    # Swarm moves faster than the normal bat
    swarm_move_step = 5

    # Different horizontal starting positions
    starts = [
        -bat_width,
        -bat_width - 16,
        -bat_width - 7,
        -bat_width - 27,
        -bat_width - 12,
    ]

    # Five irregular vertical lanes
    usable_height = max(0, height - bat_height)

    lanes = [
        int(usable_height * 0.08),
        int(usable_height * 0.68),
        int(usable_height * 0.38),
        int(usable_height * 0.85),
        int(usable_height * 0.18),
    ]

    # Prevent all bats from flapping in sync
    frame_offsets = [0, 2, 5, 1, 4]
    step = 0

    while True:
        # Calculate the current x position of every bat
        positions = [start + step * swarm_move_step
            for start in starts]

        # Stop once every bat has completely passed the terminal
        if all(x > width for x in positions):
            break

        clear_screen()

        # Draw all five bats
        for i in range(5):

            x = positions[i]
            y = lanes[i]

            frame_index = (step + frame_offsets[i]) % len(mini_frames)
            frame = mini_frames[frame_index]

            draw_bat(
                frame,
                x,
                y,
                width,
                height
            )
        print(flush=True, end="")

        # Keep the flap timing similar to the normal animation
        time.sleep(FRAME_DELAY)
        step += 1


def dance():
    """Our little batsy dance"""
    width, height = terminal_size()
    bat_width = len(right_frames[0][0])
    bat_height = len(right_frames[0])

    # Position where the dance happens
    center_x = max(0, (width - bat_width) // 2)
    base_y = max(0, (height - bat_height) // 2)

    step = 0
    # 1. Fly in from the left
    for x in range(-bat_width, center_x + 1, MOVE_STEP):
        clear_screen()

        frame = right_frames[step % len(right_frames)]

        draw_bat(
            frame,
            x,
            base_y,
            width,
            height
        )

        print(flush=True, end="")
        time.sleep(FRAME_DELAY)
        step += 1


    # 2. Little side-to-side dance
    dance_positions = [
        0, 2, 4, 6,
        4, 2, 0,
        -2, -4, -6,
        -4, -2, 0
    ]

    # Repeat the dance twice
    for _ in range(2):
        previous_offset = 0
        for dance_step, offset in enumerate(dance_positions):
            x = center_x + offset

            # Small vertical bob
            bob = [0, -1, 0, 1][dance_step % 4]
            y = base_y + bob

            # Face whichever direction the bat is currently moving
            if offset >= previous_offset:
                frame = right_frames[step % len(right_frames)]
            else:
                frame = left_frames[step % len(left_frames)]

            clear_screen()

            draw_bat(
                frame,
                x,
                y,
                width,
                height
            )

            print(flush=True, end="")
            time.sleep(FRAME_DELAY)

            previous_offset = offset
            step += 1

    # 3. Fly away to the right
    for x in range(center_x, width + 1, MOVE_STEP):
        clear_screen()

        frame = right_frames[step % len(right_frames)]

        draw_bat(
            frame,
            x,
            base_y,
            width,
            height
        )

        print(flush=True, end="")
        time.sleep(FRAME_DELAY)
        step += 1        



def main():
    parser = argparse.ArgumentParser( description="Summon a terminal bat.")

    modes = parser.add_mutually_exclusive_group()

    modes.add_argument(
        "--return",
        dest="return_mode",
        action="store_true",
        help="Fly across the terminal and return."
    )

    modes.add_argument(
        "--perch",
        action="store_true",
        help="Fly in and flap until Ctrl+C."
    )

    modes.add_argument(
        "--swarm",
        action="store_true",
        help="Send several smaller bats across."
    )

    modes.add_argument(
        "--dance",
        action="store_true",
        help="Make the bat perform a little dance."
    )
    
    args = parser.parse_args()

    # Temporary screen + hidden cursor
    print("\033[?1049h\033[?25l", end="", flush=True)

    try:
        if args.return_mode:
            fly_return()
        elif args.perch:
            perch()
        elif args.swarm:
            swarm()
        elif args.dance:
            dance()    
        else:
            fly()    

    except KeyboardInterrupt:
        pass

    finally:

        # Restore normal terminal
        print("\033[?25h\033[?1049l",end="",flush=True)


if __name__ == "__main__":
    main()

