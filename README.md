# Speech Tray

Speech Tray is a system tray application that uses speech recognition to convert spoken words into text and insert them at the current cursor position.

## Installation

First, install the system-level dependencies. On Ubuntu, you can do this with:

    sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 python3-pil portaudio19-dev

Then, clone the repository and install the Python dependencies:

    git clone https://github.com/baztian/speech-tray.git
    cd speech-tray
    pip install -r requirements.txt
    pip install .

### Startup and stop

    speech-tray
    kill $(cat "$HOME/.local/share/speech-tray/pid.txt")

### Add keyboard shortcuts

In order to control via keyboard shortcuts you can control speech-tray via
Unix signals.

Depending on your window manager you can assign a key to one of the following
commands.

For english (`en-US`) speech recognition:

    bash -c "kill -SIGUSR1 $(cat "$HOME/.local/share/speech-tray/pid.txt")"

For german (`de-DE`) speech recognition:

    bash -c "kill -SIGUSR2 $(cat "$HOME/.local/share/speech-tray/pid.txt")"

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
