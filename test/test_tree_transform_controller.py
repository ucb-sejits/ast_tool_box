import unittest

from nose.tools import assert_greater, assert_is_instance, assert_equal, assert_not_equal
from nose.tools import assert_is_none, assert_is_not_none

from ast_tool_box.controllers.tree_transform_controller import TreeTransformController
from ast_tool_box.models.ast_tree_manager import AstTreeManager, AstTreeItem, AstLink
from ast_tool_box.models.ast_transformer_manager import AstTransformerManager, AstTransformerItem

class TestTreeTransformController(unittest.TestCase):
    def test_create(self):
        ttc = TreeTransformController()

        assert_is_instance(ttc, TreeTransformController)
        assert_is_instance(ttc.ast_tree_manager, AstTreeManager)
        assert_is_instance(ttc.ast_transformer_manager, AstTransformerManager)

    def test_load_ast(self):
        ttc = TreeTransformController()
        ttc.ast_tree_manager.new_item_from_file("sample.py")

        assert_equal(ttc.ast_tree_manager.count(), 1)
        assert_is_instance(ttc.ast_tree_manager[0], AstTreeItem)

    def test_load_transforms(self):
        ttc = TreeTransformController()
        ttc.ast_transformer_manager.get_ast_transformers("ctree.transformations")

        assert_greater(ttc.ast_transformer_manager.count(), 1)
        assert_is_instance(ttc.ast_transformer_manager[0], AstTransformerItem)

    def test_apply_transforms(self):
        ttc = TreeTransformController()
        ttc.ast_transformer_manager.get_ast_transformers("ctree.transformations")
        ttc.ast_tree_manager.new_item_from_file("sample.py")

        new_ast_item = ttc.apply_transform(0, 0)

        assert_is_instance(new_ast_item, AstTreeItem)
        assert_equal(new_ast_item, ttc.ast_tree_manager[1])

        assert_is_instance(new_ast_item.parent_link, AstLink)
        assert_equal(new_ast_item.parent_link.parent_ast_tree, ttc.ast_tree_manager[0])