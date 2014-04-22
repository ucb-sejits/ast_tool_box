from __future__ import print_function

import ast
import sys
import os
import inspect
from pprint import pprint
from operator import methodcaller
from PySide import QtCore, QtGui

import ast_viewer.controllers as controllers
import ast_viewer.models.transform_models.transform_model as transform_model
from ast_viewer.models.transform_models.transform_file import TransformFile, TransformThing
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

        self.load_name_list = []
        self.transforms_loaded = []
        self.transform_items = []
        self.transforms_by_name = {}

    def reload_transforms(self):
        to_load = self.transforms_loaded[:]

        for module in to_load:
            TransformPresenter.delete_module(module)

        self.transforms_loaded = []
        print("calling load transforms now")
        self.load_transforms(to_load)

    def set_code_presenter(self, code_presenter):
        # assert isinstance(code_presenter, controllers.TransformPresenter)
        self.code_presenter = code_presenter

    def apply_transform(self, code_item, transform_item):
        self.code_presenter.apply_transform(code_item=code_item, transform_item=transform_item)

    def current_item(self):
        return self.transform_pane.current_item()

    def apply_current_transform(self):
        transform_item = self.current_item().transform_item
        code_item = self.code_presenter.current_item()
        self.apply_transform(code_item, transform_item)

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
            # print("--> importing module %s" % module_name)
            # pprint(sys.path)
            __import__(module_name)
        except Exception as exception:
            print("cannot load %s message %s" % (module_name, exception.message))

    def reload(self):
        """rebuild list of all in memory subclasses of ast.NodeTransformer"""

        self.transform_items = []
        for transform_name in self.transforms_loaded:
            module = sys.modules[transform_name]

            for key in module.__dict__:
                thing = module.__dict__[key]
                if inspect.isclass(thing):
                    if issubclass(thing, ast.NodeTransformer):
                        if thing.__name__ != "NodeTransformer":
                            self.transform_items.append(
                                transform_model.AstTransformItem(thing, package_name=transform_name)
                            )
                    if issubclass(thing, CodeGenVisitor):
                        if thing.__name__ != "CodeGenVisitor":
                            self.transform_items.append(transform_model.CodeGeneratorItem(thing))

        self.transform_items.sort(key=methodcaller('name'))
        for transform_item in self.transform_items:
            # print("loaded %s" % transform_item.name())
            self.transforms_by_name[transform_item.name()] = transform_item

    def get_instance_by_name(self, transform_name):
        transform_item = self.transforms_by_name[transform_name]
        return transform_item.get_instance()

    def __iter__(self):
        return iter(self.transform_items)

    def load_file(self, file_name):
        if not os.path.isfile(file_name):
            TransformPane.show_error("Cannot open %s" % file_name)
            return
        transform_file = TransformFile(file_name)
        self.load_name_list.append(transform_file)

    def load_files(self, file_names):
        for file_name in file_names:
            self.load_file(file_name)

        self.transform_pane.transform_tree_widget.build(self.load_name_list)

    @staticmethod
    def delete_module(module_name):
        Util.clear_classes_and_reload_package(module_name)


