from __future__ import print_function

__author__ = 'Chick Markley'

import ast
import os
import ast_viewer.models.transform_models.transform_model as transform_model


class CodeItem(object):
    """
    Base class for python source, ast trees and generated c code
    """
    def __init__(self, code=None, code_name=None, path_name=None, parent_link=None):
        assert parent_link is None or isinstance(parent_link, CodeTransformLink)
        self.code = code
        self.code_name = code_name
        self.path_name = path_name
        self.parent_code_item = parent_link

    def name(self):
        self.code_name

    def path(self):
        self.path_name

    def has_parent(self):
        return self.parent_code_item is not None and self.parent_code_item.code_item is not None


class AstTreeItem(CodeItem):
    """
    represent an ast and where it came from
    """
    def __init__(self, ast_tree, parent_link=None, source=None, file_name=None, name=None):
        base_name = None if file_name is None else os.path.basename(file_name)
        name = name if name else base_name if base_name else "Derived"
        super(AstTreeItem, self).__init__(
            ast_tree,
            code_name=name,
            path_name=file_name,
            parent_link=parent_link
        )
        self.ast_tree = ast_tree

    @staticmethod
    def from_source(source_text):
        return AstTreeItem(ast.parse(source_text), source_text)

    @staticmethod
    def from_file(file_name):
        with open(file_name, "r") as file_handle:
            source_text = file_handle.read()
            return AstTreeItem(ast.parse(source_text), source=source_text, file_name=file_name)
        return None


class FileItem(CodeItem):
    def __init__(self, code=None, file_name=None, parent_link=None):
        super(FileItem, self).__init__(
            code=code, code_name=os.path.basename(file_name), path_name=file_name
        )


class GeneratedCodeItem(CodeItem):
    def __init__(self, code=None, parent_link=None, parent_ast_node=None, transform_item=None):
        super(GeneratedCodeItem, self).__init__(
            code,
            parent_link=parent_link
        )


class CodeTransformLink(object):
    def __init__(self, code_item=None, transform_item=None):
        assert isinstance(code_item, CodeItem)
        assert transform_item is None or isinstance(transform_item, transform_model.TransformItem)
        self.code_item = code_item
        self.transform_item = transform_item