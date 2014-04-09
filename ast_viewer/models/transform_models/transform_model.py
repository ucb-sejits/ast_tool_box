from __future__ import print_function

__author__ = 'Chick Markley'

import sys
import ast
from ast_viewer.util import Util
from ctree.codegen import CodeGenVisitor


class TransformItem(object):
    def __init__(self, transform):
        self.transform = transform

    def package(self):
        return self.transform.__module__

    def name(self):
        print("self.transform %s" % self.transform)
        return self.transform.__name__

    def get_instance(self):
        return self.transform()


class AstTransformItem(TransformItem):
    """
    Basic wrapper of an ast.NodeTransform with convenience methods
    for creating, getting names etc
    """
    def __init__(self, node_transform):
        assert issubclass(node_transform, ast.NodeTransformer), "bad node_transform %s" % node_transform
        super(AstTransformItem, self).__init__(node_transform)
        self.node_transform = node_transform


class CodeGeneratorItem(TransformItem):
    """
    Basic wrapper of an CodeGenVisitor with convenience methods
    for creating, getting names etc
    """
    def __init__(self, code_generator):
        assert issubclass(code_generator, CodeGenVisitor)
        super(CodeGeneratorItem, self).__init__(code_generator)
        self.code_generator = self.transform


class AstParseItem(TransformItem):
    def __init__(self):
        # super(AstParseItem, self).__init__(self)
        pass

    def package(self):
        """override base class method"""
        return ""

    def name(self):
        """override base class method"""
        return "ast.parse"

    def get_instance(self):
        """override base class method"""
        return None
