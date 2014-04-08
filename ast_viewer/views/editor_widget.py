__author__ = 'Chick Markley'

from PySide import QtGui

class EditorPane(QtGui.QPlainTextEdit):
    def __init__(self):
        # Editor widget
        super(EditorPane, self).__init__()
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(13)

        self.setReadOnly(True)
        self.setFont(font)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setStyleSheet("selection-color: black; selection-background-color: yellow;")
