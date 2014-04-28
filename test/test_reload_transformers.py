import unittest
import ast
import inspect
import subprocess
from sys import modules
import imp
from ast_tool_box.util import Util
from pprint import pprint

from nose.tools import assert_greater, assert_is_instance, assert_equal, assert_not_equal

from ast_tool_box.models.ast_transformer_manager import AstTransformerManager
from ast_tool_box.models.ast_transformer_manager import AstTransformerItem
from ast_tool_box.transformers.identity_transform import NoisyIdentityTransform, IdentityTransform

file1 = """
import ast


class Transformer1(ast.NodeTransformer):
    pass
"""

file2 = """
import ast

class Transformer1(ast.NodeTransformer):
    pass


class Transformer2(Transformer1):
    pass


class Transformer3(Transformer2):
    pass

"""


class TestReloadTransformers(unittest.TestCase):
    def test_basic_load(self):

        with open('transform.py', "w+") as f:
            f.write(file2)

        name = 'test.transform'
        __import__(name)

        assert name in modules

        loaded_module = modules[name]

        transformer1 = loaded_module.__dict__['Transformer1']
        assert issubclass(transformer1, ast.NodeTransformer)

        transformer2 = loaded_module.__dict__['Transformer2']
        assert issubclass(transformer2, ast.NodeTransformer)

        transformer3 = loaded_module.__dict__['Transformer3']
        assert issubclass(transformer3, ast.NodeTransformer)

        subprocess.call("rm -f transform.pyc", shell=True)
        with open('transform.py', "w+") as f:
            f.write(file1)

        imp.reload(loaded_module)

        #loaded_module = modules[name]
        print(loaded_module)

        Util.clear_classes_and_reload_package(name)
        assert not 'Transformer2' in loaded_module.__dict__

        loaded_module = modules[name]
        transformer1 = loaded_module.__dict__['Transformer1']
        assert issubclass(transformer1, ast.NodeTransformer)

        pprint(loaded_module.__dict__)
        assert not 'Transformer2' in loaded_module.__dict__
        assert not 'Transformer3' in loaded_module.__dict__

        subprocess.call("rm -f transform.py", shell=True)

