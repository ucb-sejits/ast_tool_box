"""
read files, look for transforms and figure out what arguments that they need
"""
from __future__ import print_function
import sys
import os.path
import inspect
import ast
from operator import methodcaller
from ctree.codegen import CodeGenVisitor
from pprint import pprint
from ast_viewer.util import Util
from collections import namedtuple
import codegen


PositionalArg = namedtuple('PositionalArg', ['name', 'default_source'])


class TransformThing(object):
    def __init__(self, transform, package_name=None, file_name=None, transform_file=None):
        self.transform = transform
        self.package_name = package_name
        self.transform_file = transform_file
        self.source_text = inspect.getsource(self.transform)
        self.file_name = file_name
        # print(self.source_text)
        self.ast_root = ast.parse(self.source_text)
        self.positional_args = []
        self._has_varargs = False
        self._has_kwargs = False
        self._super_classes = []
        self.doc = "TODO to get doc string from transform"
        self.get_args()
        self.figure_super_classes()

    def name(self):
        return self.transform.__name__

    def has_positional_args(self):
        return len(self.positional_args) > 0

    def has_varargs(self):
        return self._has_varargs

    def has_kwargs(self):
        return self._has_kwargs

    def super_classes(self):
        return self._super_classes

    def figure_super_classes(self):
        do_copy = True
        for clazz in inspect.getmro(self.transform):
            if do_copy:
                self._super_classes.append(
                    "%s.%s" % (clazz.__module__, clazz.__name__)
                )
            if clazz.__module__ == 'ast':
                if clazz.__name__ == 'NodeTransformer':
                    do_copy = False

    def get_args(self):
        class_def = self.find_node(self.ast_root, tipe=ast.ClassDef)
        print("class_def %s %s" % (class_def, class_def.name))
        if class_def is None:
            return []

        init_func = self.find_node(class_def, name='__init__')
        print("init_func %s" % init_func)
        if init_func is None:
            return []

        # for key, val in ast.iter_fields(init_func):
        #     print("field key %s val %s" % (key, val))

        # for key, val in ast.iter_fields(init_func.args):
        #     print("args field key %s val %s %s" % (key, val, type(val)))

        if hasattr(init_func.args, 'defaults'):
            defaults = init_func.args.defaults

        while len(defaults) < len(init_func.args.args):
            defaults.insert(0, None)

        for index, val in enumerate(init_func.args.args):
            if not val.id == 'self':
                if defaults[index] is not None:
                    default_st = codegen.to_source(defaults[index])
                else:
                    default_st = None
                # print("args args field val %s %s" % (val.id, default_st))
                self.positional_args.append(PositionalArg(val.id, default_st))

        # for val in init_func.args.defaults:
        #     if isinstance(val, str):
        #         print("default %s" % val)
        #     else:
        #         print("")

        self._has_varargs = hasattr(init_func.args, 'vararg') and init_func.args.vararg
        self._has_kwargs = hasattr(init_func.args, 'kwarg') and init_func.args.kwarg
        # if init_func.args.vararg:
        #     for val in init_func.args.vararg:
        #         print("vargs field val %s" % val)
        #
        # if init_func.args.kwarg:
        #     for key, val in init_func.args.kwarg:
        #         print("kwargs field field key %s -> %s" % (key, val))

        # for arg in init_func.args:
        #     print("got arg %s", arg)
        # for arg in init_func.arg
        # for child in ast.iter_child_nodes(self.ast_root):
        #     print("---------")
        #     pprint(child.__dict)

    def __str__(self):
        return "\n".join(
            ["%s(%s)" % (self.name(), self.super_classes())] +
            map(lambda x: x.__str__(), self.positional_args) +
            [
                "has varargs %s" % self.has_varargs(),
                "has kwargs %s" % self.has_kwargs(),
            ]
        )

    def find_node(self, node, name=None, tipe=None):

        def name_match():
            if name is None:
                return True
            else:
                if 'name' in node.__dict__:
                    return name == node.__dict__['name']
                return False

        def type_match():
            if tipe is None:
                return True
            else:
                return isinstance(node, tipe)

        if type_match() and name_match():
            return node

        for child_node in ast.iter_child_nodes(node):
            found_node = self.find_node(child_node, name=name, tipe=tipe)
            if found_node is not None:
                return found_node

        return None


class TransformFile(object):
    """
    a list of transforms contained in file
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.base_name = os.path.basename(file_name)
        self.source_text = ''
        with open(file_name, "r") as f:
            self.source_text = f.read()

        self.transforms = []
        self.code_generators = []
        self.class_def_nodes = {}

        self.ast_tree = ast.parse(self.source_text)
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                self.class_def_nodes[node.name] = node
                print("Found class def for %s" % node.name)

        self.path, self.package_name = Util.path_to_path_and_package(self.file_name)

        if not self.path in sys.path:
            sys.path.append(self.path)

        try:
            __import__(self.package_name)
        except Exception as exception:
            print("cannot load %s message %s" % (self.package_name, exception.message))
            return

        module = sys.modules[self.package_name]

        for key in module.__dict__:
            thing = module.__dict__[key]
            if inspect.isclass(thing):
                if issubclass(thing, ast.NodeTransformer):
                    if thing.__name__ != "NodeTransformer":
                        self.transforms.append(TransformThing(
                            thing,
                            file_name=file_name,
                            transform_file=self
                        ))
                if issubclass(thing, CodeGenVisitor):
                    if thing.__name__ != "CodeGenVisitor":
                        self.code_generators.append(TransformThing(
                            thing,
                            file_name=file_name,
                            transform_file=self
                        ))

        self.transforms.sort(key=methodcaller('name'))
        self.code_generators.sort(key=methodcaller('name'))

class TransformPackage(object):
    """
    a list of transforms contained in file
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.base_name = os.path.basename(file_name)
        self.source_text = ''

        self.transforms = []
        self.code_generators = []
        self.class_def_nodes = {}

        self.path, self.package_name = Util.path_to_path_and_package(self.file_name)
        print("transform package %s %s" % (self.path, self.package_name))

        if not self.path in sys.path:
            sys.path.append(self.path)

        try:
            __import__(self.package_name)
        except Exception as exception:
            print("cannot load %s message %s" % (self.package_name, exception.message))
            return

        module = sys.modules[self.package_name]
        print("module %s" % module)

        for key in module.__dict__:
            thing = module.__dict__[key]
            print("  got %s -> %s" % (key, thing))
            if inspect.isclass(thing):
                if issubclass(thing, ast.NodeTransformer):
                    if thing.__name__ != "NodeTransformer":
                        self.transforms.append(TransformThing(
                            thing,
                            file_name=file_name,
                            transform_file=self
                        ))
                if issubclass(thing, CodeGenVisitor):
                    if thing.__name__ != "CodeGenVisitor":
                        self.code_generators.append(TransformThing(
                            thing,
                            file_name=file_name,
                            transform_file=self
                        ))

        self.transforms.sort(key=methodcaller('name'))
        self.code_generators.sort(key=methodcaller('name'))

if __name__ == '__main__':
    tf = TransformFile(sys.argv[1])

    print("path %s" % tf.path)
    print("package %s" % tf.package_name)
    print("transforms", end="")
    for transform_thing in tf.transforms:
        print(transform_thing)

