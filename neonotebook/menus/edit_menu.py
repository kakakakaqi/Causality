from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QKeySequence, QAction


# the edit dropdown menu
class EditMenu:
    def __init__(self, main_window, text_edit):
        self.main_window = main_window
        self.text_edit = text_edit
        self.current_file = None

    def load(self, menu_bar):
        self.edit_menu = menu_bar.addMenu("&Edit")

        undo_action = QAction("&Undo", self.main_window)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.text_edit.undo)
        self.edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self.main_window)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.text_edit.redo)
        self.edit_menu.addAction(redo_action)

        self.edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self.main_window)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.text_edit.cut)
        self.edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self.main_window)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.text_edit.copy)
        self.edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self.main_window)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.text_edit.paste)
        self.edit_menu.addAction(paste_action)

        return self.edit_menu

