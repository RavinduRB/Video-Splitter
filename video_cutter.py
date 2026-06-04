import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import re
from pathlib import Path


class VideoSplitterApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Video Splitter")
        self.root.geometry("850x700")

        self.video_path = tk.StringVar()
        self.split_mode = tk.StringVar(value="seconds")
        self.split_value = tk.StringVar(value="30")

        self.create_ui()

    def create_ui(self):

        title = tk.Label(
            self.root,
            text="Advanced Video Splitter",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=10)

        # File Selection
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill="x", padx=15)

        tk.Entry(
            file_frame,
            textvariable=self.video_path,
            width=80
        ).pack(side="left", padx=5)

        tk.Button(
            file_frame,
            text="Browse",
            command=self.browse_file
        ).pack(side="left")

        # Options
        options = tk.LabelFrame(
            self.root,
            text="Split Options",
            padx=10,
            pady=10
        )
        options.pack(fill="x", padx=15, pady=15)

        tk.Radiobutton(
            options,
            text="Split by Seconds",
            variable=self.split_mode,
            value="seconds"
        ).pack(anchor="w")

        tk.Radiobutton(
            options,
            text="Split into Number of Parts",
            variable=self.split_mode,
            value="parts"
        ).pack(anchor="w")

        tk.Radiobutton(
            options,
            text="Custom Time Ranges",
            variable=self.split_mode,
            value="custom"
        ).pack(anchor="w")

        tk.Label(
            options,
            text="Seconds / Parts Value:"
        ).pack(anchor="w", pady=(10, 0))

        tk.Entry(
            options,
            textvariable=self.split_value,
            width=15
        ).pack(anchor="w")

        tk.Label(
            options,
            text="Custom Ranges (one per line):"
        ).pack(anchor="w", pady=(15, 0))

        self.custom_text = tk.Text(
            options,
            height=10
        )
        self.custom_text.pack(fill="x", pady=5)

        self.custom_text.insert(
            "1.0",
            "00:00:00-00:00:30\n"
            "00:00:30-00:01:00\n"
        )

        self.progress = ttk.Progressbar(
            self.root,
            mode="indeterminate",
            length=700
        )
        self.progress.pack(pady=10)

        self.start_btn = tk.Button(
            self.root,
            text="Start Splitting",
            bg="green",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=self.start_thread
        )
        self.start_btn.pack(pady=5)

        log_frame = tk.LabelFrame(
            self.root,
            text="Log"
        )
        log_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.log_box = tk.Text(
            log_frame,
            wrap="word"
        )
        self.log_box.pack(
            fill="both",
            expand=True
        )

    def browse_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                (
                    "Video Files",
                    "*.mp4 *.mkv *.avi *.mov *.webm *.flv"
                )
            ]
        )

        if path:
            self.video_path.set(path)

    def log(self, text):
        self.root.after(
            0,
            lambda: self._append_log(text)
        )

    def _append_log(self, text):
        self.log_box.insert(
            tk.END,
            text + "\n"
        )
        self.log_box.see(tk.END)

    def get_duration(self, file_path):

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return float(result.stdout.strip())

    def validate_time(self, time_str):

        pattern = r"^\d{2}:\d{2}:\d{2}$"
        return re.match(pattern, time_str)

    def split_custom_ranges(
        self,
        file_path,
        output_folder
    ):

        lines = self.custom_text.get(
            "1.0",
            tk.END
        ).strip().splitlines()

        source = Path(file_path)

        if not lines:
            raise ValueError(
                "No custom ranges found."
            )

        for idx, line in enumerate(
            lines,
            start=1
        ):

            line = line.strip()

            if not line:
                continue

            if "-" not in line:
                raise ValueError(
                    f"Invalid format:\n{line}"
                )

            start_time, end_time = line.split("-")

            start_time = start_time.strip()
            end_time = end_time.strip()

            if (
                not self.validate_time(start_time)
                or
                not self.validate_time(end_time)
            ):
                raise ValueError(
                    f"Invalid time:\n{line}"
                )

            output_file = (
                output_folder /
                f"{source.stem}_part_{idx:03d}"
                f"{source.suffix}"
            )

            self.log(
                f"Creating Part {idx}"
            )

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                file_path,
                "-ss",
                start_time,
                "-to",
                end_time,
                "-c",
                "copy",
                str(output_file)
            ]

            subprocess.run(cmd)

        self.log(
            "Custom split completed."
        )

    def split_video(self):

        try:

            file_path = self.video_path.get()

            if not file_path:
                raise ValueError(
                    "Please select a video."
                )

            source = Path(file_path)

            output_folder = (
                source.parent /
                f"{source.stem}_parts"
            )

            output_folder.mkdir(
                exist_ok=True
            )

            mode = self.split_mode.get()

            self.log(
                "Reading video info..."
            )

            duration = self.get_duration(
                file_path
            )

            self.log(
                f"Duration: {duration:.2f}s"
            )

            if mode == "custom":

                self.split_custom_ranges(
                    file_path,
                    output_folder
                )

            else:

                value = int(
                    self.split_value.get()
                )

                if value <= 0:
                    raise ValueError(
                        "Value must be greater than zero."
                    )

                if mode == "seconds":
                    segment_time = value

                elif mode == "parts":
                    segment_time = (
                        duration / value
                    )

                else:
                    raise ValueError(
                        "Invalid mode."
                    )

                self.log(
                    f"Segment length: "
                    f"{segment_time:.2f}s"
                )

                output_pattern = str(
                    output_folder /
                    f"{source.stem}_part_%03d"
                    f"{source.suffix}"
                )

                cmd = [
                    "ffmpeg",
                    "-i",
                    file_path,
                    "-c",
                    "copy",
                    "-map",
                    "0",
                    "-f",
                    "segment",
                    "-segment_time",
                    str(segment_time),
                    "-reset_timestamps",
                    "1",
                    output_pattern
                ]

                self.log(
                    "Splitting video..."
                )

                subprocess.run(cmd)

                self.log(
                    "Finished successfully."
                )

            messagebox.showinfo(
                "Completed",
                f"Saved to:\n{output_folder}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

        finally:

            self.root.after(
                0,
                self.progress.stop
            )

            self.root.after(
                0,
                lambda: self.start_btn.config(
                    state="normal"
                )
            )

    def start_thread(self):

        self.start_btn.config(
            state="disabled"
        )

        self.progress.start()

        threading.Thread(
            target=self.split_video,
            daemon=True
        ).start()


if __name__ == "__main__":

    root = tk.Tk()

    app = VideoSplitterApp(root)

    root.mainloop()