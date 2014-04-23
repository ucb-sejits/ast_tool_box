from __future__ import print_function

import ast
import sys
import os
import inspect
from pprint import pprint
from operator import methodcaller
from PySide import QtCore, QtGui

from ast_viewer.models.transform_models.transform_file import TransformFile, TransformPackage
from ast_viewer.controllers.tree_transform_controller import TreeTransformController
from ast_viewer.views.transform_views.transform_pane import TransformPane
from ctree.codegen import CodeGenVisitor
from ast_viewer.util import Util


class TransformPresenter(object):
    """
    keeps track of transforms (subclasses of ast.NodeTransformers or
    ctree.codegen.CodeGenVisitor) that are found in either a package
    or a file, transforms can be applied to the code objects in the
    code pane
    """
    def __init__(self, tree_transform_controller=None, start_packages=None):
        assert isinstance(tree_transform_controller, TreeTransformController)

        self.code_presenter = None
        self.tree_transform_controller = tree_transform_controller
        self.transform_pane = TransformPane(transform_presenter=self)

        self.transform_collections = []
        self.transforms_loaded = []
        self.transforms_by_name = {}

    def transform_items(self):
        for collection in self.transform_collections:
            for item in collection.node_transforms:
                yield item
            for item in collection.code_generators:
                yield item

    def reload_transforms(self):
        """
        reload all transforms, clearing everything first
        """
        to_load = self.transform_collections[:]

        for module in to_load:
            TransformPresenter.delete_module(module.package_name)

        self.transform_collections = []
        self.load_files(
            map(lambda x: x.collection_name, to_load)
        )

    def set_code_presenter(self, code_presenter):
        # assert isinstance(code_presenter, controllers.TransformPresenter)
        self.code_presenter = code_presenter

    def apply_transform(self, code_item, transform_item):
        self.code_presenter.apply_transform(code_item=code_item, transform_item=transform_item)

    def current_item(self):
        return self.transform_pane.current_item()

    def apply_current_transform(self):
        transform_item = self.current_item().source
        print("just got transform item %s" % transform_item)
        code_item = self.code_presenter.current_item()
        self.apply_transform(code_item, transform_item)

    def clear(self):
        self.transforms_by_name = {}

    def count(self):
        """return current transforms"""
        return len(list(self.transform_items()))

    # def __getitem__(self, item):
    #     if isinstance(item, int):
    #         return self.transform_items[item]
    #     elif isinstance(item, str):
    #         return self.transforms_by_name[item]

    # def get_valid_index(self, index):
    #     """
    #     convenience method for checking index
    #     if index is a string make it an int
    #     None returned if failed to convert or index out of range
    #     """
    #     if not isinstance(index, int):
    #         try:
    #             index = int(index)
    #         except ValueError:
    #             return None
    #
    #     if index >= 0:
    #         if index < len(self.transform_items):
    #             return index
    #     return None

    # def get_instance_by_name(self, transform_name):
    #     transform_item = self.transforms_by_name[transform_name]
    #     return transform_item.get_instance()

    # def __iter__(self):
    #     return iter(self.transform_items)

    def load_file(self, file_name):
        print("loading %s" % file_name)
        if not os.path.isfile(file_name):
            transform_package = TransformPackage(file_name)
            if len(transform_package.node_transforms) > 0:
                self.transform_collections.append(transform_package)
            else:
                TransformPane.show_error("Cannot open %s" % file_name)
            return

        transform_file = TransformFile(file_name)
        self.transform_collections.append(transform_file)

    def load_files(self, file_names):
        for file_name in file_names:
            self.load_file(file_name)

        self.transform_pane.transform_tree_widget.build(self.transform_collections)

    @staticmethod
    def delete_module(module_name):
        Util.clear_classes_and_reload_package(module_name)


