import logging
import json
import random
import sys
import os
import pygame


from pathlib import Path
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QDesktopWidget, QCheckBox, QDialog, QRadioButton, QButtonGroup, QGridLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5 import QtCore
from gtts import gTTS
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from popup.hiragana_popup import HiraganaTablePopup

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

client = WebClient(token=os.environ['BOT_TOKEN'])

logging.basicConfig(filename='log.txt', level=logging.ERROR)

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(bundle_dir, 'character_lists.json')

if not os.path.isfile(file_path):
    file_path = os.path.join(os.path.dirname(bundle_dir), 'character_lists.json')

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

hiragana_list = data.get('hiragana_list', [])
katakana_list = data.get('katakana_list', [])
hiragana_dakuten = data.get('hiragana_dakuten', [])
katakana_dakuten = data.get('katakana_dakuten', [])
word_list = data.get('word_list', [])
hiragana_spell = data.get('hiragana_spell', {})
hiragana_dakuten_spell = data.get('hiragana_dakuten_spell', {})
katakana_spell = data.get('katakana_spell', {})
katakana_dakuten_spell = data.get('katakana_dakuten_spell', {})

class QuizPopup(QDialog):
    def __init__(self, hiragana_spell, katakana_spell, hiragana_dakuten_spell, katakana_dakuten_spell):
        super(QuizPopup, self).__init__()

        self.japanese_font = QFont();
        font_path = os.path.abspath('fonts/MPLUS2-VariableFont_wght.ttf')

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            available_font_families = QFontDatabase.applicationFontFamilies(font_id)
            if "M PLUS 2" in available_font_families:
                self.japanese_font = QFont("M PLUS 2")
                self.japanese_font.setFamily('M PLUS 2')
                self.japanese_font.setPointSize(60)
            else:
                print("Font 'M PLUS 2' not found after registration.")
        else:
            print("Failed to load font:", font_path)

        self.hiragana_spell = hiragana_spell
        self.katakana_spell = katakana_spell
        self.hiragana_dakuten_spell = hiragana_dakuten_spell
        self.katakana_dakuten_spell = katakana_dakuten_spell
        self.questions = self.generate_questions()

        self.setWindowTitle("Quizzing!")
        self.setStyleSheet("background-color: white; background-color: black;")

        popup_width = 250
        popup_height = 300

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        self.setGeometry(screen_rect.width() - popup_width, screen_rect.height() - popup_height, popup_width, popup_height)

        self.current_question_index = 0
        self.correct_answers = 0

        self.question_label = QLabel("", self)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setStyleSheet("color: red; font-size: 70px; font-weight: bold; margin-bottom: 20px;")
        self.question_label.setFont(self.japanese_font)
        self.radio_buttons = []
        self.button_group = QButtonGroup(self)
        self.setup_ui()

        self.show_question()

    def setup_ui(self):
        layout = self.layout()

        layout.addWidget(self.question_label)

        for i in range(4):
            radio_button = QRadioButton("", self)
            self.radio_buttons.append(radio_button)
            self.button_group.addButton(radio_button)
            layout.addWidget(radio_button)

        submit_button = QPushButton("Send", self)
        submit_button.clicked.connect(self.check_answer)
        submit_button.setStyleSheet("color: white; font-size: 12px; background-color: red; font-weight: bold;")
        layout.addWidget(submit_button)


    def show_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.question_label.setText(f"{question['question']}")
            self.question_label.setFont(self.japanese_font)
            
            random.shuffle(question['options'])
            for i in range(4):
                self.radio_buttons[i].setText(question['options'][i])
                self.radio_buttons[i].setFont(self.japanese_font)
                self.radio_buttons[i].setStyleSheet("color: white; font-size: 13px; font-weight: bold;")

            self.current_question_index += 1

            self.clear_radio_buttons()
        else:
            self.show_result()

    def check_answer(self):
        selected_answer = None
        for i, radio_button in enumerate(self.radio_buttons):
            if radio_button.isChecked():
                selected_answer = i
                break

        if selected_answer is not None:
            correct_answer_index = self.questions[self.current_question_index - 1]['options'].index(
                self.questions[self.current_question_index - 1]['answer']
            )

            if selected_answer == correct_answer_index:
                print("Correct!")
                self.correct_answers += 1
            else:
                print(f"Wrong! Correct answer: {self.questions[self.current_question_index - 1]['answer']}")

            self.show_question()
        else:
            print("Please select an answer before moving on.")

    def clear_radio_buttons(self):
        self.button_group.setExclusive(False)
        for radio_button in self.radio_buttons:
            radio_button.setChecked(False)
        self.button_group.setExclusive(True) 

    def show_result(self):
        try:
            icon_label = QLabel("🎉", self)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("font-size: 50px; margin-bottom: 5px;")

            result_label = QLabel(f"Correct Answers: {self.correct_answers}", self)
            result_label.setAlignment(Qt.AlignCenter)
            result_label.setStyleSheet("color: green; font-size: 20px; font-weight: bold; margin-bottom: 20px;")

            close_button = QPushButton("Close Result!", self)
            close_button.clicked.connect(lambda: self.close_result_and_popup(result_dialog))
            close_button.setStyleSheet("color: white; font-size: 12px; background-color: red; font-weight: bold;")

            result_layout = QVBoxLayout()
            result_layout.addWidget(icon_label)
            result_layout.addWidget(result_label)
            result_layout.addWidget(close_button)

            result_dialog = QDialog(self)
            result_dialog.setWindowTitle("Quiz Results")
            result_dialog.setLayout(result_layout)
            result_dialog.exec_()

            score_msg = f"🎉🎉🎉 Congratulations!!!\n *[Self-study Hiragana and Katakana App] Your score in Hiragana & Katakana test: {self.correct_answers}*"

            client.chat_postMessage(
                channel=os.environ['SLACK_CHANNEL'],
                text=score_msg,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": score_msg
                        }
                    }
                ],
            )
        except Exception as e:
            print(f"An error occurred in show_result: {e}")

    def close_result_and_popup(self, result_dialog):
        self.close()
        result_dialog.close()

    def generate_questions(self):
        questions = []
        characters_used = set()

        while len(questions) < 35:
            random_character = random.choice(
                list(self.hiragana_spell.keys()) +
                list(self.hiragana_dakuten_spell.keys()) +
                list(self.katakana_spell.keys()) +
                list(self.katakana_dakuten_spell.keys())
            )
            correct_answer = (
                self.hiragana_spell.get(random_character, "")
                or self.hiragana_dakuten_spell.get(random_character, "")
                or self.katakana_spell.get(random_character, "")
                or self.katakana_dakuten_spell.get(random_character, "")
                or random_character
            )

            if random_character not in characters_used:
                characters_used.add(random_character)

                options = [correct_answer]
                while len(options) < 4:
                        random_option = random.choice(
                            list(self.hiragana_spell.keys())
                            + list(self.hiragana_dakuten_spell.keys())
                            + list(self.katakana_spell.keys())
                            + list(self.katakana_dakuten_spell.keys())
                        )

                        if random_option not in options:
                            # Collect options from the available dictionaries
                            option_value = (
                                self.hiragana_spell.get(random_option, "")
                                or self.hiragana_dakuten_spell.get(random_option, "")
                                or self.katakana_spell.get(random_option, "")
                                or self.katakana_dakuten_spell.get(random_option, "")
                                or random_option
                            )

                            options.append(option_value)

                random.shuffle(options)

                questions.append({
                    'question': random_character,
                    'options': options,
                    'answer': correct_answer
                })

        return questions

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.japanese_font = QFont();
        self.quizz_popup = None
        font_path = os.path.abspath('fonts/MPLUS2-VariableFont_wght.ttf')

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            available_font_families = QFontDatabase.applicationFontFamilies(font_id)
            if "M PLUS 2" in available_font_families:
                self.japanese_font = QFont("M PLUS 2")
                self.japanese_font.setFamily('M PLUS 2')
                self.japanese_font.setPointSize(60)
            else:
                print("Font 'M PLUS 2' not found after registration.")
        else:
            print("Failed to load font:", font_path)

        self.setWindowTitle("Self-study Hiragana and Katakana")
        self.setStyleSheet("background-color: white; background-color: black;")

        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(self.japanese_font)
        self.label.setStyleSheet("color: red; font-size: 60px; font-weight: bold; margin-bottom: 20px;")
        self.label.setFixedHeight(100)

        self.checkbox_word = QCheckBox("Show Words", self)
        self.checkbox_word.setFont(self.japanese_font)
        self.checkbox_word.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        self.checkbox_word.stateChanged.connect(self.show_random_character)

        next_button = QPushButton("Next ➡️", self)
        next_button.clicked.connect(self.show_random_character)
        next_button.setFont(self.japanese_font)
        next_button.setStyleSheet("color: black; font-size: 12px; background-color: yellow; font-weight: bold;")

        speak_button = QPushButton("Speak 🗣️", self)
        speak_button.clicked.connect(self.speak_character)
        speak_button.setFont(self.japanese_font)
        speak_button.setStyleSheet("color: black; font-size: 12px; background-color: yellow; font-weight: bold;")

        quizz_button = QPushButton("Quizz 💯", self)
        quizz_button.clicked.connect(self.show_quizz_popup)
        quizz_button.setFont(self.japanese_font)
        quizz_button.setStyleSheet("color: black; font-size: 12px; background-color: yellow; font-weight: bold;")

        close_button = QPushButton("Close ❌", self)
        close_button.clicked.connect(self.close)
        close_button.setFont(self.japanese_font)
        close_button.setStyleSheet("color: black; font-size: 12px; background-color: #78f542; font-weight: bold;")

        hiragana_table_button = QPushButton("Hiragana Table", self)
        hiragana_table_button.clicked.connect(self.show_hiragana_table)

        self.version_label = QLabel("🍁 Developed by NhutNM Ⓒ 2023 - Version 1.0", self)
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setFont(self.japanese_font)
        self.version_label.setStyleSheet("color: #9ACD32; font-size: 7px; margin-top: 15px;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.checkbox_word)

        grid_layout = QGridLayout()
        grid_layout.addWidget(next_button, 0, 0)
        grid_layout.addWidget(speak_button, 0, 1)
        grid_layout.addWidget(quizz_button, 1, 0)
        grid_layout.addWidget(close_button, 1, 1)

        layout.addLayout(grid_layout)
        layout.addWidget(self.version_label, alignment=Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(hiragana_table_button)

        self.setGeometry(0, 0, 230, 0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_random_character)
        self.show_random_character()

        pygame.mixer.init()

    def show_quizz_popup(self):
        self.quizz_popup = QuizPopup(hiragana_spell, hiragana_dakuten_spell, katakana_spell, katakana_dakuten_spell)
        self.quizz_popup.finished.connect(self.quizz_popup_closed)
        self.quizz_popup.show()
    
    def quizz_popup_closed(self, result):
        if result == QDialog.Rejected:
            self.quizz_popup = None

    def show_random_character(self):
        try:
            show_words = self.checkbox_word.isChecked()
            if show_words:
                character = random.choice(word_list)
                font_size = 35
            else:
                character = random.choice(hiragana_list + hiragana_dakuten + katakana_list + katakana_dakuten)
                font_size = 60
            self.label.setText(character)
            self.label.setStyleSheet(f"color: red; font-size: {font_size}px; font-weight: bold; margin-bottom: 20px;")
            

            desktop = QDesktopWidget()
            screen_rect = desktop.availableGeometry()

            self.setGeometry(screen_rect.width() - self.width(), screen_rect.height() - self.height(), self.width(), self.height())

            if self.quizz_popup is None:
                self.activateWindow()
                self.raise_()

            self.timer.start(15000)
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

    def show_hiragana_table(self):
        hiragana_table_popup = HiraganaTablePopup()
        hiragana_table_popup.exec_()

    def closeEvent(self, event):
        try:
            if self.quizz_popup is not None:
                self.quizz_popup.close()
            
            pygame.mixer.quit()

            file_path = "text_generate.mp3"
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"{file_path} removed successfully.")
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
            else:
                print(f"{file_path} does not exist.")
            event.accept()
        except Exception as e:
            logging.error(f"Error in closeEvent: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainWindow()
    main_app.show()
    sys.exit(app.exec_())
