from __future__ import print_function

from ast_viewer.models.ast_tree_manager import AstTreeManager
from ast_viewer.models.node_transformer_manager import AstTransformerManager


class TreeTransformController(object):
    def __iter__(self):
        self.ast_tree_manager = AstTreeManager()
        self.node_transformer_manager = AstTransformerManager()