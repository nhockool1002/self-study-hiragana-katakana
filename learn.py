import logging
import json

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QDesktopWidget, QCheckBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from gtts import gTTS
import random
import sys
import os
import pygame

# Configure logging to write to a file
logging.basicConfig(filename='log.txt', level=logging.ERROR)

with open('character_lists.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

hiragana_list = data.get('hiragana_list', [])
katakana_list = data.get('katakana_list', [])
word_list = data.get('word_list', [])

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        font_path = 'fonts/MPLUS2-VariableFont_wght.ttf'
        self.japanese_font = QFont(font_path)
        self.japanese_font.setFamily('MPLUS2')
        self.japanese_font.setPointSize(60)

        self.setWindowTitle("Self-study Hiragana and Katakana")
        self.setStyleSheet("background-color: white; background-color: black;")

        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: red; font-size: 60px; font-weight: bold; margin-bottom: 20px;")
        self.label.setFixedHeight(100)

        self.checkbox_word = QCheckBox("Show Words", self)
        self.checkbox_word.setStyleSheet("color: white; font-weight: bold;")
        self.checkbox_word.stateChanged.connect(self.show_random_character)

        next_button = QPushButton("Next ►", self)
        next_button.clicked.connect(self.show_random_character)
        next_button.setStyleSheet("color: black; background-color: yellow; font-weight: bold;")

        speak_button = QPushButton("Speak ⚡", self)
        speak_button.clicked.connect(self.speak_character)
        speak_button.setStyleSheet("color: black; background-color: yellow; font-weight: bold;")

        close_button = QPushButton("Close ✖", self)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("color: black; background-color: red; font-weight: bold;")

        self.version_label = QLabel("Developed by NhutNM Ⓒ 2023 - Version 1.0", self)
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("color: #9ACD32; font-size: 7px; margin-top: 15px;")


        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.checkbox_word)
        layout.addWidget(next_button)
        layout.addWidget(speak_button)
        layout.addWidget(close_button)
        layout.addWidget(self.version_label, alignment=Qt.AlignRight | Qt.AlignBottom)

        self.setGeometry(0, 0, 230, 0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_random_character)
        self.show_random_character()

        pygame.mixer.init()

    def show_random_character(self):
        try:
            show_words = self.checkbox_word.isChecked()
            if show_words:
                character = random.choice(word_list)
                font_size = 35
            else:
                character = random.choice(hiragana_list + katakana_list)
                font_size = 60
            self.label.setText(character)
            self.label.setStyleSheet(f"color: red; font-size: {font_size}px; font-weight: bold; margin-bottom: 20px;")
            

            desktop = QDesktopWidget()
            screen_rect = desktop.availableGeometry()

            self.setGeometry(screen_rect.width() - self.width(), screen_rect.height() - self.height(), self.width(), self.height())

            self.activateWindow()
            self.raise_()

            self.timer.start(60000)
        except Exception as e:
            logging.error(f"Error in show_random_character: {e}")

    def speak_character(self):
        try:
            character = self.label.text()
            tts = gTTS(text=character, lang='ja', tld='co.jp')
            tts.save("text_generate.mp3")

            pygame.mixer.music.load("text_generate.mp3")
            pygame.mixer.music.play()

            print(f"Character resolved: {self.label.text()}")  
        except Exception as e:
            logging.error(f"Error in speak_character: {e}")

    def closeEvent(self, event):
        try:
            pygame.mixer.quit()

            os.remove("text_generate.mp3")
            event.accept()
        except Exception as e:
            logging.error(f"Error in closeEvent: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainWindow()
    main_app.show()
    sys.exit(app.exec_())
