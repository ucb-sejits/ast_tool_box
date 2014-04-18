"""
read files, look for transforms and figure out what arguments that they need
"""
from __future__ import print_function
import sys
import inspect
import ast
from ctree.codegen import CodeGenVisitor
from pprint import pprint
from ast_viewer.util import Util
from collections import namedtuple


PositionalArg = namedtuple('PositionalArg', ['name', 'default_source'])


class TransformThing(object):
    def __init__(self, transform):
        self.transform = transform
        self.source = inspect.getsource(self.transform)
        # print(self.source)
        self.ast_root = ast.parse(self.source)
        self.args = self.get_args()

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

        for key, val in ast.iter_fields(init_func.args):
            print("args field key %s val %s %s" % (key, val, type(val)))

        for val in init_func.args.args:
            print("args args field val %s" % val.id)

        for val in init_func.args.defaults:
            if isinstance(val, str):
                print("default %s" % val)
            else:
                print("")

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
        return []

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
    def __init__(self, file_name):
        self.file_name = file_name
        self.transforms = []
        self.code_generators = []

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
                        self.transforms.append(TransformThing(thing))
                if issubclass(thing, CodeGenVisitor):
                    if thing.__name__ != "CodeGenVisitor":
                        self.code_generators.append(thing)






if __name__ == '__main__':
    tf = TransformFile(sys.argv[1])

    print("path %s" % tf.path)
    print("package %s" % tf.package_name)
    print("transforms", end="")
    pprint(tf.transforms)

