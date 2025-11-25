from PySide6.QtCore import QObject, Slot, Signal

class EventPublisher(QObject):
    file_operation = Signal(dict)
    def __init__(self):
        super().__init__()

    def emit_file_action(self, type, args): 
        self.file_operation.emit({"type":type, "args":args})

class EventBus(QObject):
    def __init__(self, events):
        super().__init__()

    @Slot(dict)
    def on_command(self, msg): print(msg)