from __future__ import print_function

__author__ = 'Chick Markley'

import ast
import copy


class NodeTransformerManager(object):
    """
    manage the list of all transformer items that have been discovered.  items
    are all subclasses of ast.NodeTransformer
    TODO: Figure out how to use transformers whose constructors require parameters
    """
    def __init__(self):
        self.transformer_items = []
        self.transformers_by_name = {}

    def count(self):
        """return current transformers"""
        return len(self.transformer_items)

    def get_node_transformers(self, module_name):
        """Use module_name to discover some transformers"""

        try:
            __import__(module_name)
            self.reload()
        except Exception as exception:
            print("cannot load %s message %s" % (module_name, exception.message))

    def reload(self):
        """rebuild list of all in memory subclasses of ast.NodeTransformer"""

        self.transformer_items = map(
            lambda transformer: NodeTransformerItem(transformer),
            ast.NodeTransformer.__subclasses__()
        )

        for transformer_item in self.transformer_items:
            # print("loaded %s" % transformer_item.name())
            self.transformers_by_name[transformer_item.name()] = transformer_item

    def get_instance_by_name(self, transformer_name):
        transformer_item = self.transformers_by_name[transformer_name]
        return transformer_item.get_instance()

    def __iter__(self):
        return iter(self.transformer_items)

if __name__ == '__main__':
    ntm = NodeTransformerManager()

    ntm.get_node_transformers('ctree.transformations')


class NodeTransformerItem(object):
    """
    Basic wrapper of an ast.NodeTransformer with convenience methods
    for creating, getting names etc
    """
    def __init__(self, node_transformer):
        self.node_transformer = node_transformer

    def package(self):
        return self.node_transformer.__module__

    def name(self):
        return self.node_transformer.__name__

    def get_instance(self):
        return self.node_transformer()

    def transform_in_place(self, *args, **kwargs):
        """Transform a tree in place"""
        if args:
            transformer = self.node_transformer(*args[1:], **kwargs)
            transformer.visit(args[0])

    def copy_and_transform(self, *args, **kwargs):
        if args:
            new_ast = copy.deepcopy(args[0])
            new_args = [new_ast]
            new_args += args[1:]

            self.transform_in_place(*new_args, **kwargs)
            return new_ast
        return None


