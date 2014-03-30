from __future__ import print_function

__author__ = 'Chick Markley'

from PySide import QtCore, QtGui
from ast_viewer.transformers import NodeTransformerManager
import copy

class AstTransformViewer(QtGui.QGroupBox):
    def __init__(self, parent):
        super(AstTransformViewer, self).__init__("Available Transforms")

        self.parent_viewer = parent
        layout = QtGui.QVBoxLayout()

        self.transform_list = QtGui.QListWidget()
        self.transformers = NodeTransformerManager()
        self.transformers.get_node_transformers('ctree.transformations')

        for transform_name in self.transformers:
            self.transform_list.addItem(
                QtGui.QListWidgetItem(transform_name)
            )
        self.transform_list.doubleClicked.connect(self.go)

        layout.addWidget(self.transform_list)

        go_button = QtGui.QPushButton("Go")
        go_button.clicked.connect(self.go)
        layout.addWidget(go_button)

        self.setLayout(layout)

    def go(self):
        current_item = self.transform_list.currentItem()
        print(current_item.text())

        transformer = self.transformers.get_instance(current_item.text())

        self.parent_viewer.add_tree_tab(name=current_item.text(), transformer=transformer)

