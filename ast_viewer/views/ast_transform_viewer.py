from __future__ import print_function

__author__ = 'Chick Markley'

from PySide import QtGui, QtCore
import ast
import inspect
from ctree.codegen import CodeGenVisitor
from ast_viewer.views.editor_widget import EditorPane


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
        self.transformers = self.controller.ast_transformer_manager
        self.transformers.get_ast_transformers('ctree.transformations')

        self.reload_list()
        self.transform_list.itemClicked.connect(self.show)
        self.transform_list.doubleClicked.connect(self.go)

        layout.addWidget(self.transform_list)

        self.editor = EditorPane()
        layout.addWidget(self.editor)

        self.setLayout(layout)

    def go(self):
        current_item = self.transform_list.currentItem()
        print("apply invoked with %s" % current_item.text())

        transformer = current_item.ast_transformer_item.node_transformer()
        print("go got transformer %s" % transformer)
        if isinstance(transformer, ast.NodeTransformer):
            print("let's add a tree")
            self.parent_viewer.add_tree_tab(name=current_item.text(), transformer=transformer)
        elif isinstance(transformer, CodeGenVisitor):
            print(transformer.visit(self))

    @QtCore.Slot(QtGui.QListWidgetItem)
    def show(self, item):
        print("show item %s" % item)
        transformer = item.ast_transformer_item.node_transformer
        self.editor.setPlainText(inspect.getsource(transformer))

    def reload_list(self):
        print("self.transformers %s" % self.transformers)
        self.transform_list.clear()
        for transformer in self.transformers.transformer_items:
            print("adding transformer %s" % transformer.name)
            self.transform_list.addItem(
                AstTransformWidgetItem(transformer)
            )

    def load(self):
        file_name, _ = QtGui.QFileDialog.getOpenFileName(
            self.parent_viewer,
            caption="Select a file containing Node Transformers",
            # dir=os.getcwd(),
            # filter="Python Files (*.py);;All Files (*);;"
        )
        print("got file_name %s" % file_name)
        self.controller.load_transforms(file_name)
        self.reload_list()

    def load_package(self):
        package_name, ok = QtGui.QInputDialog.getText(
            self,
            "Load additional tranformers",
            "package name or path to file",
            QtGui.QLineEdit.Normal,
            "ast_viewer.transformers.identity_transform"
        )
        if ok and package_name != '':
            print("Got package name %s" % package_name)
            self.controller.load_transforms(package_name)
            self.reload_list()

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


class AstTransformWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, ast_transformer_item):
        super(AstTransformWidgetItem, self).__init__(ast_transformer_item.name())
        self.ast_transformer_item = ast_transformer_item
