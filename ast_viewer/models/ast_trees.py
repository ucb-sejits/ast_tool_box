from __future__ import print_function

__author__ = 'Chick Markley'

import ast
import inspect
import copy

class AstTrees(object):
    def __init__(self):
        self.ast_trees = []

    def count(self):
        return len(self.ast_trees)

    def __iter__(self):
        return iter(self.ast_trees)

    def create_transformed_child(self, ast_tree_item, ast_transform_item=None):
        child_ast_tree = copy.deepcopy(ast_tree_item.ast_tree)
        if ast_transform_item:
            ast_transform_item.transform_in_place(child_ast_tree)
        new_ast_tree_item = AstTreeItem(child_ast_tree, parent_link=ast_tree_item)

        self.ast_trees.append(new_ast_tree_item)
        return new_ast_tree_item

    def new_item_from_source(self, source_text):
        new_ast_item = AstTreeItem.from_source(source_text)
        self.ast_trees.append(new_ast_item)
        return new_ast_item

    def new_item_from_file(self, file_name):
        new_ast_item = AstTreeItem.from_file(file_name)
        self.ast_trees.append(new_ast_item)
        return new_ast_item


class AstTreeItem(object):
    """
    represent an ast and where it came from
    """
    def __init__(self, ast_tree, parent_link=None, source=None, file_name=None):
        self.ast_tree = ast_tree
        self.parent_link = parent_link
        self.source = source
        self.file_name = file_name

    def get_parent_link(self):
        return self.parent_link

    @staticmethod
    def from_source(source_text):
        return AstTreeItem(ast.parse(source_text), source_text)

    @staticmethod
    def from_file(file_name):
        with open(file_name, "r") as file_handle:
            source = file_handle.read()
            return AstTreeItem(source, file_name=file_name)
        return None


class AstLink(object):
    def __init__(self, parent_ast_tree=None, parent_ast_node=None, transform_item=None):
        self.parent_ast_tree = parent_ast_tree
        self.parent_ast_node = parent_ast_node if parent_ast_node else parent_ast_tree
        self.transform_item = transform_item
