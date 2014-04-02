__author__ = 'Chick Markley'

from PySide import QtGui

class EditorPane(object):
    def __init__(self):
        # Editor widget
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(13)

        self.editor = QtGui.QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(font)
        self.editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.editor.setStyleSheet("selection-color: black; selection-background-color: yellow;")
