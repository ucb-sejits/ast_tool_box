__author__ = 'Chick Markley'

from PySide import QtGui
import types
import ast


class AstTreeTabs(QtGui.QTabWidget):
    def __init__(self, parent, tree_transform_controller):
        super(AstTreeTabs, self).__init__(parent)
        self.tree_transform_controller = tree_transform_controller

    def current_ast(self):
        if self.currentWidget():
            return self.currentWidget().ast_root
        return None