from __future__ import print_function

__author__ = 'Chick Markley'

import sys
import ast
import copy
from ast_tool_box.util import Util
from ctree.codegen import CodeGenVisitor


class AstTransformerManager(object):
    """
    manage the list of all transformer items that have been discovered.  items
    are all subclasses of ast.NodeTransformer
    TODO: Figure out how to use transformers whose constructors require parameters
    """
    def __init__(self):
        self.transformer_items = []
        self.transformers_by_name = {}

    def clear(self):
        self.transformer_items = []
        self.transformers_by_name = {}

    def count(self):
        """return current transformers"""
        return len(self.transformer_items)

    def __getitem__(self, item):
        return self.transformer_items[item]

    def get_valid_index(self, index):
        """
        convenience method for checking index
        if index is a string make it an int
        None returned if failed to convert or index out of range
        """
        if not isinstance(index, int):
            try:
                index = int(index)
            except ValueError:
                return None

        if index >= 0:
            if index < len(self.transformer_items):
                return index
        return None

    def get_ast_transformers(self, module_name):
        """Use module_name to discover some transformers"""

        try:
            __import__(module_name)
            self.reload()
        except Exception as exception:
            print("cannot load %s message %s" % (module_name, exception.message))

    def reload(self):
        """rebuild list of all in memory subclasses of ast.NodeTransformer"""

        self.transformer_items = map(
            lambda transformer: AstTransformerItem(transformer),
            ast.NodeTransformer.__subclasses__()
        )

        self.transformer_items += map(
            lambda transformer: AstTransformerItem(transformer),
            CodeGenVisitor.__subclasses__()
        )

        for transformer_item in self.transformer_items:
            print("loaded %s" % transformer_item.name())
            self.transformers_by_name[transformer_item.name()] = transformer_item

    def get_instance_by_name(self, transformer_name):
        transformer_item = self.transformers_by_name[transformer_name]
        return transformer_item.get_instance()

    def __iter__(self):
        return iter(self.transformer_items)

    def load_transformers_by_file_name(self, file_name):
        """Todo"""
        pass

    def load_transformers(self, key):
        path, package_name = Util.path_to_path_and_package(key)

        print("path %s package %s" % (path, package_name))

        if not path in sys.path:
            sys.path.append(path)

        self.get_ast_transformers(package_name)
        self.reload()

        print("AstTransformerManager %s" % self)


if __name__ == '__main__':
    ntm = AstTransformerManager()

    ntm.get_ast_transformers('ctree.transformations')


class AstTransformerItem(object):
    """
    Basic wrapper of an ast.NodeTransformer with convenience methods
    for creating, getting names etc
    """
    def __init__(self, node_transformer):
        self.node_transformer = node_transformer

    def package(self):
        return self.node_transformer.__module__

    def name(self):
        return self.node_transformer.__name__

    def get_instance(self):
        return self.node_transformer()

    def transform(self, *args, **kwargs):
        """Transform a tree in place"""
        if args:
            transformer = self.node_transformer(*args[1:], **kwargs)
            return transformer.visit(args[0])
        return None

    def copy_and_transform(self, *args, **kwargs):
        if args:
            new_ast = copy.deepcopy(args[0])
            new_args = [new_ast]
            new_args += args[1:]

            new_ast = self.transform(*new_args, **kwargs)
            return new_ast
        return None


