__author__ = 'Chick Markley'

from PySide import QtGui, QtCore
from ast_viewer.models.code_models.code_model import AstTreeItem, CodeItem, FileItem, GeneratedCodeItem
from ast_viewer.views.code_views.ast_tree_widget import AstTreeWidget
from ast_viewer.views.editor_widget import EditorPane
import ast_viewer.ast_tool_box


class CodePane(QtGui.QGroupBox):
    """
    A pane that can show one or more code_items
    A code item can be source ast
    """
    def __init__(self, code_presenter=None, panel_count=2):
        super(CodePane, self).__init__("Code & Trees")
        self.code_presenter = code_presenter
        self.panel_count = panel_count

        layout = QtGui.QVBoxLayout()

        toolbar_layout = QtGui.QHBoxLayout()
        toolbar_layout.addSpacing(0)

        one_button = QtGui.QPushButton("|1|")
        one_button.clicked.connect(self.set_to_one_panel)
        toolbar_layout.addWidget(one_button)

        two_button = QtGui.QPushButton("|1|2|")
        two_button.clicked.connect(self.set_to_two_panel)
        toolbar_layout.addWidget(two_button)

        self.three_button = QtGui.QPushButton("|1|2|3|")
        self.three_button.clicked.connect(self.set_to_three_panel)
        toolbar_layout.addWidget(self.three_button)
        self.three_button.setEnabled(False)

        toolbar_layout.addSpacing(10)

        del_button = QtGui.QPushButton("Del")
        del_button.clicked.connect(self.code_presenter.delete_last)
        toolbar_layout.addWidget(del_button)
        toolbar_layout.addStretch(1)

        layout.addLayout(toolbar_layout)

        self.code_splitter = QtGui.QSplitter(self, orientation=QtCore.Qt.Horizontal)

        self.tab_bar = QtGui.QTabBar()
        self.tab_bar.setStyle(QtGui.QStyleFactory.create("Plastique"))
        layout.addWidget(self.tab_bar)

        layout.addWidget(self.code_splitter)
        #
        #
        # self.search_box = SearchLineEdit(self, on_changed=self.search_box_changed)
        # layout.addWidget(self.search_box)

        # self.ast_tree_tabs = AstTreeTabs(self, self.code_presenter)
        # layout.addWidget(self.ast_tree_tabs)

        self.setLayout(layout)

    def clear(self):
        for index in range(self.code_splitter.count()-1, 0, -1):
            self.tab_bar.removeTab(index)
            self.code_splitter.widget(index).deleteLater()

    def delete_at(self, index):
        item = self.code_splitter.widget(index)
        item.deleteLater()
        self.tab_bar.removeTab(index)
        self.set_panel_sizes()

    def set_to_one_panel(self):
        self.panel_count = 1
        self.set_panel_sizes()

    def set_to_two_panel(self):
        self.panel_count = 2
        self.set_panel_sizes()

    def set_to_three_panel(self):
        self.panel_count = 3
        self.set_panel_sizes()

    def set_panel_sizes(self):
        sizes = self.code_splitter.sizes()
        print("In set panel sizes splitter %s self.panel_count %d sizes %s" %
              (
                  [self.code_splitter.size(),self.code_splitter.baseSize(), self.code_splitter.frameSize()],
                   self.panel_count,
                   sizes
              )
        )
        total = sum(sizes)
        if total == 0:
            total = ast_viewer.ast_tool_box.AstToolBox.default_left_frame_size
        new_sizes = map(lambda x: 0, sizes)
        panel_count = self.panel_count
        if panel_count > len(sizes):
            panel_count = len(sizes)

        if panel_count == 1:
            new_sizes[-1] = total
        elif panel_count == 2:
            new_sizes[-2] = int(total * 0.4)
            new_sizes[-1] = int(total * 0.6)
        elif panel_count > 2:
            new_sizes[-3] = int(total * 0.2)
            new_sizes[-2] = int(total * 0.3)
            new_sizes[-1] = int(total * 0.5)

        self.code_splitter.setSizes(new_sizes)

    def current_item(self):
        return self.code_presenter.current_item()

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
            widget = AstTreeWidget(self.code_presenter, code_item.code)
        elif isinstance(code_item, GeneratedCodeItem):
            widget = EditorPane()
            widget.setPlainText(code_item.code)
        else:
            CodePane.show_error("add_code_item got %s %s" % (type(code_item), code_item))
            return

        self.tab_bar.addTab(code_item.code_name)

        self.code_splitter.addWidget(widget)
        if self.code_splitter.count() > 2:
            self.three_button.setEnabled(True)
        self.code_splitter.setCollapsible(self.code_splitter.count()-1, True)
        self.set_panel_sizes()

    @staticmethod
    def show_error(message):
        QtGui.QErrorMessage.showMessage(message)

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
