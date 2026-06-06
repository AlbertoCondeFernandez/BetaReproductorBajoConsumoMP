import sys
import os
"""
si no detecta en terminal hay que poner
pip install python-vlc
pip install PyQt6
"""
#os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
import random
import vlc  #python -m pip install python-vlc
#python -m pip install PyQt6
#python -m pip show PyQt6 para comprobar
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QListWidget,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox
)

from PyQt6.QtCore import QTimer


class MusicPlayer(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Reproductor MP3 / MP4")
        self.resize(800, 600)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.playlist = []
        self.current_index = -1

        self.shuffle_mode = False
        self.repeat_song = False
        self.repeat_folder = True

        self.create_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_song_end)
        self.timer.start(1000)

    def create_ui(self):

        layout = QVBoxLayout()

        self.lbl_folder = QLabel("Ninguna carpeta seleccionada")
        layout.addWidget(self.lbl_folder)

        btn_folder = QPushButton("Seleccionar carpeta")
        btn_folder.clicked.connect(self.select_folder)
        layout.addWidget(btn_folder)

        self.song_list = QListWidget()
        self.song_list.doubleClicked.connect(self.play_selected)
        layout.addWidget(self.song_list)

        controls = QHBoxLayout()

        self.btn_prev = QPushButton("⏮")
        self.btn_prev.clicked.connect(self.previous_song)

        self.btn_back = QPushButton("-10s")
        self.btn_back.clicked.connect(self.backward_10)

        self.btn_play = QPushButton("▶")
        self.btn_play.clicked.connect(self.play)

        self.btn_pause = QPushButton("⏸")
        self.btn_pause.clicked.connect(self.pause)

        self.btn_next = QPushButton("⏭")
        self.btn_next.clicked.connect(self.next_song)

        self.btn_forward = QPushButton("+10s")
        self.btn_forward.clicked.connect(self.forward_10)

        controls.addWidget(self.btn_prev)
        controls.addWidget(self.btn_back)
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_pause)
        controls.addWidget(self.btn_forward)
        controls.addWidget(self.btn_next)

        layout.addLayout(controls)

        self.chk_shuffle = QCheckBox("Aleatorio")
        self.chk_shuffle.stateChanged.connect(
            lambda: setattr(
                self,
                "shuffle_mode",
                self.chk_shuffle.isChecked()
            )
        )

        self.chk_repeat_song = QCheckBox("Repetir canción")
        self.chk_repeat_song.stateChanged.connect(
            lambda: setattr(
                self,
                "repeat_song",
                self.chk_repeat_song.isChecked()
            )
        )

        self.chk_repeat_folder = QCheckBox("Repetir carpeta")
        self.chk_repeat_folder.setChecked(True)
        self.chk_repeat_folder.stateChanged.connect(
            lambda: setattr(
                self,
                "repeat_folder",
                self.chk_repeat_folder.isChecked()
            )
        )

        layout.addWidget(self.chk_shuffle)
        layout.addWidget(self.chk_repeat_song)
        layout.addWidget(self.chk_repeat_folder)

        self.setLayout(layout)

    def select_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta"
        )

        if not folder:
            return

        self.lbl_folder.setText(folder)

        self.playlist.clear()
        self.song_list.clear()

        valid_extensions = (
            ".mp3",
            ".mp4",
            ".wav",
            ".m4a"
        )

        for file in os.listdir(folder):

            if file.lower().endswith(valid_extensions):

                full_path = os.path.join(folder, file)

                self.playlist.append(full_path)
                self.song_list.addItem(file)

    def play_selected(self):

        row = self.song_list.currentRow()

        if row >= 0:
            self.current_index = row
            self.load_and_play()

    def load_and_play(self):

        if self.current_index < 0:
            return

        media = self.instance.media_new(
            self.playlist[self.current_index]
        )

        self.player.set_media(media)
        self.player.play()

    def play(self):

        if self.current_index == -1 and self.playlist:
            self.current_index = 0
            self.load_and_play()
        else:
            self.player.play()

    def pause(self):
        self.player.pause()

    def next_song(self):

        if not self.playlist:
            return

        if self.shuffle_mode:

            self.current_index = random.randint(
                0,
                len(self.playlist) - 1
            )

        else:

            self.current_index += 1

            if self.current_index >= len(self.playlist):

                if self.repeat_folder:
                    self.current_index = 0
                else:
                    self.current_index = len(self.playlist) - 1
                    return

        self.song_list.setCurrentRow(self.current_index)
        self.load_and_play()

    def previous_song(self):

        if not self.playlist:
            return

        self.current_index -= 1

        if self.current_index < 0:
            self.current_index = 0

        self.song_list.setCurrentRow(self.current_index)
        self.load_and_play()

    def forward_10(self):

        current = self.player.get_time()
        self.player.set_time(current + 10000)

    def backward_10(self):

        current = self.player.get_time()

        self.player.set_time(
            max(0, current - 10000)
        )

    def check_song_end(self):

        state = self.player.get_state()

        if state == vlc.State.Ended:

            if self.repeat_song:

                self.load_and_play()

            else:

                self.next_song()

#cierra todo sin errores
    def closeEvent(self, event):

        self.player.stop()

        try:
            self.player.release()
            self.instance.release()
        except:
            pass

        event.accept()
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MusicPlayer()
    window.show()

    sys.exit(app.exec())