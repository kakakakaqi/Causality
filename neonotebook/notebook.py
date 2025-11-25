# notebook class -> notebook window

from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit, QMainWindow, QFileDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence

from menus.file_menu import FileMenu
from menus.edit_menu import EditMenu
from event_bus import EventPublisher

# each notebook gets its own eventbus

class NoteBook(QMainWindow):
    def __init__(self, event_api = None):
        super().__init__()
        self.setWindowTitle("NeoNoteBook")
        self.resize(600, 400)
        self.current_file = None
        self.events = event_api or EventPublisher()

        # the text editor part
        self.text_area = QTextEdit()
        self.main_window = self.text_area
        self.setCentralWidget(self.text_area)
    
        # the menu bar -> add actions later
        self.menu_bar = self.menuBar()
        self.menu_bar.setNativeMenuBar(False)

        # initialize the menu classes and load them 
        # self.file_menu = FileMenu(self, self.text_area, self.current_file, self.events)
        # self.file_menu.load(menu_bar)
        self.fmenu = self.loadFileMenu()
        self.fmenu.load(self.menu_bar)

        self.emenu = self.loadEditMenu()
        self.emenu.load(self.menu_bar)


    def loadFileMenu(self):
        self.file_menu = self.menu_bar.addMenu("&File")
        
        # New action
        new = QAction("&New", self.main_window)
        new.setShortcut(QKeySequence.StandardKey.New)
        new.triggered.connect(self.new_file)
        self.file_menu.addAction(new)
        
        # Open action
        open = QAction("&Open", self.main_window)
        open.setShortcut(QKeySequence.StandardKey.Open)
        open.triggered.connect(self.open_file)
        self.file_menu.addAction(open)

        # Save action
        save = QAction("&Save", self.main_window)
        save.setShortcut(QKeySequence.StandardKey.Save)
        save.triggered.connect(self.save_file)
        self.file_menu.addAction(save)
        
        return self.file_menu

    def loadEditMenu(self):
        self.edit_menu = self.menu_bar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self.main_window)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.main_window.undo)
        self.edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self.main_window)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.main_window.redo)
        self.edit_menu.addAction(redo_action)

        self.edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self.main_window)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.main_window.cut)
        self.edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self.main_window)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.main_window.copy)
        self.edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self.main_window)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.main_window.paste)
        self.edit_menu.addAction(paste_action)

        return self.edit_menu

    def new_file(self): # new file
        print("new file")


    def open_file(self): # file dialogue to get file path and reads the path and puts text
        print("open file")
        filepath, _ = QFileDialog.getOpenFileName(caption="Open File")
        print(filepath)
        if filepath:
            with open(filepath, 'rt') as f:
                self.text_edit.setPlainText(f.read())
                self.current_directory = filepath
        else: print("no file found")

    def save_file(self): # add file dialogue later, currently just saves to current dir if there is one
        print("save file")
        if self.current_directory:
            content = self.text_edit.toPlainText()
            with open(self.current_directory, 'wt') as f:
                f.write(content)

    @Slot(dict)
    def on_command(self, msg): print(msg)