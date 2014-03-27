__author__ = 'Chick Markley'

from PySide import QtGui
import types
import ast


class AstTreeTabs(QtGui.QTabWidget):
    def __init__(self, parent):
        super(AstTreeTabs, self).__init__(parent)
