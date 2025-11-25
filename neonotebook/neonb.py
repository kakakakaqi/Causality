# the main file

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit, QMainWindow
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QIcon

from menus.file_menu import FileMenu
from notebook import NoteBook

from event_bus import EventPublisher

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("icon.png"))
app.setApplicationDisplayName("NeoNotebook")
app.setApplicationName("NeoNotebook")

editor = NoteBook(EventPublisher())
editor.show()

# mainloop
sys.exit(app.exec())