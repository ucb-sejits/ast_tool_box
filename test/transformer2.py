import ast

class Transformer1(ast.NodeTransformer):
    pass


class Transformer2(Transformer1):
    pass


class Transformer3(Transformer2):
    pass

