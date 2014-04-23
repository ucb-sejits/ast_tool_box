from __future__ import print_function

from PySide import QtGui, QtCore
import inspect
import os
from ast_viewer.views.editor_widget import EditorPane
from ast_viewer.views.transform_views.transform_tree_widget import TransformTreeWidget, TransformTreeWidgetItem
from ast_viewer.models.transform_models.transform_file import TransformFile, TransformThing

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
        self.current_editor_item = None

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

        self.main_splitter = QtGui.QSplitter(self, orientation=QtCore.Qt.Vertical)

        self.transform_tree_widget = TransformTreeWidget(self.transform_presenter, self)
        # self.transform_tree_widget.setMaximumHeight(200)
        self.main_splitter.addWidget(self.transform_tree_widget)

        self.editor = EditorPane()
        self.main_splitter.addWidget(self.editor)
        self.main_splitter.setSizes([300, 700])

        layout.addWidget(self.main_splitter)
        self.setLayout(layout)

    @QtCore.Slot(QtGui.QListWidgetItem)
    def load_editor_from(self, item):
        """
        When a transform is clicked in the list, we put the cursor on that line in
        the file. Don't redraw or reload if cursor is already there.  If there is
        no file level source try and load from the inspect.getsource text from
        loading transform
        """
        file_name = ''
        source_text = ''
        line_number = 0
        column_number = 0
        read_only = False
        if isinstance(item.source, TransformThing):
            if item.source.transform_file:
                file_item = item.source.transform_file
                file_name = file_item.file_name
                if not file_item.source_text:
                    source_text = item.source.source_text
                    read_only = True
                else:
                    source_text = file_item.source_text
                    if item.name() in file_item.class_def_nodes:
                        node = file_item.class_def_nodes[item.name()]
                        if hasattr(node, 'lineno'):
                            line_number = node.lineno
                            column_number = node.col_offset
            else:
                self.current_editor_item = item.source.file_name
                self.editor.setPlainText(item.source.source_text)
        elif isinstance(item.source, TransformFile):
            if self.current_editor_item != item.source.file_name:
                self.current_editor_item = item.source.file_name
                self.editor.setPlainText(item.source.source_text)

        if file_name and file_name != self.current_editor_item:
            self.current_editor_item = item.source.file_name
            self.editor.setPlainText(source_text)

        self.editor.setCenterOnScroll(True)
        text_cursor = self.editor.textCursor()
        text_block = self.editor.document().findBlockByLineNumber(line_number - 1)
        pos = text_block.position() + column_number
        text_cursor.setPosition(pos)
        self.editor.setTextCursor(text_cursor)
        self.editor.setReadOnly(read_only)
        self.editor.setCenterOnScroll(False)

    def update_view(self):
        self.transform_tree_widget.build(self.transform_presenter.transform_files)

    def current_item(self):
        return self.transform_tree_widget.currentItem()

    @staticmethod
    def show_error(message):
        message_box = QtGui.QMessageBox()
        message_box.setText("Error:\n%s" % message)
        message_box.exec_()

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
            QtGui.QAction("Show source_text", self)
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
