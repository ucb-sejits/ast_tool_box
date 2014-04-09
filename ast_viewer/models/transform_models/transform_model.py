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
        return self.transform.__name__

    def get_instance(self):
        return self.transform()


class AstTransformItem(TransformItem):
    """
    Basic wrapper of an ast.NodeTransform with convenience methods
    for creating, getting names etc
    """
    def __init__(self, node_transform):
        assert isinstance(node_transform, ast.NodeTransformer)
        super(AstTransformItem, self).__init__(node_transform.__name__)
        self.node_transform = node_transform


class CodeGeneratorItem(TransformItem):
    """
    Basic wrapper of an CodeGenVisitor with convenience methods
    for creating, getting names etc
    """
    def __init__(self, code_generator):
        assert isinstance(code_generator, CodeGenVisitor)
        super(CodeGeneratorItem, self).__init__(code_generator)
        self.code_generator = self.transform


class AstParseItem(TransformItem):
    def __init__(self):
        super(AstParseItem, self).__init__(self)

    def package(self):
        """override base class method"""
        return ""

    def name(self):
        """override base class method"""
        return "ast.parse"

    def get_instance(self):
        """override base class method"""
        return None
