from pathlib import Path
import argparse

from scss_parser import load_frames
from renderer import render_frames
from modes import (dance, fly, fly_return, perch, swarm,)


def main():
    parser = argparse.ArgumentParser(
        description="Summon a terminal bat.")

    modes = parser.add_mutually_exclusive_group()

    modes.add_argument("--return", dest="return_mode", action="store_true")

    modes.add_argument("--perch", action="store_true")

    modes.add_argument("--swarm", action="store_true")

    modes.add_argument("--dance", action="store_true")

    args = parser.parse_args()


    # Find bat.scss relative to bat.py
    folder = Path(__file__).parent
    scss_file = folder / "bat.scss"

    frames = load_frames(scss_file)

    # Pre-render normal bats facing both directions
    right_frames = render_frames(frames, flip=True)

    left_frames = render_frames(frames, flip=False)


    # Enter alternate screen and hide cursor
    print("\033[?1049h\033[?25l", end="", flush=True)

    try:
        if args.return_mode:
            fly_return(right_frames, left_frames)

        elif args.perch: 
            perch(right_frames)

        elif args.swarm:
            swarm(frames)

        elif args.dance:
            dance(right_frames, left_frames)

        else:
            fly(right_frames)

    except KeyboardInterrupt:
        pass

    finally:
        # Restore cursor and original terminal
        print("\033[?25h\033[?1049l", end="", flush=True)


if __name__ == "__main__":
    main()