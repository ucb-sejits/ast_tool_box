from __future__ import print_function

from Pyside import QtCore, QtGui
from ast_viewer.views.transformer_views import TransformerPane
from ast_viewer.models.code_models.code_model import CodeModel

class TransformerController(object):
    """
    coordinate between various transformer, either
    ast transformers or code generators
    have direct connection to a code controller
    """
    def __init__(self, code_controller=None):
        self.code_controller = code_controller
        self.transformer_view = TransformerPane()
        self.transformer_model = CodeModel
        self.files_loaded = []

    def apply_current_transform(self):
        current_item = self.transform_list.currentItem()
        print("apply invoked with %s" % current_item.text())

        transformer = current_item.ast_transformer_item.node_transformer()
        code_controller.apply_transform(current_item)
        print("go got transformer %s" % transformer)
        if isinstance(transformer, ast.NodeTransformer):
            print("let's add a tree")
            self.parent_viewer.add_tree_tab(name=current_item.text(), transformer=transformer)
        elif isinstance(transformer, CodeGenVisitor):
            print(transformer.visit(self))

    def load_transformers(self, file_name):
