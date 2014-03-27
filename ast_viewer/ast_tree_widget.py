__author__ = 'Chick Markley'

from PySide import QtGui
import types
import ast

DEBUGGING = False


class AstTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent, source_node=None):
        super(AstTreeItem, self).__init__(parent)
        self.ast_node = source_node


class AstTreeWidget(QtGui.QTreeWidget):
    # Tree column indices
    COL_NODE = 0
    COL_FIELD = 1
    COL_CLASS = 2
    COL_VALUE = 3
    COL_POS = 4
    COL_HIGHLIGHT = 5

    def __init__(self):
        super(AstTreeWidget, self).__init__()

        self.setColumnCount(2)
        self.setHeaderLabels(
            ["Node", "Field", "Class", "Value", "Line : Col", "Highlight"]
        )
        self.header().resizeSection(AstTreeWidget.COL_NODE, 250)
        self.header().resizeSection(AstTreeWidget.COL_FIELD, 80)
        self.header().resizeSection(AstTreeWidget.COL_CLASS, 80)
        self.header().resizeSection(AstTreeWidget.COL_VALUE, 80)
        self.header().resizeSection(AstTreeWidget.COL_POS, 80)
        self.header().resizeSection(AstTreeWidget.COL_HIGHLIGHT, 100)
        self.setColumnHidden(AstTreeWidget.COL_HIGHLIGHT, not DEBUGGING)
        self.header().setStretchLastSection(True)

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
        menu.addAction(self.make_root_action)
        menu.addAction(self.expand_descendants_action)
        menu.exec_(event.globalPos())

    def make_root(self):
        self.make_tree_from(self.currentItem().ast_node)

    def expand_descendants(self, item=None):
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
                position_str = "{:d} : {:d}".format(ast_node.lineno, ast_node.col_offset)

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
                    add_node(val, node_item, key)
            # elif type(ast_node) == types.ListType or type(ast_node) == types.TupleType:
            elif isinstance(ast_node, types.ListType) or isinstance(ast_node, types.TupleType):
                value_str = ''
                node_str = "{} = {}".format(field_label, class_name(ast_node))
                for idx, node in enumerate(ast_node):
                    add_node(node, node_item, "{}[{:d}]".format(field_label, idx))
            else:
                value_str = repr(ast_node)
                node_str = "{} = {}".format(field_label, value_str)

            node_item.setText(AstTreeWidget.COL_NODE, node_str)
            node_item.setText(AstTreeWidget.COL_FIELD, field_label)
            node_item.setText(AstTreeWidget.COL_CLASS, class_name(ast_node))
            node_item.setText(AstTreeWidget.COL_VALUE, value_str)
            node_item.setText(AstTreeWidget.COL_POS, position_str)

        # End of helper function

        #syntax_tree = ast.parse(self._source_code, filename=self._file_name, mode=self._mode)
        #logger.debug(ast.dump(syntax_tree))
        add_node(syntax_tree, self, '"{}"'.format(file_name))
        self.expandToDepth(display_depth)

        # Fill highlight column for remainder of nodes
        for elem in to_be_updated:
            elem.setText(AstTreeWidget.COL_HIGHLIGHT, "{} : {}".format(state['to'], "... : ..."))


def class_name(obj):
    """ Returns the class name of an object"""
    return obj.__class__.__name__
