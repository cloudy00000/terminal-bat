# For wsl or linux
# Add this to ~/.bashrc.
# Replace the path below with the path to bat.py on your system.

bat() {
    python3 /path/to/bat_animation/bat.py "$@"
}

# Optional:
# Uncomment this block if you want the bat to fly every time Bash starts.
#bat

# The guard prevents the animation from replaying when ~/.bashrc
# is manually sourced again in the same shell.

# if [[ -z "$BAT_STARTUP_DONE" ]]; then
#     BAT_STARTUP_DONE=1
#     bat
# fi