Overview
BPM Analyzer is a Python application that allows users to extract audio from YouTube videos, process the audio to extract the BPM (Beats Per Minute), and optionally create binaural audio files. This application provides a user-friendly GUI to facilitate these tasks, making it accessible for users without extensive technical knowledge.

Features
YouTube Audio Extraction: Download and extract audio from YouTube videos.
Audio Processing: Convert the extracted audio to different sample rates and bit rates.
BPM Detection: Analyze the audio to determine its BPM using the librosa library.
Binaural Audio Creation: Optionally create binaural audio versions of the extracted files.
User-Friendly Interface: Simple GUI for entering YouTube links, setting audio parameters, and managing files.
File Management: View, search, and refresh a list of processed audio files.
Installation
Requirements
Python 3.12 or higher
pip (Python package installer)
Python Libraries
PyQt5: For the GUI.
pytube: For downloading YouTube videos.
librosa: For audio processing and BPM detection.
numpy: For numerical operations.
soundfile: For audio file manipulation.

pip install PyQt5 pytube librosa numpy soundfile


the binaural beats was an experiment and doesnt really work but if you want to mess around with it and make it work then go for it 