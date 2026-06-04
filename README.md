# Video Splitter

A simple desktop application for splitting video files using `ffmpeg` and a Tkinter GUI.

## Features

- Select a video file from disk.
- Split by fixed segment length in seconds.
- Split into a set number of parts.
- Split by custom time ranges.
- Outputs split files into a folder next to the source video.

## Requirements

- Python 3.8+
- `tkinter` (often included with Python on Windows)
- `ffmpeg` installed and available on the system PATH

## Setup

1. Install Python if it is not already installed.
2. Install `ffmpeg` and ensure the `ffmpeg` and `ffprobe` commands work from a terminal.("pip install tkinterdnd2")
3. Optionally, install `tkinter` if your Python installation does not include it. ("pip install tk")

## Usage

1. Open a terminal in the project folder.
2. Run:

```bash
python video_cutter.py
```

3. Use the GUI to:
   - browse for a video file
   - choose a split mode
   - enter a value or custom ranges
   - start splitting

## Notes

- Split output is saved in a new folder named after the source file with `_parts` appended.
- Custom ranges should be entered in `HH:MM:SS-HH:MM:SS` format, one range per line.
