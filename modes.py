import time
from renderer import (clear_screen, draw_bat, render_frames, terminal_size,)


FRAME_DELAY = 0.10
MOVE_STEP = 3
SWARM_MOVE_STEP = 5


def fly(right_frames):
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



def fly_return(right_frames, left_frames):
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



def perch(right_frames):
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



def swarm(frames):
    '''Five smaller bats fly across together'''
    width, height = terminal_size()

    # Render smaller versions of all animation frames
    mini_frames = render_frames(
    frames,
    flip=True,
    shrink=2
)

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


def dance(right_frames, left_frames):
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
