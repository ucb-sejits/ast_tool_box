import unittest
import ast
import inspect

from nose.tools import assert_greater, assert_is_instance, assert_equal, assert_not_equal
from nose.tools import assert_is_none, assert_is_not_none

from ast_tool_box.models.ast_tree_manager import AstTreeItem, AstLink, AstTreeManager
from ast_tool_box.models.ast_transformer_manager import AstTransformerItem
from ast_tool_box.transformers.identity_transform import NoisyIdentityTransform, IdentityTransform


class TestAstTrees(unittest.TestCase):
    def test_basic_load(self):
        trees = AstTreeManager()

        assert_equal(trees.count(), 0)

        test_ast = trees.new_item_from_source(inspect.getsource(sample_code))

        assert_equal(trees.count(), 1)
        assert_is_not_none(test_ast)

        ti = AstTransformerItem(NoisyIdentityTransform)
        trees.create_transformed_child(test_ast, ast_transform_item=ti)

        assert_equal(trees.count(), 2)


class TestAstTree(unittest.TestCase):
    def test_from_source(self):
        source = ""
        nti = AstTreeItem(inspect.getsource(sample_code))

        assert_is_none(nti.get_parent_link())


class TestAstLink(unittest.TestCase):
    def test_link(self):
        tree1 = AstTreeItem(inspect.getsource(sample_code))

        tree1
        ast_link = AstLink()


def sample_code(x):
    return x * x
