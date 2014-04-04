__author__ = 'Chick Markley'

from PySide import QtGui
from ast_viewer.views.ast_tree_widget import AstTreeWidget


class AstTreeTabs(QtGui.QTabWidget):
    def __init__(self, parent, tree_transform_controller):
        super(AstTreeTabs, self).__init__(parent)
        self.tree_transform_controller = tree_transform_controller

        for tree_item in self.tree_transform_controller.ast_tree_manager:
            ast_tree_widget = AstTreeWidget(self)
            ast_tree_widget.make_tree_from(tree_item.ast_tree)
            self.addTab(
                ast_tree_widget,
                tree_item.name
            )

    def current_ast(self):
        if self.currentWidget():
            return self.currentWidget().ast_root
        return None