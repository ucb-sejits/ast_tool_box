import unittest
import ast
import inspect

from nose.tools import assert_greater, assert_is_instance, assert_equal, assert_not_equal
from nose.tools import assert_is_none

from ast_viewer.models.ast_trees import AstTree, AstLink, AstTrees
from ast_viewer.models.transformers import NodeTransformerItem
from ast_viewer.transformers.identity_transform import NoisyIdentityTransform, IdentityTransform


class TestAstTrees(unittest.TestCase):
    def test_basic_load(self):
        trees = AstTrees()

        assert_greater(trees.count(), 0)


class TestAstTree(unittest.TestCase):
    def test_from_source(self):
        source = ""
        nti = AstTree(inspect.getsource(sample_code))

        assert_is_none(nti.parent_link())


def sample_code(x):
    return x * x
