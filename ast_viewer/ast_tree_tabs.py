__author__ = 'Chick Markley'

from PySide import QtGui
import types
import ast


class AstTreeTabs(QtGui.QTabWidget):
    def __init__(self, parent):
        super(AstTreeTabs, self).__init__(parent)

    def current_ast(self):
        if self.currentWidget():
            return self.currentWidget().ast_root
        return None