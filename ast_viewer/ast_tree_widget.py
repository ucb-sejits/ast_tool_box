__author__ = 'Chick Markley'

from PySide import QtGui
import types

# Tree column indices
COL_NODE = 0
COL_FIELD = 1
COL_CLASS = 2
COL_VALUE = 3
COL_POS = 4
COL_HIGHLIGHT = 5

DEBUGGING = False


class AstTreeWidget(QtGui.QTreeWidget):
    def __init__(self):
        super(AstTreeWidget, self).__init__()

        self.setColumnCount(2)
        self.setHeaderLabels(
            ["Node", "Field", "Class", "Value", "Line : Col", "Highlight"]
        )
        self.header().resizeSection(COL_NODE, 250)
        self.header().resizeSection(COL_FIELD, 80)
        self.header().resizeSection(COL_CLASS, 80)
        self.header().resizeSection(COL_VALUE, 80)
        self.header().resizeSection(COL_POS, 80)
        self.header().resizeSection(COL_HIGHLIGHT, 100)
        self.setColumnHidden(COL_HIGHLIGHT, not DEBUGGING)
        self.header().setStretchLastSection(True)

    def make_tree_from(self, ast):
        """
        Populates the tree widget.
        """
        self.clear()

        # State we keep during the recursion.
        # Is needed to populate the selection column.
        to_be_updated = list([])
        state = {'from': '? : ?', 'to': '1 : 0'}

        def add_node(ast_node, parent_item, field_label):
            """ Helper function that recursively adds nodes.

                :param parent_item: The parent QTreeWidgetItem to which this node will be added
                :param field_label: Labels how this node is known to the parent
            """
            node_item = QtGui.QTreeWidgetItem(parent_item)

            if hasattr(ast_node, 'lineno'):
                position_str = "{:d} : {:d}".format(ast_node.lineno, ast_node.col_offset)

                # If we find a new position string we set the items found since the last time
                # to 'old_line : old_col : new_line : new_col' and reset the list
                # of to-be-updated nodes
                if position_str != state['to']:
                    state['from'] = state['to']
                    state['to'] = position_str
                    for elem in to_be_updated:
                        elem.setText(COL_HIGHLIGHT, "{} : {}".format(state['from'], state['to']))
                    to_be_updated[:] = [node_item]
                else:
                    to_be_updated.append(node_item)
            else:
                to_be_updated.append(node_item)
                position_str = ""

            # Recursively descent the AST
            if isinstance(ast_node, ast.AST):
                value_str = ''
                node_str = "{} = {}".format(field_label, class_name(ast_node))
                for key, val in ast.iter_fields(ast_node):
                    add_node(val, node_item, key)
            # elif type(ast_node) == types.ListType or type(ast_node) == types.TupleType:
            elif isinstance(ast_node, types.ListType) or isinstance(ast_node,types.TupleType):
                value_str = ''
                node_str = "{} = {}".format(field_label, class_name(ast_node))
                for idx, elem in enumerate(ast_node):
                    add_node(elem, node_item, "{}[{:d}]".format(field_label, idx))
            else:
                value_str = repr(ast_node)
                node_str = "{} = {}".format(field_label, value_str)

            node_item.setText(COL_NODE, node_str)
            node_item.setText(COL_FIELD, field_label)
            node_item.setText(COL_CLASS, class_name(ast_node))
            node_item.setText(COL_VALUE, value_str)
            node_item.setText(COL_POS, position_str)

        # End of helper function

        syntax_tree = ast.parse(self._source_code, filename=self._file_name, mode=self._mode)
        #logger.debug(ast.dump(syntax_tree))
        add_node(syntax_tree, self.ast_tree, '"{}"'.format(self._file_name))
        self.ast_tree.expandToDepth(1)

        # Fill highlight column for remainder of nodes
        for elem in to_be_updated:
            elem.setText(COL_HIGHLIGHT, "{} : {}".format(state['to'], "... : ..."))


def class_name(obj):
    """ Returns the class name of an object"""
    return obj.__class__.__name__

