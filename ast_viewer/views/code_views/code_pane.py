__author__ = 'Chick Markley'

from PySide import QtGui, QtCore
from ast_viewer.models.code_models.code_model import AstTreeItem, CodeItem, FileItem, GeneratedCodeItem
from ast_viewer.views.code_views.ast_tree_widget import AstTreePane, AstTreeWidget
from ast_viewer.views.editor_widget import EditorPane
import ast_viewer.ast_tool_box


class CodePane(QtGui.QGroupBox):
    """
    A pane that can show one or more code_items
    A code item can be source ast
    """
    def __init__(self, code_presenter=None, panel_count=2):
        super(CodePane, self).__init__("Code && Trees")
        self.code_presenter = code_presenter
        self.panel_count = panel_count
        self.all_expanded = True

        layout = QtGui.QVBoxLayout()

        toolbar_layout = QtGui.QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.addSpacing(0)

        # one_button = QtGui.QPushButton(QtGui.QIcon(QtGui.QPixmap("images/one_windows.png")), "")
        one_button = QtGui.QPushButton("|1|")
        one_button.setStyleSheet("QToolButton { border: none; padding: 0px;}")
        one_button.clicked.connect(self.set_to_one_panel)
        toolbar_layout.addWidget(one_button)

        # two_button = QtGui.QPushButton(QtGui.QIcon(QtGui.QPixmap("images/two_windows.png")), "")
        two_button = QtGui.QPushButton("|1|2|")
        two_button.setStyleSheet("QToolButton { border: none; padding: 0px;}")
        two_button.clicked.connect(self.set_to_two_panel)
        toolbar_layout.addWidget(two_button)

        # self.three_button = QtGui.QPushButton(QtGui.QIcon(QtGui.QPixmap("images/three_windows.png")), "")
        self.three_button = QtGui.QPushButton("|1|2|3|")
        self.three_button.setStyleSheet("QToolButton { border: none; padding: 0px;}")
        self.three_button.clicked.connect(self.set_to_three_panel)
        toolbar_layout.addWidget(self.three_button)
        self.three_button.setEnabled(False)

        self.expand_all_button = QtGui.QPushButton("><")
        self.expand_all_button.clicked.connect(self.expand_all_asts)
        toolbar_layout.addWidget(self.expand_all_button)

        # del_button = QtGui.QPushButton("Del")
        # del_button.clicked.connect(self.code_presenter.delete_last)
        # toolbar_layout.addWidget(del_button)

        toolbar_layout.addStretch(1)

        layout.addLayout(toolbar_layout)

        self.code_splitter = QtGui.QSplitter(self, orientation=QtCore.Qt.Horizontal)

        self.tab_bar = QtGui.QTabBar()
        # style = QtGui.QStyleFactory.create(u"Plastique")
        # self.tab_bar.setStyle(style)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setUsesScrollButtons(True)

        self.tab_bar.tabCloseRequested.connect(self.delete_at)
        self.tab_bar.currentChanged.connect(self.tab_selected)
        layout.addWidget(self.tab_bar)

        # delete_signal = QtCore.Signal(int)
        # delete_signal.connect(self.delete_tab_happened)

        class XXX(QtCore.QObject):
            delete_signal = QtCore.Signal(int)

        self.xxx = XXX(self)
        self.xxx.delete_signal.connect(self.delete_tab_happened)


        layout.addWidget(self.code_splitter)
        self.setLayout(layout)

    def expand_all_asts(self):
        if self.all_expanded:
            self.all_expanded = False
            AstTreeWidget.expand_all_at_create = False
            self.expand_all_button.setText("<>")
            self.expand_all_button.setToolTip("Expand all ast trees")
            for index in range(self.code_splitter.count()):
                try:
                    self.code_splitter.widget(index).collapse_all()
                except AttributeError:
                    pass
        else:
            self.all_expanded = True
            AstTreeWidget.expand_all_at_create = True
            self.expand_all_button.setText("><")
            self.expand_all_button.setToolTip("Collapse all ast trees")
            for index in range(self.code_splitter.count()):
                try:
                    self.code_splitter.widget(index).expand_all()
                except AttributeError:
                    pass

    def clear(self):
        for index in range(self.code_splitter.count()-1, -1, -1):
            self.tab_bar.removeTab(index)
            self.code_splitter.widget(index).deleteLater()

    @QtCore.Slot(int)
    def tab_selected(self, index):
        if index < self.tab_bar.count():
            print("Tab selected %d" % index)
            self.set_panel_sizes(emphasize_index=index)

    @QtCore.Slot(int)
    def delete_at(self, index):
        item = self.code_splitter.widget(index)
        item.deleteLater()
        # item.destroy(destroyWindow=True, destroySubWindows=True)
        self.tab_bar.removeTab(index)
        #
        # TODO the following call does not work as expected due to the deleteLater above
        #
        # self.set_panel_sizes()
        self.xxx.delete_signal.emit(index)

    @QtCore.Slot(int)
    def delete_tab_happened(self, index):
        print("deleted_tab_happened %d %s" % (index, self.code_splitter.sizes()))
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

    def set_panel_sizes(self, emphasize_index=None):
        """
        resize the panel based on current panel pattern
        """
        sizes = self.code_splitter.sizes()
        # print("In set panel sizes splitter %s self.panel_count %d sizes %s" %
        #       (
        #           [self.code_splitter.size(),self.code_splitter.baseSize(), self.code_splitter.frameSize()],
        #           self.panel_count,
        #           sizes
        #       )
        # )
        total = sum(sizes)
        if total == 0:
            total = ast_viewer.ast_tool_box.AstToolBox.default_left_frame_size
        new_sizes = map(lambda x: 0, sizes)
        panel_count = self.panel_count
        if panel_count > len(sizes):
            panel_count = len(sizes)

        if emphasize_index is None or emphasize_index >= len(sizes):
            main_emphasis_index = -1
            second_emphasis_index = -2
            third_emphasis_index = -3
        elif isinstance(emphasize_index, int):
            main_emphasis_index = emphasize_index
            current_max_tab = max(sizes)
            second_emphasis_index = sizes.index(current_max_tab)
            sizes[second_emphasis_index] = 0
            current_max_tab = max(sizes)
            third_emphasis_index = sizes.index(current_max_tab)
        else:
            main_emphasis_index = -1
            second_emphasis_index = -2
            third_emphasis_index = -3

        if panel_count == 1:
            new_sizes[main_emphasis_index] = total
        elif panel_count == 2:
            new_sizes[second_emphasis_index] = int(total * 0.4)
            new_sizes[main_emphasis_index] = int(total * 0.6)
        elif panel_count > 2:
            new_sizes[third_emphasis_index] = int(total * 0.2)
            new_sizes[second_emphasis_index] = int(total * 0.3)
            new_sizes[main_emphasis_index] = int(total * 0.5)

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
            widget = AstTreePane(self.code_presenter, code_item.code)
        elif isinstance(code_item, GeneratedCodeItem):
            widget = EditorPane()
            widget.setPlainText(code_item.code)
        else:
            CodePane.show_error("add_code_item got %s %s" % (type(code_item), code_item))
            return

        self.tab_bar.addTab(code_item.code_name)
        self.tab_bar.setCurrentIndex(self.tab_bar.count()-1)

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
