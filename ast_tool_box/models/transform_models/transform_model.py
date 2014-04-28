from __future__ import print_function

__author__ = 'Chick Markley'

import sys
import ast
from ast_tool_box.util import Util
from ctree.codegen import CodeGenVisitor


class TransformItem(object):
    def __init__(self, transform, package_name=''):
        self.transform = transform
        self._package_name = package_name

    def package_name(self):
        return self._package_name

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
    def __init__(self, node_transform, package_name=''):
        assert issubclass(node_transform, ast.NodeTransformer), "bad node_transform %s" % node_transform
        super(AstTransformItem, self).__init__(node_transform, package_name=package_name)
        self.node_transform = node_transform


class CodeGeneratorItem(TransformItem):
    """
    Basic wrapper of an CodeGenVisitor with convenience methods
    for creating, getting names etc
    """
    def __init__(self, code_generator, package_name=''):
        assert issubclass(code_generator, CodeGenVisitor)
        super(CodeGeneratorItem, self).__init__(code_generator, package_name=package_name)
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
