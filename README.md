# MapuAlpha
MapuAlpha is a lightweight Dots and Boxes AI for a 5×5 board, implemented in C++17 and Python 3.10.
It uses chain analysis and minimax with alpha-beta pruning to explore the game tree.

This model was developed for the 2025 Hanyang AI Challenge (HAIC), where it achieved 1st place, winning 219 out of 220 matches. The agent plays under a 24-second total time limit per game.

# Running
A pre-compiled build is available in the **release** directory.

## Windows

Download the `MapuAlpha-0.x.0-windows-x86_64.zip` file and extract it.

Inside the extracted folder, run:

    MapuAlpha.exe

No additional setup is required.  
If Windows shows a security warning, click **More info → Run anyway** to proceed.

## Linux

Download the `MapuAlpha-0.x.0-linux-x86_64.tar.gz` archive and extract it:

    tar -xzvf MapuAlpha-0.x.0-linux-x86_64.tar.gz
    cd MapuAlpha-0.x.0-linux-x86_64

Make the binary executable (usually already set, but safe to ensure):

    chmod +x MapuAlpha

Run the program:

    ./MapuAlpha

If you see a "Permission denied" error, it means the file is not executable.
Run the chmod command above again.

### Dependencies

The GUI requires the Tkinter runtime.
If your system does not have it installed, install it with:

**Ubuntu / Debian**

    sudo apt install python3-tk

**Fedora**

    sudo dnf install python3-tkinter

**Arch Linux**

    sudo pacman -S tk

MapuAlpha does not require Python to be installed system-wide,
but the Tk runtime must be present for the GUI.

