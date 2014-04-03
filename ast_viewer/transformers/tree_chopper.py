from __future__ import print_function

import ast


class TreeChopperTransform(ast.NodeTransformer):
    def visit(self, node):
        print("node %s" % node)
        stump_node = ast.Pass()
        return stump_node
