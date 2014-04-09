from __future__ import print_function

__author__ = 'Chick Markley'

import sys
import ast
from ast_viewer.util import Util
from ctree.codegen import CodeGenVisitor


class TransformManager(object):
    """
    manage the list of all transforms items that have been discovered.  items
    will all subclasses of ast.NodeTransformer, and ctree CodeGenerator
    TODO: Figure out how to use transformers whose constructors require parameters
    """
    def __init__(self):
        self.transform_items = []
        self.transforms_by_name = {}

    def clear(self):
        self.transform_items = []
        self.transforms_by_name = {}

    def count(self):
        """return current transforms"""
        return len(self.transform_items)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.transform_items[item]
        elif isinstance(item, str):
            return self.transforms_by_name[item]

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
            if index < len(self.transform_items):
                return index
        return None

    def get_ast_transforms(self, module_name):
        """Use module_name to discover some transforms"""

        try:
            __import__(module_name)
            self.reload()
        except Exception as exception:
            print("cannot load %s message %s" % (module_name, exception.message))

    def reload(self):
        """rebuild list of all in memory subclasses of ast.Nodetransform"""

        self.transform_items = map(
            lambda transform: AstTransformItem(transform),
            ast.NodeTransformer.__subclasses__()
        )

        self.transform_items += map(
            lambda transform: CodeGeneratorItem(transform),
            CodeGenVisitor.__subclasses__()
        )

        for transform_item in self.transform_items:
            print("loaded %s" % transform_item.name())
            self.transforms_by_name[transform_item.name()] = transform_item

    def get_instance_by_name(self, transform_name):
        transform_item = self.transforms_by_name[transform_name]
        return transform_item.get_instance()

    def __iter__(self):
        return iter(self.transform_items)

    def load_transforms_by_file_name(self, file_name):
        """Todo"""
        pass

    def load_transforms(self, key):
        path, package_name = Util.path_to_path_and_package(key)

        print("path %s package %s" % (path, package_name))

        if not path in sys.path:
            sys.path.append(path)

        self.get_ast_transforms(package_name)
        self.reload()

        print("AsttransformManager %s" % self)


if __name__ == '__main__':
    ntm = TransformManager()

    ntm.get_ast_transforms('ctree.transformations')


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