from __future__ import print_function

import ast


class IdentityTransform(ast.NodeTransformer):
    pass


class NoisyIdentityTransform(ast.NodeTransformer):
    def __init__(self):
        super(NoisyIdentityTransform, self).__init__()

    def visit(self, node):
        print("node %s" % node)
        return super(NoisyIdentityTransform, self).visit(node)


class LambdaIdentityTransform(ast.NodeTransformer):
    def __init__(self, func):
        super(LambdaIdentityTransform, self).__init__()
        self.lambda_func = func

    def visit(self, node):
        self.lambda_func(node)
        return super(LambdaIdentityTransform, self).visit(node)

