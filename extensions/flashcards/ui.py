import sys
from dataclasses import dataclass
from typing import List

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QFileDialog,
)
from PySide6.QtCore import Qt


# =========================
# Data Model
# =========================


@dataclass
class Question:
    question: str
    answer: str


# =========================
# Flashcard Display Widget
# =========================


class FlashcardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                padding: 20px;
                border: 2px solid #444;
                border-radius: 12px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def set_text(self, text: str):
        self.label.setText(text)


# =========================
# Controller
# =========================


class FlashcardController:
    def __init__(self, questions: List[Question]):
        if not questions:
            raise ValueError("Question list cannot be empty")

        self.questions = questions
        self.index = 0
        self.showing_answer = False

    def current_text(self) -> str:
        q = self.questions[self.index]
        return q.answer if self.showing_answer else q.question

    def flip(self):
        self.showing_answer = not self.showing_answer

    def next(self):
        self.index = (self.index + 1) % len(self.questions)
        self.showing_answer = False

    def previous(self):
        self.index = (self.index - 1) % len(self.questions)
        self.showing_answer = False


# =========================
# Main Window
# =========================


class FlashcardWindow(QMainWindow):
    def __init__(self, questions: List[Question]):
        super().__init__()

        self.setWindowTitle("Flashcard App")
        self.resize(600, 400)

        self.controller = FlashcardController(questions)

        self.card = FlashcardWidget()

        self.flip_btn = QPushButton("Flip")
        self.next_btn = QPushButton("Next")
        self.prev_btn = QPushButton("Previous")
        self.import_btn = QPushButton("Import…")

        self.flip_btn.clicked.connect(self.flip_card)
        self.next_btn.clicked.connect(self.next_card)
        self.prev_btn.clicked.connect(self.prev_card)
        self.import_btn.clicked.connect(self.import_file)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_btn)
        button_layout.addWidget(self.flip_btn)
        button_layout.addWidget(self.next_btn)
        button_layout.addWidget(self.import_btn)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(self.card)
        layout.addLayout(button_layout)

        self.setCentralWidget(root)

        self.update_card()

    def update_card(self):
        self.card.set_text(self.controller.current_text())

    def flip_card(self):
        self.controller.flip()
        self.update_card()

    def next_card(self):
        self.controller.next()
        self.update_card()

    def prev_card(self):
        self.controller.previous()
        self.update_card()

    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Questions", "", "All Files (*)"
        )

        if not path:
            return

        questions = self.load_questions_from_file(path)
        if questions:
            self.controller = FlashcardController(questions)
            self.update_card()

    def load_questions_from_file(self, path: str) -> list[Question]:
        questions: list[Question] = []
        if path.endswith(".qlst"):
            with open(path, "r", encoding="utf-8") as f:
                txt = f.read()
            stuff = txt.split(f"{chr(8)}\n")
            for s in stuff[:-1]:
                q, a = s.split(chr(8))
                questions.append(Question(q, a))
        return questions


# =========================
# App Entry Point
# =========================


def main():
    app = QApplication(sys.argv)

    questions = [
        Question(
            "To import a list of questions, click the <import> button", "wrong side"
        ),
    ]

    window = FlashcardWindow(questions)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
