import sys
import os
import whisper
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox,
    QFileDialog, QMessageBox, QListWidget, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def generate_subtitles(file_path, model, language):
    result = model.transcribe(file_path, language=language)

    srt_path = os.path.splitext(file_path)[0] + ".srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            f.write(f"{i + 1}\n")
            f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
            f.write(f"{text}\n\n")
    return srt_path


class TranscriptionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, files, model_name, language):
        super().__init__()
        self.files = files
        self.model_name = model_name
        self.language = language

    def run(self):
        model = whisper.load_model(self.model_name)
        total = len(self.files)
        for i, file_path in enumerate(self.files):
            try:
                generate_subtitles(file_path, model, self.language)
            except Exception as e:
                self.finished.emit(f"Error: {str(e)}")
                return
            self.progress.emit(int(((i + 1) / total) * 100))
        self.finished.emit("Done")


class SubtitleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Subtitle Generator")
        self.setFixedSize(500, 400)
        self.setAcceptDrops(True)
        self.files = []

        self.label = QLabel("Drag and drop media files or click 'Browse'", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.language_label = QLabel("Select Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "en", "fr", "es", "de", "hi", "zh", "ar", "ru", "ja", "ko"
        ])

        self.model_label = QLabel("Select Whisper Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])

        self.browse_button = QPushButton("Browse Files")
        self.browse_button.clicked.connect(self.browse_files)

        self.start_button = QPushButton("Start Transcription")
        self.start_button.clicked.connect(self.start_transcription)

        self.list_widget = QListWidget()

        self.progress = QProgressBar()
        self.progress.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_combo)
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_combo)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def browse_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Media Files", "", "Media Files (*.mp3 *.mp4 *.wav *.m4a *.mov *.mkv)"
        )
        if file_paths:
            self.files = file_paths
            self.list_widget.clear()
            self.list_widget.addItems([os.path.basename(f) for f in self.files])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.list_widget.clear()
        self.list_widget.addItems([os.path.basename(f) for f in self.files])

    def start_transcription(self):
        if not self.files:
            QMessageBox.warning(self, "No Files", "Please select or drag-and-drop media files.")
            return

        language = self.language_combo.currentText()
        model_name = self.model_combo.currentText()

        self.thread = TranscriptionThread(self.files, model_name, language)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.on_transcription_finished)
        self.progress.setValue(0)
        self.start_button.setEnabled(False)
        self.thread.start()

    def on_transcription_finished(self, message):
        self.start_button.setEnabled(True)
        if message == "Done":
            QMessageBox.information(self, "Success", "Subtitle generation complete!")
        else:
            QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubtitleApp()
    window.show()
    sys.exit(app.exec_())
