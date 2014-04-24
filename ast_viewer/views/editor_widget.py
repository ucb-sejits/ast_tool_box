__author__ = 'Chick Markley'

from PySide import QtGui, QtCore
from ast_viewer.views.highlighter import Highlighter


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

        self.highlighter = Highlighter(self.document())

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_read_only(self, value):
        if self.parent_panel:
            self.parent_panel.set_read_only(value)


class EditorPanel(QtGui.QGroupBox):
    def __init__(self):
        super(EditorPanel, self).__init__("Editor")

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
        layout.addWidget(button_panel)
        layout.addWidget(self.editor)

        self.setLayout(layout)

    def save(self):
        print("Got save file for %s" % self.editor.file_name)

    def set_read_only(self, value):
        value = not value
        self.save_button.setEnabled(value)
        self.undo_button.setEnabled(value)
        self.redo_button.setEnabled(value)
