import unittest

import ast
from nose.tools import assert_greater
from ast_viewer.transformers import NodeTransformerManager

class NodeTransformerSubClass(ast.NodeTransformer):
    pass

class TestTransformers(unittest.TestCase):
    def test_basic_load(self):
        ntm = NodeTransformerManager()
        ntm.reload()

        assert_greater(ntm.all_transformers, 0)
