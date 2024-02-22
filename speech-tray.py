#!/usr/bin/env python3
"""
Speech Tray

This script creates a system tray application that uses speech recognition to convert
spoken words into text and insert them at the current cursor position. It uses the
Google Speech Recognition API for speech-to-text conversion, and the GTK library for
the system tray interface.
"""
import os
from pathlib import Path
import queue
import subprocess
import signal
import threading
from PIL import Image, ImageDraw
import speech_recognition as sr
import gi

gi.require_version('Gtk', '3.0')  # Specify the version of GTK
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GdkPixbuf, GLib

IMG_SIZE = (64, 64)

def create_pixbuf_from_image(image):
    data = image.tobytes()
    w, h = image.size
    data = GLib.Bytes.new(data)
    pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * 3)
    return pixbuf

def create_pause_icon():
    image = Image.new('RGB', IMG_SIZE, color='white')
    draw = ImageDraw.Draw(image)

    # Define the size and position of the pause rectangles
    rect_width = IMG_SIZE[0] // 8  # Width of each pause rectangle
    gap = rect_width  # Gap between rectangles
    left_rect_x1 = IMG_SIZE[0] // 2 - rect_width - gap // 2
    right_rect_x1 = IMG_SIZE[0] // 2 + gap // 2
    rect_y1 = IMG_SIZE[1] // 4
    rect_y2 = IMG_SIZE[1] - IMG_SIZE[1] // 4

    # Draw the pause rectangles (black)
    draw.rectangle([left_rect_x1, rect_y1, left_rect_x1 + rect_width, rect_y2], fill='black')
    draw.rectangle([right_rect_x1, rect_y1, right_rect_x1 + rect_width, rect_y2], fill='black')
    return image

def create_record_icon():
    image = Image.new('RGB', IMG_SIZE, color='white')

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    # Define the size and position of the record circle
    circle_center = (IMG_SIZE[0] // 2, IMG_SIZE[1] // 2)
    circle_radius = IMG_SIZE[0] // 4

    # Draw the record circle (red)
    draw.ellipse((circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                circle_center[0] + circle_radius, circle_center[1] + circle_radius), fill='red')
    return image

def create_cursor_icon():
    image = Image.new('RGB', IMG_SIZE, color='white')
    draw = ImageDraw.Draw(image)

    # Define the size and position of the cursor lines
    line_width = 4  # Width of the lines
    vertical_line_height = IMG_SIZE[1] // 2  # Height of the vertical line
    horizontal_line_length = IMG_SIZE[0] // 4  # Length of the horizontal lines
    vertical_line_center_x = IMG_SIZE[0] // 2
    horizontal_line_y_top = (IMG_SIZE[1] - vertical_line_height) // 2
    horizontal_line_y_bottom = horizontal_line_y_top + vertical_line_height

    # Draw the vertical line
    draw.line([(vertical_line_center_x, horizontal_line_y_top + line_width),
            (vertical_line_center_x, horizontal_line_y_bottom - line_width)], fill='black', width=line_width)

    # Draw the top horizontal line segments
    draw.line([(vertical_line_center_x - horizontal_line_length, horizontal_line_y_top),
            (vertical_line_center_x - line_width // 2, horizontal_line_y_top)], fill='black', width=line_width)
    draw.line([(vertical_line_center_x + line_width // 2, horizontal_line_y_top),
            (vertical_line_center_x + horizontal_line_length, horizontal_line_y_top)], fill='black', width=line_width)

    # Draw the bottom horizontal line segments
    draw.line([(vertical_line_center_x - horizontal_line_length, horizontal_line_y_bottom),
            (vertical_line_center_x - line_width // 2, horizontal_line_y_bottom)], fill='black', width=line_width)
    draw.line([(vertical_line_center_x + line_width // 2, horizontal_line_y_bottom),
            (vertical_line_center_x + horizontal_line_length, horizontal_line_y_bottom)], fill='black', width=line_width)
    return image

PAUSE_ICON = create_pixbuf_from_image(create_pause_icon())
RECORD_ICON = create_pixbuf_from_image(create_record_icon())
CURSOR_ICON = create_pixbuf_from_image(create_cursor_icon())

class Task:
    def __init__(self, action, data=None):
        self.action = action
        self.data = data

# Signal handler for SIGUSR1
def record_signal(signum, frame):
    if signum == signal.SIGUSR2:
        start_german()
    else:
        start_english()

def start_english(*args):
    record()

def start_german(*args):
    record(language='de-DE')

def record(language=None):
    task_queue.put(Task('change_icon', RECORD_ICON))
    task_queue.put(Task('get_and_insert_text', language))
    task_queue.put(Task('change_icon', PAUSE_ICON))

def get_and_insert_text(language):
    text = get_audio_text(language)
    if text:
        task_queue.put(Task('change_icon', CURSOR_ICON))
        task_queue.put(Task('insert_text', text))

def get_audio_text(language=None):
    language = language or "en-US"
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Say something [{language}]:")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service; {e}")
        return None

def insert_text_at_cursor(text):
    subprocess.run(["xdotool", "type", "--clearmodifiers", text])

def tray_icon_task_handler(task_queue, status_icon):
    while True:
        task = task_queue.get()
        if task.action == 'change_icon':
            GLib.idle_add(status_icon.set_from_pixbuf, task.data)
        elif task.action == 'get_and_insert_text':
            get_and_insert_text(task.data)
        elif task.action == 'insert_text':
            insert_text_at_cursor(task.data)
            task_queue.put(Task('change_icon', PAUSE_ICON))
        elif task.action == 'quit':
            GLib.idle_add(Gtk.main_quit)
            break

def get_xdg_base_dir():
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.local/share')
    return Path(xdg_config_home)

def write_pid():
    pid_dir = get_xdg_base_dir() / 'speech-tray'
    pid_dir.mkdir(parents=True, exist_ok=True)
    pid_file = pid_dir / 'pid.txt'
    with pid_file.open('w') as f:
        f.write(str(os.getpid()))

def create_menu_item(label, callback):
    item = Gtk.MenuItem()
    item.set_label(label)
    item.connect("activate", callback)
    item.show()
    return item

if __name__ == '__main__':
    write_pid()
    # Register the signal handler
    signal.signal(signal.SIGUSR1, record_signal)
    signal.signal(signal.SIGUSR2, record_signal)

    # Queue to hold the change commands
    task_queue = queue.Queue()

    # Create the status icon
    status_icon = Gtk.StatusIcon.new_from_pixbuf(PAUSE_ICON)
    status_icon.set_title('Tray Icon Example')
    status_icon.set_tooltip_text('Tray Icon Example')
    status_icon.set_visible(True)

    # Create a menu for the status icon
    menu = Gtk.Menu()
    menu.append(create_menu_item("Record english", start_english))
    menu.append(create_menu_item("Record german", start_german))
    menu.append(create_menu_item("Quit", quit))
    status_icon.connect('popup-menu', lambda icon, button, time: menu.popup(None, None, None, icon, button, time))

    task_handler_thread = threading.Thread(target=tray_icon_task_handler, args=(task_queue, status_icon))
    task_handler_thread.start()

    Gtk.main()
    task_handler_thread.join()