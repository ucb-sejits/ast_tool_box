import unittest
import ast
import inspect

from nose.tools import assert_greater, assert_is_instance, assert_equal, assert_not_equal
from nose.tools import assert_is_none, assert_is_not_none

from ast_viewer.models.ast_trees import AstTreeItem, AstLink, AstTreeManager
from ast_viewer.models.node_transformers import NodeTransformerItem
from ast_viewer.transformers.identity_transform import NoisyIdentityTransform, IdentityTransform


class TestAstTrees(unittest.TestCase):
    def test_basic_load(self):
        trees = AstTreeManager()

        assert_equal(trees.count(), 0)

        test_ast = trees.new_item_from_source(inspect.getsource(sample_code))

        assert_equal(trees.count(), 1)
        assert_is_not_none(test_ast)

        ti = NodeTransformerItem(NoisyIdentityTransform)
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
