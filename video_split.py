import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar
from moviepy.video.io.VideoFileClip import VideoFileClip
import logging


class LoggingWidgetHandler(logging.Handler):
    """A logging handler that writes to a widget in the GUI."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.insert(tk.END, msg + '\n')
        self.widget.see(tk.END)


def browse_input_file():
    """Open a file dialog to select the input video file."""
    filename = filedialog.askopenfilename()
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, filename)


def browse_output_dir():
    """Open a file dialog to select the output directory."""
    dirname = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, dirname)


def split_video():
    """Split the input video into 6-second clips."""
    # get the input video filename, output directory, and clip duration from the user
    input_file = input_file_entry.get()
    output_dir = output_dir_entry.get()
    clip_duration = int(duration_entry.get())

    # set up logging to the widget
    logging_widget.config(state=tk.NORMAL)
    logging_widget.delete('1.0', tk.END)
    logging_handler = LoggingWidgetHandler(logging_widget)
    logging_handler.setLevel(logging.INFO)
    logging.getLogger('moviepy').addHandler(logging_handler)

    # load the input video
    video = VideoFileClip(input_file)

    # calculate the number of clips
    num_clips = int(video.duration // clip_duration) + 1

    # initialize the progress bar
    progress_bar['value'] = 0
    progress_bar['maximum'] = num_clips

    # iterate over each clip and save it as a new video file
    for i in range(num_clips):
        # set the start and end times of the clip
        start_time = i * clip_duration
        end_time = min((i + 1) * clip_duration, video.duration)

        # extract the clip from the input video
        clip = video.subclip(start_time, end_time)

        # set the output filename
        output_file = f'clip{i}.mp4'
        output_path = f'{output_dir}/{output_file}'

        # save the clip as a new video file
        clip.write_videofile(output_path, codec='libx264')

        # update the progress bar
        progress_bar['value'] += 1
        progress_bar.update()

    # close the input video file
    video.close()

    # display a success message
    messagebox.showinfo('Success', 'Video splitting complete!')

    # reset the logging widget
    logging.getLogger('moviepy').removeHandler(logging_handler)
    logging_widget.config(state=tk.DISABLED)


# create the GUI
root = tk.Tk()
root.title('Video Splitter')

# create the input file label and entry
input_file_label = tk.Label(root, text='Input file:')
input_file_label.grid(row=0, column=0)
input_file_entry = tk.Entry(root)
input_file_entry.grid(row=0, column=1)
input_file_button = tk.Button(root, text='Browse',command=browse_input_file)
input_file_button.grid(row=0, column=2)

output_dir_label = tk.Label(root, text='Output directory:')
output_dir_label.grid(row=1, column=0)
output_dir_entry = tk.Entry(root)
output_dir_entry.grid(row=1, column=1)
output_dir_button = tk.Button(root, text='Browse', command=browse_output_dir)
output_dir_button.grid(row=1, column=2)

duration_label = tk.Label(root, text='Clip duration (seconds):')
duration_label.grid(row=2, column=0)
duration_entry = tk.Entry(root)
duration_entry.grid(row=2, column=1)

logging_label = tk.Label(root, text='Log:')
logging_label.grid(row=3, column=0)
logging_widget = ScrolledText(root, width=50, height=10, state=tk.DISABLED)
logging_widget.grid(row=4, column=0, columnspan=3)

progress_bar = Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
progress_bar.grid(row=5, column=0, columnspan=3)

split_button = tk.Button(root, text='Split Video', command=split_video)
split_button.grid(row=6, column=1)

root.mainloop()

