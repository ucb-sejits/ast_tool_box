from __future__ import print_function

__author__ = 'Chick Markley'

from PySide import QtGui
from ast_viewer.models.transformers import NodeTransformerManager


class AstTransformViewer(QtGui.QGroupBox):
    def __init__(self, parent):
        super(AstTransformViewer, self).__init__("Available Transforms")

        self.parent_viewer = parent

        self.last_used_directory = "."

        layout = QtGui.QVBoxLayout()

        button_box = QtGui.QGroupBox()
        button_layout = QtGui.QHBoxLayout()
        go_button = QtGui.QPushButton("Apply")
        go_button.clicked.connect(self.go)

        open_button = QtGui.QPushButton("Load More")
        open_button.clicked.connect(self.load)

        button_layout.addWidget(open_button)
        button_layout.addWidget(go_button)

        button_box.setLayout(button_layout)

        layout.addWidget(button_box)

        self.transform_list = QtGui.QListWidget()
        self.transformers = NodeTransformerManager()
        self.transformers.get_node_transformers(''
                                                'ctree.transformations')

        for transformer in self.transformers:
            self.transform_list.addItem(
                QtGui.QListWidgetItem(transformer.name())
            )
        self.transform_list.doubleClicked.connect(self.go)

        layout.addWidget(self.transform_list)

        self.setLayout(layout)

    def go(self):
        current_item = self.transform_list.currentItem()
        print(current_item.text())

        transformer = self.transformers.get_instance_by_name(current_item.text())

        self.parent_viewer.add_tree_tab(name=current_item.text(), transformer=transformer)

    def load(self):
        file_name, _ = QtGui.QFileDialog.getOpenFileName(
            self,
            "Open File",
            '',
            "Python Files (*.py);;All Files (*)"
        )
        # self.transformers.get_node_transformers()

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        menu.addAction(
            QtGui.QAction("Show source", self)
        )
        menu.addAction(
            QtGui.QAction("Apply to current tree", self)
        )
        menu.addAction(
            QtGui.QAction("Apply to current node of current tree", self)
        )
        menu.exec_(event.globalPos())

