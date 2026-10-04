# Add this to your PowerShell $PROFILE.
# Replace the path below with the path to bat.py on your computer.

function bat {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$BatArgs
    )

    python3 "C:\path\to\bat_animation\bat.py" @BatArgs
}

# Optional:
# Uncomment the next line if you want the bat to fly every time PowerShell starts.
# bat