from __future__ import print_function

__author__ = 'Chick Markley'

import ast
import copy


class AstTreeManager(object):
    def __init__(self):
        self.ast_trees = []

    def clear(self):
        self.ast_trees = []

    def count(self):
        return len(self.ast_trees)

    def __getitem__(self, item):
        return self.ast_trees[item]

    def __iter__(self):
        return iter(self.ast_trees)

    def get_valid_index(self, index):
        """
        convenience method for checking index,
        if index is a string it will be converted to int
        None returned if failed to convert or index out of range
        """
        if not isinstance(index, int):
            try:
                index = int(index)
            except ValueError:
                return None

        if index >= 0:
            if index < len(self.ast_trees):
                return index
        return None

    def create_transformed_child(self, ast_tree_item, ast_transform_item=None, name=None):
        # child_ast_tree = copy.deepcopy(ast_tree_item.ast_tree)
        # if ast_transform_item:
        #     child_ast_tree = ast_transform_item.transform(child_ast_tree)
        child_ast_tree = ast_transform_item.copy_and_transform(ast_tree_item.ast_tree)
        link = AstLink(parent_ast_tree=ast_tree_item, transform_item=ast_transform_item)
        new_ast_tree_item = AstTreeItem(child_ast_tree, parent_link=link, name=name)

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

    def delete(self, ast_tree_item):
        """
        delete an ast tree from manager
        ast_tree_item can be AstTreeItem or index or string
        representing index
        """
        if isinstance(ast_tree_item, AstTreeItem):
            self.ast_trees.remove(ast_tree_item)
            return True
        else:
            index = self.get_valid_index(ast_tree_item)
            if index:
                self.ast_trees.remove(self.ast_trees[index])
                return True
        return False


class AstTreeItem(object):
    """
    represent an ast and where it came from
    """
    def __init__(self, ast_tree, parent_link=None, source=None, file_name=None, name=None):
        self.ast_tree = ast_tree
        self.parent_link = parent_link
        self.source = source
        self.file_name = file_name
        self.name = name if name else file_name if file_name else "Derived"

    @staticmethod
    def from_source(source_text):
        return AstTreeItem(ast.parse(source_text), source_text)

    @staticmethod
    def from_file(file_name):
        with open(file_name, "r") as file_handle:
            source_text = file_handle.read()
            return AstTreeItem(ast.parse(source_text), source=source_text, file_name=file_name)
        return None


class AstLink(object):
    def __init__(self, parent_ast_tree=None, parent_ast_node=None, transform_item=None):
        self.parent_ast_tree = parent_ast_tree
        self.parent_ast_node = parent_ast_node if parent_ast_node else parent_ast_tree
        self.transform_item = transform_item
