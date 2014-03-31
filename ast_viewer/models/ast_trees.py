from __future__ import print_function

__author__ = 'Chick Markley'

import ast
import inspect

class AstTrees(object):
    def __init__(self):
        self.ast_trees = []

    def count(self):
        return len(self.ast_trees)

    def __iter__(self):
        return iter(self.ast_trees)


class AstTree(object):
    """
    represent an ast and where it came from
    """
    def __init__(self, ast_tree, parent_link=None, source=None, file_name=None):
        self.ast_tree = ast_tree
        self.parent_link = parent_link
        self.source = source
        self.file_name = file_name

    @staticmethod
    def from_source(source_text):
        return AstTree(ast.parse(source_text), source_text)

    @staticmethod
    def from_file(file_name):
        with open(file_name, "r") as file_handle:
            source = file_handle.read()
            return AstTree(source, file_name=file_name)
        return None


class AstLink(object):
    def __init__(self, parent_ast_tree=None, parent_ast_node=None, transform_item=None):
        self.parent_ast_tree = parent_ast_tree
        self.parent_ast_node = parent_ast_node if parent_ast_node else parent_ast_tree
        self.transform_item = transform_item

    def parent_link(self):
        return self.parent_link()

