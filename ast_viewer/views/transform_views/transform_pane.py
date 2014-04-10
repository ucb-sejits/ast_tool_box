from __future__ import print_function

from PySide import QtGui, QtCore
import inspect
from ast_viewer.views.editor_widget import EditorPane


class TransformPane(QtGui.QGroupBox):
    """
    Show a list of transformers
    ast_transformers create a new tree from an existing tree
    code generators generate some language text from a tree
    transformers can be applied to nodes other than the root
    """
    def __init__(self, transform_presenter=None):
        super(TransformPane, self).__init__("Transformers & CodeGenerators")
        self.transform_presenter = transform_presenter

        self.last_used_directory = "."

        layout = QtGui.QVBoxLayout()

        button_box = QtGui.QGroupBox()
        button_layout = QtGui.QHBoxLayout()
        go_button = QtGui.QPushButton("Apply")
        go_button.clicked.connect(self.transform_presenter.apply_current_transform)

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

        self.transform_list.itemClicked.connect(self.load_editor_from)
        self.transform_list.doubleClicked.connect(self.transform_presenter.apply_current_transform)

        layout.addWidget(self.transform_list)

        self.editor = EditorPane()
        layout.addWidget(self.editor)

        self.setLayout(layout)

    @QtCore.Slot(QtGui.QListWidgetItem)
    def load_editor_from(self, item):
        print("show item %s" % item)
        transformer = item.transform_item.transform
        self.editor.setPlainText(inspect.getsource(transformer))

    def reload_list(self):
        self.transform_list.clear()
        for transformer in self.transform_presenter.transform_items:
            print("adding transformer %s" % transformer.name)
            self.transform_list.addItem(
                TransformWidgetItem(transformer)
            )

    def current_item(self):
        return self.transform_list.currentItem()

    def load(self):
        file_name, _ = QtGui.QFileDialog.getOpenFileName(
            self.parent_viewer,
            caption="Select a file containing Node Transformers",
            # dir=os.getcwd(),
            # filter="Python Files (*.py);;All Files (*);;"
        )
        print("got file_name %s" % file_name)
        self.transform_presenter.load_transformers(file_name)
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
            self.controller.load_transformers(package_name)
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


class TransformWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, transform_item):
        super(TransformWidgetItem, self).__init__(transform_item.name())
        self.transform_item = transform_item
