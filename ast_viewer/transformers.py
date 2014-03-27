from __future__ import print_function

__author__ = 'Chick Markley'

import sys
import ast
import inspect

class NodeTransformerManager(object):
    def __init__(self):
        self.all_transformers = {}

    def get_node_transformers(self, module_name):
        """Use module_name to discover some transformers"""

        try:
            __import__(module_name)

            for subclass in ast.NodeTransformer.__subclasses__():
                package = subclass.__module__
                clazz = subclass.__name__
                print("found %s" % clazz)

                self.all_transformers[package + clazz] = subclass
            # just_imported = sys.modules[module_name]
            # for key, value in just_imported.__dict__.iteritems():
            #     if inspect.isclass(value):
            #         print("got %s -> %s super %s" % (key, value, value.__bases__[0]))
            #         if (value.__bases__[0], ast.NodeTransformer):
            #             print("got %s -> %s super %s" % (key, value, value.__bases__[0]))



        except Exception as exception:
            print("cannot load %s message %s" % (module_name, exception.message))

if __name__ == '__main__':
    ntm = NodeTransformerManager()

    ntm.get_node_transformers('ctree.transformations')

