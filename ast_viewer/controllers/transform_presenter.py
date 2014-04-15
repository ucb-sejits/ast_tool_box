from __future__ import print_function

import ast
import sys
import inspect
from PySide import QtCore, QtGui

import ast_viewer.controllers as controllers
import ast_viewer.models.transform_models.transform_model as transform_model
from ast_viewer.controllers.tree_transform_controller import TreeTransformController
from ast_viewer.views.transform_views.transform_pane import TransformPane
from ctree.codegen import CodeGenVisitor
from ast_viewer.util import Util


class TransformPresenter(object):
    """
    coordinate between various transformer, either
    ast transformers or code generators
    have direct connection to a code code_presenter
    TODO: Do more investigation of managing transforms in separate namespace
    """
    def __init__(self, tree_transform_controller=None, start_packages=None):
        assert isinstance(tree_transform_controller, TreeTransformController)

        self.code_presenter = None
        self.tree_transform_controller = tree_transform_controller
        self.transform_pane = TransformPane(transform_presenter=self)

        self.transforms_loaded = []
        self.transform_items = []
        self.transforms_by_name = {}

        to_load = start_packages + [
            'ctree.transformations',
            'ctree.c.codegen',
            'ctree.ocl.codegen',
            'ctree.omp.codegen',
        ]
        self.load_transforms(to_load)

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
                            self.transform_items.append(transform_model.AstTransformItem(thing))
                    if issubclass(thing, CodeGenVisitor):
                        if thing.__name__ != "CodeGenVisitor":
                            self.transform_items.append(transform_model.CodeGeneratorItem(thing))
        # self.transform_items = map(
        #     lambda transform: transform_model.AstTransformItem(transform),
        #     ast.NodeTransformer.__subclasses__()
        # )
        # print("transform_presenter.reload so far %s" %
        #       map(lambda i: i.name(), self.transform_items))
        #
        # self.transform_items += map(
        #     lambda transform: transform_model.CodeGeneratorItem(transform),
        #     CodeGenVisitor.__subclasses__()
        # )
        #
        # print("transform_presenter.reload final %s" %
        #       map(lambda i: i.name(), self.transform_items))
        #
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

    def load_transform(self, key):
        """
        ONLY do import, finding transforms imported is separate
        step
        """
        self.transforms_loaded.append(key)

        path, package_name = Util.path_to_path_and_package(key)

        print("path %s package %s" % (path, package_name))

        if not path in sys.path:
            sys.path.append(path)

        self.get_ast_transforms(package_name)

    def load_transforms(self, key_list):
        if not isinstance(key_list, list):
            key_list = [key_list]

        for key in key_list:
            self.load_transform(key)

        print("AstTransformManager %s" % self)

        self.reload()
        self.transform_pane.update_view()

    @staticmethod
    def delete_module(module_name, paranoid=None):
        Util.clear_classes_and_reload_package(module_name)
        # from sys import modules
        # try:
        #     this_module = modules[module_name]
        # except KeyError:
        #     raise ValueError(module_name)
        # these_symbols = dir(this_module)
        #
        # if paranoid:
        #     try:
        #         paranoid[:]  # sequence support
        #     except:
        #         raise ValueError('must supply a finite list for paranoid')
        #     else:
        #         these_symbols = paranoid[:]
        #
        # print("deleting module %s" % module_name)
        # try:
        #     del modules[module_name]
        # except Exception as e:
        #     print("Error failed del %s error %s" % (module_name, e))

        # for mod in modules.values():
        #     try:
        #         delattr(mod, module_name)
        #     except AttributeError:
        #         print("Error failed del %s" % module_name)
        #     if paranoid:
        #         for symbol in these_symbols:
        #             if symbol[:2] == '__':  # ignore special symbols
        #                 continue
        #             try:
        #                 delattr(mod, symbol)
        #             except AttributeError:
        #                 pass

