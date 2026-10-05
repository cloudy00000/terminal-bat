# Terminal Bat 🦇

A small Python terminal animation that turns a CSS pixel-art bat into an animated Unicode Braille sprite.

The bat can fly across the terminal, return, perch, swarm with friends, or perform a tiny dance.

The project started as an experiment in converting a CSS `box-shadow` pixel animation into something that could be rendered directly in a terminal.

## Features

- Parses the original SCSS animation frames directly
- Converts pixel coordinates into Unicode Braille characters
- Supports ANSI true-color terminal output
- Clips the sprite correctly while entering and leaving the screen
- Automatically adapts to the current terminal size
- Works with PowerShell and Bash on Linux / WSL
- Includes multiple animation modes

## Modes

Run the default animation:

```bash
bat
```

Available modes:

```bash
bat --return
bat --perch
bat --swarm
bat --dance
```

### `bat`

The standard animation. The bat flies in from the left and exits through the right side of the terminal.

### `bat --return`

The bat flies across the terminal, turns around, and flies back.

### `bat --perch`

The bat flies into the terminal and stays there flapping.

Press:

```text
Ctrl+C
```

to release it.

### `bat --swarm`

Sends five smaller bats across the terminal using different heights, starting positions, and animation phases.

### `bat --dance`

The bat flies to the center of the terminal, performs a small side-to-side dance with a vertical bob, and then flies away.

---

## Requirements

- Python 3
- A terminal with ANSI escape-sequence support
- Unicode / Braille character support

The project uses only the Python standard library, so no additional Python packages are required.

---

## Running Directly

Clone the repository and enter the project directory.

Run:

```bash
python3 bat.py
```

Or choose a mode:

```bash
python3 bat.py --dance
python3 bat.py --return
python3 bat.py --perch
python3 bat.py --swarm
```

On systems where Python is invoked using `python` rather than `python3`, use:

```bash
python bat.py
```

---

## Shell Setup

The repository contains example shell snippets inside:

```text
shell/
├── bashrc_snippet.sh
└── powershell_profile.ps1
```

These allow the program to be called simply as:

```bash
bat
```

from anywhere in the terminal.

### PowerShell

Add the function from:

```text
shell/powershell_profile.ps1
```

to your PowerShell profile.

You can open the profile with:

```powershell
notepad $PROFILE
```

or your preferred editor.

Replace the example path with the actual path to `bat.py`:

```powershell
function bat {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$BatArgs
    )

    python3 "C:\path\to\bat_animation\bat.py" @BatArgs
}
```

Reload the profile:

```powershell
. $PROFILE
```

You can now use:

```powershell
bat
bat --dance
bat --return
bat --perch
bat --swarm
```

#### Optional PowerShell Startup Animation

To make the bat fly whenever PowerShell starts, add:

```powershell
bat
```

after the function definition in your profile.

---

### Bash / Linux / WSL

Add the function from:

```text
shell/bashrc_snippet.sh
```

to:

```bash
~/.bashrc
```

Replace the example path with the location of `bat.py`:

```bash
bat() {
    python3 /path/to/bat_animation/bat.py "$@"
}
```

Reload Bash:

```bash
source ~/.bashrc
```

You can then use:

```bash
bat
bat --dance
bat --return
bat --perch
bat --swarm
```

The same function works with Bash on both Linux and WSL.

For WSL, a project stored on the Windows `C:` drive may have a path resembling:

```text
/mnt/c/Users/username/path/to/bat_animation/bat.py
```

#### Optional Bash Startup Animation

To run the animation whenever a new Bash shell starts:

```bash
if [[ -z "$BAT_STARTUP_DONE" ]]; then
    BAT_STARTUP_DONE=1
    bat
fi
```

The guard prevents the animation from running again when `.bashrc` is manually reloaded in the same shell.

---

## Project Structure

```text
bat_animation/
├── bat.py
├── bat.scss
├── modes.py
├── renderer.py
├── scss_parser.py
│
├── legacy_files/
│   ├── bat_simple.py
│   └── entire_bat.py
│
├── shell/
│   ├── bashrc_snippet.sh
│   └── powershell_profile.ps1
│
├── README.md
└── .gitignore
```

### `bat.py`

The main entry point.

It parses command-line arguments, loads the SCSS animation, prepares the rendered frames, selects the requested animation mode, and manages terminal setup and cleanup.

### `scss_parser.py`

Reads `bat.scss` and extracts the pixel coordinates for each animation frame.

### `renderer.py`

Handles conversion from pixels to Unicode Braille, colors, sprite mirroring, terminal clipping, terminal dimensions, and drawing frames.

### `modes.py`

Contains the animation behaviours:

- normal flight
- return flight
- perch
- swarm
- dance

### `legacy_files/`

Contains earlier versions of the program from before the code was split into separate modules.

---

## How It Works

The original animation represents the bat using many CSS `box-shadow` coordinates.

A line such as:

```scss
33px 6px $a,
```

represents one colored pixel.

`scss_parser.py` extracts these coordinates and groups them by animation frame.

The renderer then compresses the source pixels into Unicode Braille cells.

A Braille character can represent a grid of:

```text
2 × 4 pixels
```

which makes it possible to reproduce the pixel-art bat at a practical size inside a terminal.

The resulting frames are drawn using ANSI cursor positioning and color escape sequences.

---

## Credits

The original bat pixel-art animation is based on:

**Bat Pixel Art Animation on one Div**  
by **Yuxin Guo (@timothyguo)**

Original CodePen:

https://codepen.io/timothyguo/pen/jbarzP

The Python parser, Braille renderer, terminal animation system, movement modes, and shell integration were developed as part of this project.

---

## Why?

Because it's October, Halloween is almost here, and the terminal needed a bat.