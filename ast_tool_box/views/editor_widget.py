__author__ = 'Chick Markley'

from PySide import QtGui, QtCore
from ast_tool_box.views.highlighter import Highlighter


class EditorPane(QtGui.QPlainTextEdit):
    def __init__(self, parent_panel=None):
        # Editor widget
        super(EditorPane, self).__init__()
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(13)

        self.file_name = ''
        self.parent_panel = parent_panel

        # self.setReadOnly(True)
        self.setFont(font)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setStyleSheet("selection-color: black; selection-background-color: yellow;")

        if self.parent_panel:
            self.textChanged.connect(self.parent_panel.text_changed)

        self.highlighter = Highlighter(self.document())

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_read_only(self, value):
        if self.parent_panel:
            self.parent_panel.set_read_only(value)
        self.setReadOnly(value)

    def setPlainText(self, text):
        if self.parent_panel:
            self.parent_panel.save_button.setEnabled(True)
            self.parent_panel.undo_button.setEnabled(True)
        super(EditorPane, self).setPlainText(text)


class EditorPanel(QtGui.QGroupBox):
    def __init__(self, transform_pane=None):
        super(EditorPanel, self).__init__("Editor")
        self.transform_pane = transform_pane

        layout = QtGui.QVBoxLayout()
        button_panel = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)

        self.save_button = QtGui.QPushButton("Save")
        self.undo_button = QtGui.QPushButton("Undo")
        self.redo_button = QtGui.QPushButton("Undo")
        self.save_button = button_panel.addButton(u"Save", QtGui.QDialogButtonBox.AcceptRole)
        self.undo_button = button_panel.addButton(u"Undo", QtGui.QDialogButtonBox.ActionRole)
        self.redo_button = button_panel.addButton(u"Redo", QtGui.QDialogButtonBox.ActionRole)

        self.editor = EditorPane(parent_panel=self)

        self.save_button.clicked.connect(self.save)
        self.undo_button.clicked.connect(self.undo)
        self.redo_button.clicked.connect(self.redo)

        layout.addWidget(button_panel)
        layout.addWidget(self.editor)

        self.setLayout(layout)

    def text_changed(self):
        self.save_button.setEnabled(True)
        self.undo_button.setEnabled(True)

    def undo(self):
        self.editor.undo()
        if not self.editor.undoAvailable():
            self.undo_button.setEnabled(False)
        self.redo_button.setEnabled(True)

    def redo(self):
        self.editor.redo()
        if not self.editor.redoAvailable():
            self.redo_button.setEnabled(False)
        self.undo_button.setEnabled(True)

    def save(self):
        print("Got save file for %s" % self.editor.file_name)
        file_text = self.editor.toPlainText()
        with open(self.editor.file_name, "w+") as f:
            f.write(file_text)
        self.editor.setPlainText(file_text)
        self.save_button.setEnabled(False)
        if self.transform_pane:
            self.transform_pane.transform_presenter.reload_transforms()

    def set_read_only(self, value):
        if value:
            self.disable_buttons()

    def disable_buttons(self):
        self.save_button.setEnabled(False)
        self.undo_button.setEnabled(False)
        self.redo_button.setEnabled(False)
