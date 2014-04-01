__author__ = 'Chick Markley'

import types
import ast
import copy

from PySide import QtGui, QtCore

from ast_viewer.models.node_transformers import NodeTransformerManager


DEBUGGING = False


class AstTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent, source_node=None):
        super(AstTreeItem, self).__init__(parent)
        self.ast_node = source_node


class TransformerAction(QtGui.QAction):
    def __init__(self, text, tree_widget, **kwargs):
        super(TransformerAction, self).__init__(text, tree_widget, **kwargs)
        self.tree_widget = tree_widget
        self.text = text

    def triggered(self, *args, **kwargs):
        print("Triggered with string %s" % self.text)
        self.tree_widget.transform_current_ast(self.text)

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

    def __init__(self, parent=None):
        super(AstTreeWidget, self).__init__(parent)

        self.parent_viewer = parent
        self.ast_root = None
        self.setColumnCount(2)
        self.setHeaderLabels(
            ["Node"]
        )
        self.header().resizeSection(AstTreeWidget.COL_NODE, 800)
        self.header().setStretchLastSection(True)

        self.node_transformers = NodeTransformerManager()
        self.node_transformers.get_node_transformers('ctree.transformations')

        self.transform_signal = QtCore.Signal(int)

        self.make_new_tab_action = QtGui.QAction(
            "&Duplicate this tree",
            self,
            statusTip="Duplicate this tree in new tab",
            triggered=self.make_new_tab
        )
        self.make_root_action = QtGui.QAction(
            "&Make this node be root",
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

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        menu.addAction(self.make_new_tab_action)
        menu.addAction(self.expand_descendants_action)

        sub_menu = QtGui.QMenu(self)
        sub_menu.setTitle("Available transformers")
        for transformer_name in self.node_transformers.all_transformers_by_name:
            sub_menu_action = TransformerAction(transformer_name, self)
            sub_menu.addAction(sub_menu_action)
        menu.addMenu(sub_menu)
        menu.addAction(self.make_root_action)
        menu.exec_(event.globalPos())

    def transform_current_ast(self, name):
        transformer = self.node_transformers.get_instance(name)
        new_ast = copy.deepcopy(self.ast_root)
        transformer.visit(new_ast)
        self.parent_viewer.add_tree_tab(new_ast)

    def make_new_tab(self):
        self.parent_viewer.add_tree_tab(copy.deepcopy(self.ast_root))

    def make_root(self):
        """make the current item the displayed root of the tree"""
        self.make_tree_from(self.currentItem().ast_node)

    def expand_descendants(self, item=None):
        """Expand all descendants of the current item"""
        if item is None:
            item = self.currentItem()
        item.setExpanded(True)
        # print("at_node %s children count %d" % (item, item.childCount()))
        for child_index in range(item.childCount()):
            self.expand_descendants(item.child(child_index))

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
            node_item = AstTreeItem(parent_item)
            node_item.ast_node = ast_node

            if hasattr(ast_node, 'lineno'):
                position_str = "({:d}:{:d})".format(ast_node.lineno, ast_node.col_offset)

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
                value_str = ''
                node_str = "{} = {}".format(field_label, class_name(ast_node))
                for idx, node in enumerate(ast_node):
                    add_node(node, node_item, "{}[{:d}]".format(field_label, idx))
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
        self.expandToDepth(display_depth)

        self.ast_root = syntax_tree

def class_name(obj):
    """ Returns the class name of an object"""
    return obj.__class__.__name__
