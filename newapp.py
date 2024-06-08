import sys
import os
import re
import subprocess
import librosa
import numpy as np
import soundfile as sf
from pytube import YouTube
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QPushButton, \
    QLineEdit, QComboBox, QLabel, QTableWidgetItem, QCheckBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from utilis import DragEnabledTable  # Assuming these are custom modules, ensure they are correctly implemented and imported.
from file_path_feature import FilePathWidget

# Function to check if FFmpeg is installed and in the system PATH
def is_ffmpeg_installed():
    try:
        result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except FileNotFoundError:
        return False

class ExtractInfoThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, float)

    def __init__(self, url, sample_rate, bit_rate, channels, save_path, binaural_audio):
        super().__init__()
        self.url = url
        self.sample_rate = sample_rate
        self.bit_rate = bit_rate
        self.channels = channels
        self.save_path = save_path
        self.binaural_audio = binaural_audio

    def run(self):
        if not is_ffmpeg_installed():
            self.finished.emit("FFmpeg is not installed or not found in PATH", 0.0)
            return

        try:
            self.progress.emit(1)
            yt = YouTube(self.url)
            stream = yt.streams.filter(only_audio=True).first()

            video_title = re.sub(r'[\\/*?:"<>|]', '', yt.title)
            video_file_path = os.path.join(self.save_path, "cache", f"{video_title}.mp4")
            audio_file_path = os.path.join(self.save_path, f"{video_title}.mp3")

            # Ensure the cache directory exists
            if not os.path.exists(os.path.join(self.save_path, "cache")):
                os.makedirs(os.path.join(self.save_path, "cache"))

            # Debug print statements
            print(f"Save path: {self.save_path}")
            print(f"Video file path: {video_file_path}")
            print(f"Audio file path: {audio_file_path}")

            if not os.path.exists(video_file_path):
                stream.download(output_path=os.path.join(self.save_path, "cache"), filename=video_file_path)

            self.progress.emit(2)
            ffmpeg_command = ['ffmpeg', '-i', video_file_path, '-y', '-vn', '-ar', str(self.sample_rate), '-b:a', str(self.bit_rate), '-ac', str(self.channels), audio_file_path]
            print(f"Running ffmpeg command: {ffmpeg_command}")

            result = subprocess.run(ffmpeg_command, check=True)
            print(f"ffmpeg command result: {result}")

            if self.binaural_audio:
                self.create_binaural(audio_file_path)

            self.progress.emit(3)
            y, sr = librosa.load(audio_file_path, sr=self.sample_rate)
            bpm, _ = librosa.beat.beat_track(y=y, sr=sr)

            self.finished.emit(video_title, bpm)

        except Exception as e:
            print("Error:", e)
            self.finished.emit("", 0.0)

    def create_binaural(self, audio_file_path):
        y, sr = librosa.load(audio_file_path, sr=self.sample_rate)
        y_left = np.roll(y, 1)
        y_right = np.roll(y, -1)
        binaural_audio = np.vstack((y_left, y_right))
        binaural_audio_path = os.path.splitext(audio_file_path)[0] + "_binaural.wav"
        sf.write(binaural_audio_path, binaural_audio.T, sr)


class BPMApp(QWidget):
    def __init__(self):
        super().__init__()
        self.working = False
        self.save_path = None

        self.setWindowTitle("App")
        self.setMinimumSize(800, 500)

        top_frame = QFrame(self)
        bottom_frame = QFrame(self)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(top_frame, stretch=1)
        main_layout.addWidget(bottom_frame, stretch=3)

        top_layout = QVBoxLayout(top_frame)
        self.yt_link_input = QLineEdit()
        self.yt_link_input.setPlaceholderText("Enter YouTube Link")
        self.yt_link_input.setFixedSize(500, 40)
        self.yt_link_input.returnPressed.connect(self.extract_info)

        extract_info_button = QPushButton("Extract Info", clicked=self.extract_info)
        extract_info_button.setCursor(Qt.PointingHandCursor)
        extract_info_button.setFixedSize(200, 40)

        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["22050", "44100", "48000", "96000"])
        self.sample_rate_combo.setFixedSize(100, 30)

        self.bit_rate_combo = QComboBox()
        self.bit_rate_combo.addItems(["64k", "128k", "192k", "256k", "320k"])
        self.bit_rate_combo.setFixedSize(100, 30)

        self.channels_combo = QComboBox()
        self.channels_combo.addItems(["1 (Mono)", "2 (Stereo)"])
        self.channels_combo.setFixedSize(100, 30)

        self.binaural_checkbox = QCheckBox("Create Binaural Audio")
        self.binaural_checkbox.setChecked(False)

        h_layout_1 = QHBoxLayout()
        h_layout_1.addStretch(1)
        h_layout_1.addWidget(self.yt_link_input)
        h_layout_1.addWidget(extract_info_button)
        h_layout_1.addStretch(1)

        h_layout_2 = QHBoxLayout()
        h_layout_2.addStretch(1)
        h_layout_2.addWidget(QLabel("Sample Rate:"))
        h_layout_2.addWidget(self.sample_rate_combo)
        h_layout_2.addWidget(QLabel("Bit Rate:"))
        h_layout_2.addWidget(self.bit_rate_combo)
        h_layout_2.addWidget(QLabel("Channels:"))
        h_layout_2.addWidget(self.channels_combo)
        h_layout_2.addStretch(1)

        h_layout_3 = QHBoxLayout()
        h_layout_3.addStretch(1)
        h_layout_3.addWidget(self.binaural_checkbox)
        h_layout_3.addStretch(1)

        self.progress_label = QLabel("Please enter a link.")
        h_layout_4 = QHBoxLayout()
        h_layout_4.addStretch(1)
        h_layout_4.addWidget(self.progress_label)
        h_layout_4.addStretch(1)

        # Add save path widget
        self.save_path_widget = FilePathWidget()
        self.save_path_widget.save_path_edit.setText("C:/Users/V01tage/Desktop/audios")  # Set default save path

        top_layout.addLayout(h_layout_1)
        top_layout.addLayout(h_layout_2)
        top_layout.addLayout(h_layout_3)
        top_layout.addLayout(h_layout_4)
        top_layout.addWidget(self.save_path_widget)

        bottom_layout = QVBoxLayout(bottom_frame)
        self.files_table = DragEnabledTable()

        bottom_layout.addWidget(self.files_table)

        # Add refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_list)
        bottom_layout.addWidget(refresh_button)

        # Add search box
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search MP3 files...")
        self.search_input.textChanged.connect(self.search_files)
        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        bottom_layout.addLayout(search_layout)

        # Set column labels
        self.files_table.setColumnCount(2)
        self.files_table.setHorizontalHeaderLabels(["File name", "BPM"])
        self.files_table.setStyleSheet("QHeaderView::section { background-color: indigo; color: white; }")

    def extract_info(self):
        link = self.yt_link_input.text()
        if self.working:
            QMessageBox.critical(self, "Error", "A task is already running. Please wait.")
            return
        if link == "":
            QMessageBox.critical(self, "Error", "Please enter a link.")
            return

        sample_rate = int(self.sample_rate_combo.currentText())
        bit_rate = int(self.bit_rate_combo.currentText().replace("k", "")) * 1000
        channels = int(self.channels_combo.currentText()[0])
        binaural_audio = self.binaural_checkbox.isChecked()
        self.working = True
        self.save_path = self.save_path_widget.save_path_edit.text()  # Update save path
        self.download_thread = ExtractInfoThread(link, sample_rate, bit_rate, channels, self.save_path, binaural_audio)
        self.download_thread.finished.connect(self.on_info_extracted)
        self.download_thread.progress.connect(self.progress)
        self.download_thread.start()

    def progress(self, progress):
        if progress == 1:
            self.progress_label.setText("Downloading Video. Please wait...")
        elif progress == 2:
            self.progress_label.setText("Extracting Audio. Please wait...")
        elif progress == 3:
            self.progress_label.setText("Extracting BPM. Please wait...")

    def on_info_extracted(self, file_name, bpm):
        self.working = False
        if file_name == "FFmpeg is not installed or not found in PATH":
            QMessageBox.critical(self, "Error", "FFmpeg is not installed or not found in PATH. Please install FFmpeg and add it to your PATH.")
            self.progress_label.setText("FFmpeg is not installed or not found in PATH.")
        elif file_name != "":
            row_position = self.files_table.rowCount()
            self.files_table.insertRow(row_position)
            self.files_table.setItem(row_position, 0, QTableWidgetItem(file_name))
            self.files_table.setItem(row_position, 1, QTableWidgetItem(str(bpm)))
            self.progress_label.setText("Task completed.")
        else:
            self.progress_label.setText("Task failed. Please try again.")

        self.yt_link_input.clear()

    def refresh_list(self):
        self.files_table.populate_table()

    def search_files(self):
        search_text = self.search_input.text().lower()
        for row in range(self.files_table.rowCount()):
            file_name_item = self.files_table.item(row, 0)
            bpm_item = self.files_table.item(row, 1)
            file_name_match = search_text in file_name_item.text().lower()
            bpm_match = search_text.isdigit() and search_text in bpm_item.text()
            if file_name_match or bpm_match:
                self.files_table.setRowHidden(row, False)
            else:
                self.files_table.setRowHidden(row, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BPMApp()
    window.show()
    sys.exit(app.exec_())
