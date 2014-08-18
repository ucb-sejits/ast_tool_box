from __future__ import print_function

from PySide import QtGui, QtCore
import inspect
import os
from ast_tool_box.views.editor_widget import EditorPanel
from ast_tool_box.views.transform_views.transform_tree_widget import TransformTreeWidget, TransformTreeWidgetItem
from ast_tool_box.models.transform_models.transform_file import TransformFile, TransformThing, TransformPackage

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

        # self.editor = EditorPane()
        # self.main_splitter.addWidget(self.editor)

        self.editor_panel = EditorPanel(transform_pane=self)
        self.editor = self.editor_panel.editor
        self.main_splitter.addWidget(self.editor_panel)

        self.main_splitter.setSizes([300, 700])

        layout.addWidget(self.main_splitter)
        self.setLayout(layout)

    @QtCore.Slot(QtGui.QListWidgetItem)
    def load_editor_from(self, widget_item):
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

        transform_item = widget_item.source
        file_item = None
        if isinstance(transform_item, TransformThing):
            if transform_item.transform_file:
                file_item = transform_item.transform_file
                print("file_item set to %s" % file_item)
                file_name = file_item.file_name
                if not file_item.source_text:
                    source_text = transform_item.source_text
                    read_only = True
                else:
                    source_text = file_item.source_text
                    if widget_item.name() in file_item.class_def_nodes:
                        node = file_item.class_def_nodes[widget_item.name()]
                        if hasattr(node, 'lineno'):
                            line_number = node.lineno
                            column_number = node.col_offset
            else:
                file_name = transform_item.name()
                source_text = transform_item.source_text
                read_only = True
        elif isinstance(transform_item, TransformFile):
            file_name = transform_item.file_name
            source_text = transform_item.source_text
            if transform_item.load_error_line_number:
                line_number = transform_item.load_error_line_number
            read_only = False
        else:
            print("skipping editor set on click of non file or thing")
            return

        print("setting file_name %s vs %s" % (file_name, self.current_editor_item))
        if transform_item and transform_item != self.current_editor_item:
            self.current_editor_item = transform_item
            self.editor.setPlainText(source_text)
            self.editor.set_file_name(widget_item.source.file_name)
            self.editor.set_read_only(read_only)
            self.editor_panel.disable_buttons()
            title = "Edit: %s" % widget_item.source.file_name
            if read_only:
                title += " READ ONLY"
            self.editor_panel.setTitle(title)

        if file_item:
            print("set editor from has a file_item %s" % file_item)
            self.editor_panel.transform_collection = file_item
        else:
            print("set_editor_from does not have a file_item")

        self.editor.setCenterOnScroll(True)
        text_cursor = self.editor.textCursor()
        text_block = self.editor.document().findBlockByLineNumber(line_number - 1)
        pos = text_block.position() + column_number
        text_cursor.setPosition(pos)
        self.editor.setTextCursor(text_cursor)
        self.editor.setCenterOnScroll(False)

    def update_view(self):
        self.transform_tree_widget.build(self.transform_presenter.transform_collections)

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
            self.transform_presenter.load_files([file_name])
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
            self.transform_presenter.load_files([package_name])
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
