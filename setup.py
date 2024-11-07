from setuptools import setup

setup(
    name="speech_tray",
    version="0.1",
    py_modules=["speech_tray"],
    install_requires=[
        'SpeechRecognition',
        'PyAudio'
    ],
    entry_points={
        'console_scripts': [
            'speech-tray = speech_tray:main',
        ],
    },
)
