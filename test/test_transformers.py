import unittest
import ast

from nose.tools import assert_greater, assert_is_instance

from ast_viewer.models.transformers import NodeTransformerManager


class NodeTransformerSubclass(ast.NodeTransformer):
    pass


class TestTransformers(unittest.TestCase):
    def test_basic_load(self):
        ntm = NodeTransformerManager()
        ntm.reload()

        assert_greater(ntm.all_transformers, 0)

    def test_get_transformer(self):
        ntm = NodeTransformerManager()
        ntm.reload()

        ntsc = ntm.get_instance('NodeTransformerSubclass')

        assert_is_instance(ntsc, NodeTransformerSubclass)