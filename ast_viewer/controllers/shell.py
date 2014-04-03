"""
basic shell that allows for application of ast_transformer and code serializers to be applied to
an AST
"""
from __future__ import print_function

import os
import readline
import atexit
history_file = os.path.join(os.path.expanduser("~"), ".ast_viewer_hist")
try:
    readline.read_history_file(history_file)
except IOError:
    pass
atexit.register(readline.write_history_file, history_file)
del os, history_file

from ast_viewer.controllers.tree_transform_controller import TreeTransformController


class AstTransformInterpreter(object):
    def __init__(self, file_name=None, verbose=False):
        self.verbose = verbose
        self.controller = TreeTransformController()
        self.controller.ast_tree_manager.new_item_from_file(file_name)
        self.controller.ast_transformer_manager.get_ast_transformers("ctree.transformations")

    def clear(self):
        """delete all trees and transforms"""
        self.controller.clear()
        pass

    def show_ast(self, index):
        def show_parents_links(current_ast_item):
            link = current_ast_item.parent_link
            if link:
                show_parents_links(link.parent_ast_tree)
                print(
                    "derived from item %s transform %s" %
                    (link.parent_ast_tree.name, link.transform_item.name())
                )

        ast_item = self.controller.ast_tree_manager[index]
        print("ast[%d]: %s %s" % (index, ast_item.name, ast_item.ast_tree))
        show_parents_links(ast_item)

    def show_asts(self):
        for index, ast_tree_item in enumerate(self.controller.ast_tree_manager):
            #print("Ast[%d]: %s" % (index, ast_tree_item))
            self.show_ast(index)

    def delete_ast(self, tree_item):
        return self.controller.ast_tree_manager.delete(tree_item)

    def ast_command(self, command):
        fields = command.split()
        if len(fields) < 2 or fields[1].startswith("list"):
            self.show_asts()
        elif fields[1].startswith("del"):
            if len(fields) > 2 and self.delete_ast(fields[2]):
                pass
            else:
                print("error: delete command must specify index of tree to delete")
        elif fields[1].startswith("cle"):
            self.controller.ast_tree_manager.clear()
        elif fields[1].startswith("sho"):
            try:
                index = int(fields[2])
                from ctree.visual.dot_manager import DotManager
                print("calling open")
                DotManager.dot_ast_to_browser(self.controller.ast_tree_manager[index].ast_tree, "tree%d.png" % index)
            except IOError as e:
                print("ast show requires numeric index of ast, msg %s" % e.message)
        else:
            print("unknown ast command")

    def show_transforms(self):
        for index, transformer_item in enumerate(self.controller.ast_transformer_manager):
            print("transform[%d]: %s" % (index, transformer_item.name()))

    def transform_command(self, command):
        fields = command.split()
        if len(fields) < 2 or fields[1].startswith("list"):
            self.show_transforms()
        elif fields[1].startswith("cle"):
            self.controller.ast_transformer_manager.clear()
        elif fields[1].startswith("load"):
            if len(fields) > 2:
                key = fields[2]
                self.controller.load_transformers(key)
            else:
                print("transform load must specify filename")
        else:
            print("unknown transform command")

    def apply_transform(self, command):
        fields = command.split()

        if len(fields) > 2:
            ast_index = self.controller.ast_tree_manager.get_valid_index(fields[1])
            transform_index = self.controller.ast_transformer_manager.get_valid_index(fields[2])
            name = fields[3] if len(fields) > 3 else "Tree %d" % self.controller.ast_tree_manager.count()

            if ast_index is not None and transform_index is not None:
                self.controller.apply_transform(ast_index, transform_index, name=name)
                self.show_asts()
            else:
                print("apply missing index or index out of range")
        else:
            print("apply requires two numeric indices, tree index and transform index")

    def set_verbose(self, new_value=None):
        if new_value is None:
            self.verbose = not self.verbose
        else:
            self.verbose = new_value

    @staticmethod
    def usage():
        print("command must be one of")
        print("transform [list|delete|load] <arg>")
        print("ast [list|delete|load] <arg>")
        print("apply ast_index transform_index")
        print("quit")
        print("commands can be abbreviated to first three letters")
        print("\n")

    def interactive_mode(self):
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')

        while True:
            # print("Command: ", end="")
            # user_input = sys.stdin.readline()

            user_input = raw_input("Command (quit to exit): ")
            # print("got input %s" % user_input)
            # if user_input.strip() == '':
            #     user_input = last_input

            if user_input.startswith('q') or user_input.startswith('Q'):
                return
            elif user_input.lower().startswith('cle'):
                self.clear()
            elif user_input.lower().startswith('ast'):
                self.ast_command(user_input)
            elif user_input.lower().startswith('tra'):
                self.transform_command(user_input)
            elif user_input.lower().startswith('app'):
                self.apply_transform(user_input)
            elif user_input.lower().startswith('ver'):
                self.verbose = not self.verbose
            else:
                print("unknown command: %s" % user_input)