from __future__ import print_function

from PySide import QtGui


class TransformerPane(QtGui.QGroupBox):
    def __init__(self, transformer_controller=None):
        super(TransformerPane, self).__init__("Transformers & CodeGenerators")
        self.transformer_controller = transformer_controller
