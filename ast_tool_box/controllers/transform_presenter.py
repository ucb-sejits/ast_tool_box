from __future__ import print_function

import ast
import sys
import os
import inspect
from pprint import pprint
from operator import methodcaller
from PySide import QtCore, QtGui

from ast_tool_box.models.transform_models.transform_file import TransformFile, TransformPackage
from ast_tool_box.controllers.tree_transform_controller import TreeTransformController
from ast_tool_box.views.transform_views.transform_pane import TransformPane
from ctree.codegen import CodeGenVisitor
from ast_tool_box.util import Util


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

    def load_file(self, file_name):
        print("loading %s" % file_name)
        if not os.path.isfile(file_name):
            transform_package = TransformPackage(file_name)
            if len(transform_package.node_transforms) > 0 or len(transform_package.code_generators) > 0:
                self.transform_collections.append(transform_package)
            else:
                TransformPane.show_error("Cannot open %s" % file_name)
            return

        transform_file = TransformFile(file_name)
        self.transform_collections.append(transform_file)
        if transform_file.load_error_info:
            message = transform_file.load_error_info
            self.transform_pane.show_error(message)

    def load_files(self, file_names):
        for file_name in file_names:
            self.load_file(file_name)

        self.transform_pane.transform_tree_widget.build(self.transform_collections)

    def update_file(self, transform_collection):
        TransformPresenter.delete_module(transform_collection.package_name)
        transform_collection.update()
        self.transform_pane.transform_tree_widget.rebuild(transform_collection)

    @staticmethod
    def delete_module(module_name):
        Util.clear_classes_in_package(module_name)


