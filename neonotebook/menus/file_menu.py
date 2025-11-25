from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtCore import Signal

# from notebook import NoteBook

# the file dropdown menu
class FileMenu:
    def __init__(self, main_window, text_edit, cd, events):
        self.main_window = main_window
        # self.text_edit = text_edit
        self.current_directory = cd # stores path of current file (if exists)
        self.events = events

    def load(self, menu_bar):
        self.file_menu = menu_bar.addMenu("&File")
        
        # New action
        new = QAction("&New", self.main_window)
        new.setShortcut(QKeySequence.StandardKey.New)
        new.triggered.connect(lambda: self.events.emit_file_action(type="newFile", args=""))
        self.file_menu.addAction(new)
        
        # Open action
        open = QAction("&Open", self.main_window)
        open.setShortcut(QKeySequence.StandardKey.Open)
        open.triggered.connect(lambda: self.events.emit_file_action(type="openFile", args=""))
        self.file_menu.addAction(open)

        # Save action
        save = QAction("&Save", self.main_window)
        save.setShortcut(QKeySequence.StandardKey.Save)
        # save.triggered.connect(self.save_file)
        self.file_menu.addAction(save)
        
        return self.file_menu

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
