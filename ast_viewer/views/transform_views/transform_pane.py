from __future__ import print_function

from PySide import QtGui, QtCore
import inspect
import os
from ast_viewer.views.editor_widget import EditorPane


class TransformPane(QtGui.QGroupBox):
    """
    Show a list of transformers
    ast_transformers create a new tree from an existing tree
    code generators generate some language text from a tree
    transformers can be applied to nodes other than the root
    """
    def __init__(self, transform_presenter=None):
        super(TransformPane, self).__init__("Transformers && CodeGenerators")
        self.transform_presenter = transform_presenter

        self.last_used_directory = None

        settings = QtCore.QSettings()
        settings.beginGroup("transforms")
        self.last_used_directory = settings.value("load_directory", ".")
        self.last_package_name = settings.value("load_package", "")
        settings.endGroup()

        layout = QtGui.QVBoxLayout()

        button_box = QtGui.QGroupBox()
        button_box.setMaximumHeight(40)
        button_layout = QtGui.QHBoxLayout()
        go_button = QtGui.QPushButton("Apply")
        go_button.clicked.connect(self.transform_presenter.apply_current_transform)

        open_button = QtGui.QPushButton("Load File")
        open_button.clicked.connect(self.load)

        package_button = QtGui.QPushButton("Load Package")
        package_button.clicked.connect(self.load_package)

        reload_button = QtGui.QPushButton("Reload")
        reload_button.clicked.connect(self.transform_presenter.reload_transforms)

        button_layout.addWidget(package_button)
        button_layout.addWidget(open_button)
        button_layout.addWidget(go_button)
        button_layout.addWidget(reload_button)

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
        transform = item.transform_item.transform
        self.editor.setPlainText(inspect.getsource(transform))

    def update_view(self):
        self.transform_list.clear()
        for transform in self.transform_presenter.transform_items:
            self.transform_list.addItem(
                TransformWidgetItem(transform)
            )

    def current_item(self):
        return self.transform_list.currentItem()

    def load(self):
        file_name, _ = QtGui.QFileDialog.getOpenFileName(
            self,
            caption="Select a file containing Node Transformers",
            dir=self.last_used_directory,
            filter="Python Files (*.py);;All Files (*);;"
        )
        if file_name:
            settings = QtCore.QSettings()
            settings.beginGroup("transforms")
            settings.setValue("load_directory", os.path.dirname(file_name))
            settings.setValue("load_package", self.last_package_name)
            settings.endGroup()

            print("got file_name %s" % file_name)
            self.transform_presenter.load_transforms(file_name)
            self.update_view()

    def load_package(self):
        package_name, ok = QtGui.QInputDialog.getText(
            self,
            "Load additional tranformers",
            "package name or path to file",
            QtGui.QLineEdit.Normal,
            self.last_package_name,
        )
        if ok and package_name != '':
            self.last_package_name = package_name

            settings = QtCore.QSettings()
            settings.beginGroup("transforms")
            settings.setValue("load_directory", self.last_used_directory)
            settings.setValue("load_package", self.last_package_name)
            settings.endGroup()

            print("Got package name %s" % package_name)
            self.transform_presenter.load_transforms(package_name)
            self.update_view()

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
        super(TransformWidgetItem, self).__init__(
            transform_item.package_name() + "." + transform_item.name()
        )
        self.transform_item = transform_item
