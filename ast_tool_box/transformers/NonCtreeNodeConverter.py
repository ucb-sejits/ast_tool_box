from ast import NodeTransformer, iter_fields
from ctree.nodes import CtreeNode
from ctree.codegen import CodeGenVisitor
from copy import deepcopy

class NonCtreeNodeConverter(NodeTransformer):

    def generic_visit(self, node):
        if not isinstance(node, CtreeNode):
            NodeTransformer.generic_visit(self,node)
            return NonCtreeNode(node)
        return NodeTransformer.generic_visit(self,node)

class NonCtreeNode(CtreeNode):

    def _requires_semicolon(self):
        return False

    def __init__(self, node=CtreeNode()):
        self._fields = tuple(node._fields) + ('string',)
        self.string = '// ' + type(node).__name__ + '\n'
        for field, value in iter_fields(node):
            setattr(self, field, value)

    def codegen(self, indent=0):
        str = self.string
        for field in self._fields:
            if isinstance(getattr(self,field),CtreeNode):
                str += getattr(self,field).codegen(indent)
        if 'body' in self._fields:
            visitor = CodeGenVisitor(indent = indent)
            str += visitor._genblock(self.body)

        return str
