import unittest
import ast
import inspect

from nose.tools import assert_greater, assert_is_instance, assert_equal, assert_not_equal

from ast_viewer.models.ast_transformer_manager import AstTransformerManager
from ast_viewer.models.ast_transformer_manager import AstTransformerItem
from ast_viewer.transformers.identity_transform import NoisyIdentityTransform, IdentityTransform


class TestTransformers(unittest.TestCase):
    def test_basic_load(self):
        ntm = AstTransformerManager()
        ntm.get_ast_transformers("ast_viewer.transformers.identity_transform")
        ntm.reload()

        assert_greater(ntm.count(), 0)

    def test_get_transformer(self):
        ntm = AstTransformerManager()
        ntm.reload()

        ntsc = ntm.get_instance_by_name('IdentityTransform')

        assert_is_instance(ntsc, IdentityTransform)


class TestTransformerItems(unittest.TestCase):
    def test_basics(self):
        nti = AstTransformerItem(IdentityTransform)

        assert_equal(nti.name(), "IdentityTransform")
        assert_equal(nti.package(), "ast_viewer.transformers.identity_transform")

    def test_no_arg_transformer(self):
        nti = AstTransformerItem(IdentityTransform)

        nodes_visited = []
        tree = ast.parse(inspect.getsource(sample_code))

        new_tree = nti.copy_and_transform(tree)

        assert_not_equal(tree, new_tree)

    def test_one_arg_transformer(self):
        """
        this does not work, how do we pass arguments to
        transformers that require them
        """
        pass
        # nti = AstTransformerItem(IdentityTransform)
        #
        # nodes_visited = []
        # tree = ast.parse(inspect.getsource(sample_code))
        #
        # def save_node(node):
        #     nodes_visited.append(node)
        #
        # new_tree = nti.copy_and_transform(tree, save_node)
        #
        # assert_greater(len(nodes_visited), 0)
        # assert_not_equal(tree, new_tree)


def sample_code(x):
    return x * x
