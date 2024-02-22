# Speech Tray

Speech Tray is a system tray application that uses speech recognition to convert spoken words into text and insert them at the current cursor position.

## Installation

First, install the system-level dependencies. On Ubuntu, you can do this with:

    sudo apt-get install python3-gi gir1.2-gtk-3.0

Then, clone the repository and install the Python dependencies:

    git clone https://github.com/baztian/speech_tray.git
    cd speech_tray
    pip install -r requirements.txt
    pip install .

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
