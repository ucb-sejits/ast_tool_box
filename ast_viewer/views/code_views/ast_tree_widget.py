__author__ = 'Chick Markley'

import types
import ast
from ast_viewer.views.editor_widget import EditorPane
from ast_viewer.views.search_widget import SearchLineEdit

from PySide import QtGui, QtCore

DEBUGGING = False


class AstTreePane(QtGui.QGroupBox):
    def __init__(self, code_presenter=None, ast_root=None):
        super(AstTreePane, self).__init__()
        self.code_presenter = code_presenter

        self.search_next_index = 0
        self.last_search = ''

        layout = QtGui.QVBoxLayout()

        # button_box = QtGui.QGroupBox()
        # button_layout = QtGui.QHBoxLayout()
        # go_button = QtGui.QPushButton("Apply")
        # go_button.clicked.connect(self.transform_presenter.apply_current_transform)
        #
        # open_button = QtGui.QPushButton("Load File")
        # open_button.clicked.connect(self.load)
        #
        # package_button = QtGui.QPushButton("Load Package")
        # package_button.clicked.connect(self.load_package)
        #
        # button_layout.addWidget(package_button)
        # button_layout.addWidget(open_button)
        # button_layout.addWidget(go_button)
        #
        # button_box.setLayout(button_layout)
        #
        # layout.addWidget(button_box)

        self.search_box = SearchLineEdit(on_changed=self.search_box_changed, on_next=self.search_next)
        layout.addWidget(self.search_box)

        self.ast_tree_widget = AstTreeWidget(code_presenter=self.code_presenter, ast_root=ast_root)
        layout.addWidget(self.ast_tree_widget)

        self.setLayout(layout)

    def expand_all(self):
        print("got to %s" % self)
        self.ast_tree_widget.expand_descendants()

    def collapse_all(self):
        print("got to %s" % self)
        self.ast_tree_widget.collapse_descendants()

    def make_tree_from(self, syntax_tree, file_name="", display_depth=1):
        self.ast_tree_widget.make_tree_from(syntax_tree, file_name=file_name, display_depth=display_depth)

    def search_next(self):
        if self.search_box.text() != self.last_search:
            self.search_next_index = 0
        else:
            self.search_next_index += 1

        self.last_search = self.search_box.text()

        current_tree = self.ast_tree_widget
        items = current_tree.findItems(
            self.search_box.text(),
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive,
            column=AstTreeWidget.COL_NODE
        )
        # print("Found %d items" % len(items))
        if len(items) > 0:
            if self.search_next_index >= len(items):
                self.search_next_index = 0

            # print(items[0])
            current_tree.setCurrentItem(items[self.search_next_index])
            current_tree.expandItem(items[self.search_next_index])


    def search_box_changed(self):
        if not self.search_box.text():
            return

        current_tree = self.ast_tree_widget
        # print("current tree %s" % current_tree)
        #
        # for widget_index in range(self.ast_tree_tabs.count()):
        #     widget = self.ast_tree_tabs.widget(widget_index)
        #     print("widget %s ast_tree %s" % (widget, widget.ast_root))

        items = current_tree.findItems(
            self.search_box.text(),
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive,
            column=AstTreeWidget.COL_NODE
        )
        # print("Found %d items" % len(items))
        if len(items) > 0:
            # print(items[0])
            current_tree.setCurrentItem(items[0])
            current_tree.expandItem(items[0])


class AstTreeWidget(QtGui.QTreeWidget):
    """
    displays an ast as a tree widget
    """
    COL_NODE = 0
    COL_FIELD = 1
    COL_CLASS = 2
    COL_VALUE = 3
    COL_POS = 4
    COL_HIGHLIGHT = 5

    expand_all_at_create = True

    def __init__(self, code_presenter=None, ast_root=None):
        super(AstTreeWidget, self).__init__()

        self.code_presenter = code_presenter

        self.ast_root = ast_root
        self.setColumnCount(2)
        self.setHeaderLabels(["Node"])
        self.header().resizeSection(AstTreeWidget.COL_NODE, 800)
        self.header().setStretchLastSection(True)

        self.transform_signal = QtCore.Signal(int)

        self.show_with_dot_action = QtGui.QAction(
            "&show tree using dot",
            self,
            statusTip="Create a *.png file using dot",
            triggered=self.show_with_dot
        )
        self.make_root_action = QtGui.QAction(
            "&Make new panel with this node as root",
            self,
            statusTip="This node will be made the current root in this window",
            triggered=self.make_root
        )
        self.expand_descendants_action = QtGui.QAction(
            "&Expand all children",
            self,
            statusTip="Expand all descendant nodes",
            triggered=self.expand_descendants
        )

        if ast_root:
            self.make_tree_from(self.ast_root)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        menu.addAction(self.show_with_dot_action)
        menu.addAction(self.expand_descendants_action)

        sub_menu = QtGui.QMenu(self)
        sub_menu.setTitle("Available transformers")

        for transform_item in self.code_presenter.transform_presenter.transform_items():
            sub_menu_action = TransformerAction(transform_item=transform_item, ast_tree_widget=self)
            sub_menu.addAction(sub_menu_action)

        menu.addMenu(sub_menu)
        menu.addAction(self.make_root_action)
        menu.exec_(event.globalPos())

    def transform_current_ast(self, name):
        transformer = self.ast_transformers.get_instance_by_name(name)
        self.main_window.add_tree_tab(transformer=transformer)

    def show_with_dot(self):
        from ctree.visual.dot_manager import DotManager
        start_node = self.currentItem().ast_node
        if isinstance(start_node, list):
            # TODO this parent does not work
            start_node = start_node.parent
        DotManager.dot_ast_to_browser(start_node, "ast_%s.png" % "tree")

    def make_root(self):
        """make the current item the displayed root of the tree"""
        # self.ast_root = self.currentItem().ast_node
        # self.make_tree_from(self.ast_root)
        self.code_presenter.apply_transform(code_item=self.currentItem().ast_node, transform_item=None)

    def expand_descendants(self, item=None):
        """Expand all descendants of the current item"""
        if item is None:
            print("item is none")
            item = self.currentItem()
            print("item is %s" % item)

        item.setExpanded(True)
        for child_index in range(item.childCount()):
            self.expand_descendants(item.child(child_index))

    def collapse_descendants(self, item=None):
        """Expand all descendants of the current item"""
        if item is None:
            item = self.currentItem()

        item.setExpanded(False)
        for child_index in range(item.childCount()):
            self.collapse_descendants(item.child(child_index))

    def make_tree_from(self, syntax_tree, file_name="", display_depth=1):
        """
        Populates the tree widget.
        """
        self.clear()

        # State we keep during the recursion.
        # Is needed to populate the selection column.
        to_be_updated = list([])
        state = {'from': '? : ?', 'to': '1 : 0'}

        def add_node(ast_node, parent_item, field_label):
            """
            Helper function that recursively adds nodes.
                :param parent_item: The parent QTreeWidgetItem to which this node will be added
                :param field_label: Labels how this node is known to the parent
            """

            if isinstance(ast_node, types.ListType) or isinstance(ast_node, types.TupleType):
                value_str = ''
                node_str = "{} = {}".format(field_label, class_name(ast_node))
                for idx, node in enumerate(ast_node):
                    add_node(node, parent_item, "{}[{:d}]".format(field_label, idx))
                return

            node_item = AstTreeWidgetItem(parent_item)
            if parent_item is self:
               self.setCurrentItem(node_item)

            node_item.ast_node = ast_node

            if hasattr(ast_node, 'lineno'):
                position_str = " ({:d}:{:d})".format(ast_node.lineno, ast_node.col_offset)

                # If we find a new position string we set the items found since the last time
                # to 'old_line : old_col : new_line : new_col' and reset the list
                # of to-be-updated nodes
                if position_str != state['to']:
                    state['from'] = state['to']
                    state['to'] = position_str
                    for node in to_be_updated:
                        node.setText(AstTreeWidget.COL_HIGHLIGHT, "{} : {}".format(state['from'], state['to']))
                    to_be_updated[:] = [node_item]
                else:
                    to_be_updated.append(node_item)
            else:
                to_be_updated.append(node_item)
                position_str = ""

            # Recursively descend the AST
            if isinstance(ast_node, ast.AST):
                value_str = ''
                node_str = "{} = {}".format(field_label, class_name(ast_node))
                for key, val in ast.iter_fields(ast_node):
                    if val:
                        add_node(val, node_item, key)
            elif isinstance(ast_node, types.ListType) or isinstance(ast_node, types.TupleType):
                raise Exception("%s list should have been handled earlier in function" % ast_node)
            else:
                value_str = repr(ast_node)
                node_str = "{}: {}".format(field_label, value_str)

            if position_str:
                node_str += position_str

            node_item.setText(AstTreeWidget.COL_NODE, node_str)

        # End of helper function

        #syntax_tree = ast.parse(self._source_code, filename=self._file_name, mode=self._mode)
        #logger.debug(ast.dump(syntax_tree))
        add_node(syntax_tree, self, '"{}"'.format(file_name))

        if AstTreeWidget.expand_all_at_create:
            self.expandToDepth(100)
        else:
            self.expandToDepth(display_depth)

        self.ast_root = syntax_tree


def class_name(obj):
    """ Returns the class name of an object"""
    return obj.__class__.__name__


class AstTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    connects a gui tree item with the corresponding node in the actual ast tree
    """
    def __init__(self, parent, source_node=None):
        super(AstTreeWidgetItem, self).__init__(parent)
        self.ast_node = source_node


class TransformerAction(QtGui.QAction):
    def __init__(self, transform_item, ast_tree_widget, **kwargs):
        super(TransformerAction, self).__init__(transform_item.name(), ast_tree_widget, **kwargs)
        self.ast_tree_widget = ast_tree_widget
        self.transform_item = transform_item
        self.text = transform_item.name()
        self.triggered.connect(self.do_transform)

    def do_transform(self):
        print("Triggered with string %s" % self.text)
        self.ast_tree_widget.code_presenter.apply_transform(
            code_item=self.ast_tree_widget.currentItem().ast_node,
            transform_item=self.transform_item
        )

