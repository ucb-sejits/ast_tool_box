from __future__ import print_function

import ast
from ctree.codegen import CodeGenVisitor


class IdentityTransform(ast.NodeTransformer):
    pass


class ChickTransform(ast.NodeTransformer):
    pass


class Chick2Transform(ChickTransform):
    pass


class Chick4Transform(Chick2Transform):
    def __init__(self, *variable_args):
        self.args = variable_args


class Chick3Transform(Chick2Transform):
    def __init__(self, arg1, arg2='cat', arg3=Chick4Transform((1,2))):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3


class Chick5Transform(Chick2Transform):
    def __init__(self, **kwargs):
        self.args = kwargs


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


class CodeGenX(CodeGenVisitor):
    def __init__(self, dog='dog', cat='cat'):
        super(CodeGenX, self).__init__()


class CodeGenY(CodeGenX):
    def __init__(self, dog='dog', cat='cat'):
        super(CodeGenY, self).__init__()
