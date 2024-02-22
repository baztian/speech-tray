from setuptools import setup

setup(
    name="speech_tray",
    version="0.1",
    py_modules=["speech_tray"],
    install_requires=[
        'SpeechRecognition'
    ],
    entry_points={
        'console_scripts': [
            'speech_tray = speech_tray:main',
        ],
    },
)