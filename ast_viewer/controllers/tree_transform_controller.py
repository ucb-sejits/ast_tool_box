from __future__ import print_function

from ast_viewer.models.ast_tree_manager import AstTreeManager
from ast_viewer.models.ast_transformer_manager import AstTransformerManager


class TreeTransformController(object):
    def __init__(self):
        self.ast_tree_manager = AstTreeManager()
        self.ast_transformer_manager = AstTransformerManager()

    def clear(self):
        self.ast_tree_manager.clear()
        self.ast_transformer_manager.clear()

    def apply_transform(self, tree, transform):
        """
        creates a new ast_tree item by applying
        transform to tree, updates the controllers
        internals to track that
        """
        if isinstance(tree, int):
            tree = self.ast_tree_manager[tree]
        if isinstance(transform, int):
            transform = self.ast_transformer_manager[transform]

        new_ast_tree = self.ast_tree_manager.create_transformed_child(
            tree, transform
        )
        return new_ast_tree
