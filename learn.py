import logging

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from gtts import gTTS
import random
import sys
import os
import pygame

# Configure logging to write to a file
logging.basicConfig(filename='log.txt', level=logging.ERROR)

# List of Hiragana and Katakana characters
hiragana_list = ["あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ",
                 "さ", "し", "す", "せ", "そ", "た", "ち", "つ", "て", "と",
                 "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "へ", "ほ",
                 "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "り",
                 "る", "れ", "ろ", "わ", "を", "ん"]
katakana_list = ["ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ",
                 "サ", "シ", "ス", "セ", "ソ", "タ", "チ", "ツ", "テ", "ト",
                 "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "ヒ", "フ", "ヘ", "ホ",
                 "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "リ",
                 "ル", "レ", "ロ", "ワ", "ヲ", "ン"]

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        font_path = 'fonts/MPLUS2-VariableFont_wght.ttf'
        self.japanese_font = QFont()
        self.japanese_font.setFamily('MPLUS2')  # Replace with the actual font family name
        self.japanese_font.setPointSize(60)

        self.setWindowTitle("Self-study Hiragana and Katakana")
        self.setStyleSheet("background-color: white; background-color: black;")

        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: red; font-size: 60px; font-weight: bold; margin-bottom: 20px;")

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("color: black; background-color: yellow; font-weight: bold;")

        speak_button = QPushButton("Speak", self)
        speak_button.clicked.connect(self.speak_character)
        speak_button.setStyleSheet("color: black; background-color: yellow; font-weight: bold;")

        next_button = QPushButton("Next", self)
        next_button.clicked.connect(self.show_random_character)
        next_button.setStyleSheet("color: black; background-color: yellow; font-weight: bold;")

        footer_label = QLabel("Developed by NhutNM", self)
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: red; font-size: 9px; margin-top: 10px;")

        version_label = QLabel("0.0.1", self)
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: red; font-size: 7px;")


        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(close_button)
        layout.addWidget(speak_button)
        layout.addWidget(next_button)
        layout.addWidget(footer_label)
        layout.addWidget(version_label)

        self.setGeometry(0, 0, 200, 200)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_random_character)
        self.show_random_character()

        pygame.mixer.init()

    def show_random_character(self):
        try:
            character = random.choice(hiragana_list + katakana_list)
            self.label.setText(character)

            # Get the desktop widget to determine screen size
            desktop = QDesktopWidget()
            screen_rect = desktop.availableGeometry()

            # Set the position to the right-bottom of the screen
            self.setGeometry(screen_rect.width() - self.width(), screen_rect.height() - self.height(), self.width(), self.height())

            # Raise the main window above other running applications
            self.activateWindow()
            self.raise_()

            # Restart the timer for the next 60 seconds
            self.timer.start(60000)
        except Exception as e:
            logging.error(f"Error in show_random_character: {e}")

    def speak_character(self):
        try:
            character = self.label.text()
            tts = gTTS(text=character, lang='ja', tld='co.jp')
            tts.save("text_generate.mp3")

            # Play the generated MP3 file using pygame mixer
            pygame.mixer.music.load("text_generate.mp3")
            pygame.mixer.music.play()

            print(f"Character resolved: {self.label.text()}")  
        except Exception as e:
            logging.error(f"Error in speak_character: {e}")

    def closeEvent(self, event):
        try:
            # Stop pygame mixer
            pygame.mixer.quit()

            # Remove the generated MP3 file
            os.remove("text_generate.mp3")
            event.accept()
        except Exception as e:
            logging.error(f"Error in closeEvent: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainWindow()
    main_app.show()
    sys.exit(app.exec_())
