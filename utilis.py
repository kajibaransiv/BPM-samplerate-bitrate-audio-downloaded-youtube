import os
import librosa
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt, QMimeData, QUrl
from PyQt5.QtGui import QDrag
import numpy as np

# Fixed folder where all audios are saved
FIXED_FOLDER = "C:/Users/V01tage/Desktop/audios"
CACHE_FOLDER = "C:/Users/V01tage/Desktop/audios/cache"

class DragEnabledTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)  # Hide vertical header (Row numbers)
        self.setHorizontalHeaderLabels(["File Names", "BPM"])  # Set headings

        self.setColumnCount(2)
        self.setColumnWidth(1, 150)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Make 1st column stretchable
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Make 2nd column fixed

        self.populate_table()  # Fill the table with data

    def populate_table(self):
        if not os.path.exists(FIXED_FOLDER):
            QMessageBox.warning(None, "Error", "The folder does not exist.")
            return

        files = [f for f in os.listdir(FIXED_FOLDER) if f.endswith(".mp3")]

        self.setRowCount(len(files))
        for row, file in enumerate(files):
            item = QTableWidgetItem(file)
            self.setItem(row, 0, item)
            bpm = -1
            try:
                y, sr = librosa.load(os.path.join(FIXED_FOLDER, file), sr=None)
                bpm, _ = librosa.beat.beat_track(y=y, sr=sr)

                # If bpm is a numpy array, convert it to a scalar
                if isinstance(bpm, np.ndarray):
                    bpm = bpm.item()  # Extract the scalar value

            except Exception as e:
                print(f"Error processing {file}: {e}")
                bpm = 0  # Indicate an error with BPM calculation

            item = QTableWidgetItem(str(round(bpm, 2)))
            self.setItem(row, 1, item)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startDragPos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.startDragPos).manhattanLength() < QApplication.startDragDistance():
            return

        selected_indexes = self.selectedIndexes()
        if not selected_indexes:
            return

        selected_item = self.item(selected_indexes[0].row(), 0).text()

        drag = QDrag(self)
        mime_data = QMimeData()
        urls = [os.path.join(FIXED_FOLDER, selected_item)]
        mime_data.setUrls([QUrl.fromLocalFile(url) for url in urls])
        drag.setMimeData(mime_data)

        drop_action = drag.exec_(Qt.CopyAction | Qt.MoveAction)

        if drop_action == Qt.MoveAction:
            self.removeRow(selected_indexes[0].row())
