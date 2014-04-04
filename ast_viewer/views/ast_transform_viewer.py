from __future__ import print_function

__author__ = 'Chick Markley'

from PySide import QtGui
from ast_viewer.models.ast_transformer_manager import AstTransformerManager
import os

class AstTransformViewer(QtGui.QGroupBox):
    def __init__(self, parent, tree_transform_controller):
        super(AstTransformViewer, self).__init__("Available Transforms")

        self.controller = tree_transform_controller
        self.parent_viewer = parent

        self.last_used_directory = "."

        layout = QtGui.QVBoxLayout()

        button_box = QtGui.QGroupBox()
        button_layout = QtGui.QHBoxLayout()
        go_button = QtGui.QPushButton("Apply")
        go_button.clicked.connect(self.go)

        open_button = QtGui.QPushButton("Load File")
        open_button.clicked.connect(self.load)

        package_button = QtGui.QPushButton("Load Package")
        package_button.clicked.connect(self.load_package)

        button_layout.addWidget(package_button)
        button_layout.addWidget(open_button)
        button_layout.addWidget(go_button)

        button_box.setLayout(button_layout)

        layout.addWidget(button_box)

        self.transform_list = QtGui.QListWidget()
        self.transformers = AstTransformerManager()
        self.transformers.get_ast_transformers(''
                                                'ctree.transformations')

        self.reload_list()
        self.transform_list.doubleClicked.connect(self.go)

        layout.addWidget(self.transform_list)

        self.setLayout(layout)

    def go(self):
        current_item = self.transform_list.currentItem()
        print(current_item.text())

        transformer = self.transformers.get_instance_by_name(current_item.text())

        self.parent_viewer.add_tree_tab(name=current_item.text(), transformer=transformer)

    def reload_list(self):
        self.transform_list.clear()
        for transformer in self.transformers:
            self.transform_list.addItem(
                QtGui.QListWidgetItem(transformer.name())
            )

    def load(self):
        file_name, _ = QtGui.QFileDialog.getOpenFileName(
            self.parent_viewer,
            caption="Select a file containing Node Transformers",
            # dir=os.getcwd(),
            # filter="Python Files (*.py);;All Files (*);;"
        )
        print("got file_name %s" % file_name)
        self.controller.load_transformers(file_name)
        self.reload_list()

    def load_package(self):

        pass

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

