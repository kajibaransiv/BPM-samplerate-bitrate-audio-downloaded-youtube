from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog

class FilePathWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Choose Save Path")
        self.layout = QVBoxLayout()

        self.save_path_label = QLabel("Save Path:")
        self.save_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browseSavePath)

        self.layout.addWidget(self.save_path_label)
        self.layout.addWidget(self.save_path_edit)
        self.layout.addWidget(self.browse_button)

        self.setLayout(self.layout)

    def browseSavePath(self):
        options = QFileDialog.Options()
        selected_path = QFileDialog.getExistingDirectory(self, "Select Save Path", options=options)
        if selected_path:
            self.save_path_edit.setText(selected_path)
