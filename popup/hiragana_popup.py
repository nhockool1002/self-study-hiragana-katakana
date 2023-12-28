import sys
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QLabel, QVBoxLayout, QDesktopWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class HiraganaTablePopup(QDialog):
    def __init__(self):
        super().__init__()

        self.hiragana_spell = {
            "a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",
            "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
            "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",
            "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",
            "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
            "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",
            "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
            "ya": "や", "yu": "ゆ", "yo": "よ",
            "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
            "wa": "わ", "wo": "を",
            "n": "ん"
        }
        self.hiragana_order = [
            "a", "i", "u", "e", "o",
            "ka", "ki", "ku", "ke", "ko",
            "sa", "shi", "su", "se", "so",
            "ta", "chi", "tsu", "te", "to",
            "na", "ni", "nu", "ne", "no",
            "ha", "hi", "fu", "he", "ho",
            "ma", "mi", "mu", "me", "mo",
            "ya", "", "yu", "", "yo",
            "ra", "ri", "ru", "re", "ro",
            "wa", "", "", "", "wo",
            "n", "", "", "", ""
        ]

        self.init_ui()

    def convert_to_hiragana(self, word):
        word_lower = word.lower()

        if word_lower in self.hiragana_spell:
            return self.hiragana_spell[word_lower]
        else:
            return ""

    def init_ui(self):
        self.setWindowTitle("Hiragana Table")
        self.setGeometry(100, 100, 200, 250)

        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        font_hiragana = QFont("M PLUS 2", 16) 
        font_hiragana.setBold(True)

        font_word = QFont("M PLUS 2", 8)

        row, col = 0, 0
        blocks_in_row = 5

        for hiragana_char in self.hiragana_order:
            char = self.convert_to_hiragana(hiragana_char)
            word_lt = hiragana_char

            char_label = QLabel(char, self)
            char_label.setAlignment(Qt.AlignCenter)
            char_label.setFont(font_hiragana)

            word_label = QLabel(word_lt, self)
            word_label.setAlignment(Qt.AlignCenter)
            word_label.setFont(font_word)

            # Set background color and padding for both labels
            char_label.setStyleSheet("background-color: black; color: red; padding: 0px; margin: 0;")
            word_label.setStyleSheet("background-color: black; color: white; padding: 2px; margin: 0;")

            grid_layout.addWidget(char_label, row, col)
            grid_layout.addWidget(word_label, row + 1, col)  # Adding word_lt label in the row below char

            col += 1
            if col == blocks_in_row:
                col = 0
                row += 2  # Increment row by 2 to move to the next pair of rows

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

        self.setStyleSheet("background-color: black; margin: 0; padding: 0;") 
        grid_layout.setSpacing(0)

        self.setFixedSize(300, 400)

        # Calculate the position to align with the bottom of the last row
        last_row_bottom = (len(self.hiragana_order) // 5) * 2 * 20  # Assuming 2 rows per character

        # Set the position to the lower right corner of the screen, aligned with the bottom of the last row
        screen_geometry = QDesktopWidget().screenGeometry()
        self.move(screen_geometry.width() - self.width(), screen_geometry.height() - last_row_bottom)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hiragana_popup = HiraganaTablePopup()
    hiragana_popup.show()
    sys.exit(app.exec_())
