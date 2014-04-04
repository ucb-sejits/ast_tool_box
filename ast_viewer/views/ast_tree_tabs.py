__author__ = 'Chick Markley'

from PySide import QtGui, QtCore
from ast_viewer.views.ast_tree_widget import AstTreeWidget
from ast_viewer.views.search_widget import SearchLineEdit

class AstTreePane(QtGui.QGroupBox):
    def __init__(self, controller):
        super(AstTreePane, self).__init__("AST Trees")
        self.controller = controller

        layout = QtGui.QVBoxLayout()

        self.search_box = SearchLineEdit(
            QtGui.QPixmap(r"images/search_icon.png"),
            QtGui.QPixmap(r"images/search_icon.png"),
            on_changed=self.search_box_changed
        )
        layout.addWidget(self.search_box)

        self.ast_tree_tabs = AstTreeTabs(self, self.controller)
        layout.addWidget(self.ast_tree_tabs)

        self.setLayout(layout)

    def search_box_changed(self):
        if not self.search_box.text():
            return

        current_tree = self.ast_tree_tabs.currentWidget()
        # print("current tree %s" % current_tree)
        #
        # for widget_index in range(self.ast_tree_tabs.count()):
        #     widget = self.ast_tree_tabs.widget(widget_index)
        #     print("widget %s ast_tree %s" % (widget, widget.ast_root))

        items = current_tree.findItems(
            self.search_box.text(),
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive,
            column=AstTreeWidget.COL_NODE
        )
        # print("Found %d items" % len(items))
        if len(items) > 0:
            # print(items[0])
            current_tree.setCurrentItem(items[0])
            current_tree.expandItem(items[0])


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