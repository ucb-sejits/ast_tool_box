__author__ = 'Chick Markley'

from PySide import QtGui, QtCore
from ast_viewer.models.code_models.code_model import AstTreeItem, CodeItem, FileItem, GeneratedCodeItem, CodeTransformLink
from ast_viewer.views.search_widget import SearchLineEdit
from ast_viewer.views.code_views.ast_tree_widget import AstTreeWidget, AstTreeWidgetItem
from ast_viewer.views.editor_widget import EditorPane


class CodePane(QtGui.QGroupBox):
    """
    A pane that can show one or more code_items
    A code item can be source ast
    """
    def __init__(self, code_presenter=None, panel_count=2):
        super(CodePane, self).__init__("Code & Trees")
        self.code_presenter = code_presenter

        layout = QtGui.QVBoxLayout()

        toolbar = QtGui.QGroupBox()
        toolbar_layout = QtGui.QHBoxLayout()
        one_button = QtGui.QPushButton("1")
        one_button.clicked.connect(self.set_to_one_panel)
        toolbar_layout.addWidget(one_button)
        two_button = QtGui.QPushButton("2")
        two_button.clicked.connect(self.set_to_two_panel)
        toolbar_layout.addWidget(two_button)
        toolbar.setLayout(toolbar_layout)

        layout.addWidget(toolbar)

        self.code_splitter = QtGui.QSplitter(self, orientation=QtCore.Qt.Horizontal)

        self.code_splitter.setCollapsible(0, True)
        # code_splitter.setCollapsible(1, True)
        # code_splitter.setSizes([700, 300])
        # code_splitter.setStretchFactor(0, 0.5)
        # code_splitter.setStretchFactor(1, 0.5)

        layout.addWidget(self.code_splitter)


        self.search_box = SearchLineEdit(self, on_changed=self.search_box_changed)
        layout.addWidget(self.search_box)

        # self.ast_tree_tabs = AstTreeTabs(self, self.code_presenter)
        # layout.addWidget(self.ast_tree_tabs)

        self.setLayout(layout)

        self.panel_count = panel_count

    def set_to_one_panel(self):
        pass

    def set_to_two_panel(self):
        pass

    def add_code_item(self, code_item):
        """
        add a new code item widget to the right hand side of the
        splitter, reduce size of left hand members
        """
        assert isinstance(code_item, CodeItem)

        if isinstance(code_item, FileItem):
            widget = EditorPane()
            widget.setPlainText(code_item.code)
        elif isinstance(code_item, AstTreeItem):
            widget = AstTreeWidget()

            pass
        elif isinstance(code_item, GeneratedCodeItem):
            pass
        else:
            print("add_code_item got %s %s" % (type(code_item), code_item))

        self.code_splitter.addWidget(
            widget
        )


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
            column=0
        )
        # print("Found %d items" % len(items))
        if len(items) > 0:
            # print(items[0])
            current_tree.setCurrentItem(items[0])
            current_tree.expandItem(items[0])


class CodeSplitterView(QtGui.QSplitter):
    def __init__(self):
        super(CodeSplitterView, self).__init__()


class AstTreeTabs(QtGui.QTabWidget):
    def __init__(self, parent, main_window, tree_transform_controller):
        super(AstTreeTabs, self).__init__(parent)
        self.parent = parent
        self.main_window = main_window
        self.tree_transform_controller = tree_transform_controller

        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)
        self.setStyle(QtGui.QStyleFactory.create("Plastique"))
        self.tabCloseRequested.connect(self.close_tab)

        for tree_item in self.tree_transform_controller.ast_tree_manager:
            ast_tree_widget = AstTreeWidget(self, self.main_window)
            ast_tree_widget.make_tree_from(tree_item.ast_tree)
            self.addTab(
                ast_tree_widget,
                tree_item.name
            )

    @QtCore.Slot(int)
    def close_tab(self, index):
        print("Tab close requested index %s" % index)
        self.tree_transform_controller.ast_tree_manager.delete(index)
        self.removeTab(index)

    def current_ast(self):
        if self.currentWidget():
            return self.currentWidget().ast_root
        return None