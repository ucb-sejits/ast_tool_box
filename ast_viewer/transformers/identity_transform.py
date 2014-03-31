from __future__ import print_function
__author__ = 'Chick Markley'

import ast


class IdentityTransform(ast.NodeTransformer):
    pass


class NoisyIdentityTransform(ast.NodeTransformer):
    def __init__(self, func):
        super(NoisyIdentityTransform, self).__init__()
        self.lambda_func = func

    def visit(self, node):
        self.func(node)
        super(NoisyIdentityTransform, self).visit(node)

