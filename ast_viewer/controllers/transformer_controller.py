from __future__ import print_function

from ast_viewer.views.transformer_views import TransformerPane

class TransformerController(object):
    """
    coordinate between various transformer, either
    ast transformers or code generators
    """
    def __init__(self):
        self.transformer_view = TransformerPane()
        pass