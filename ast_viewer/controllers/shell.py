"""
basic shell that allows for application of node_transformer and code serializers to be applied to
an AST
"""
from __future__ import print_function

import readline
import time
import argparse
from ast_viewer.controllers.tree_transform_controller import TreeTransformController


class AstTransformInterpreter(object):
    def __init__(self, file_name=None, verbose=False):
        self.verbose = verbose
        self.controller = TreeTransformController()
        self.controller.ast_tree_manager.new_item_from_file(file_name)
        self.controller.node_transformer_manager.get_ast_transformers("ctree.transformations")

    def clear(self):
        self.controller.clear()
        pass

    def show_asts(self):
        for index, ast_tree_item in enumerate(self.controller.ast_tree_manager):
            print("Ast[%d]: %s" % (index, ast_tree_item))

    def ast_command(self, command):
        fields = command.split()
        if len(fields) < 2 or fields[1].startswith("list"):
            self.show_asts()
        elif fields[1].startswith("cle"):
            self.controller.ast_tree_manager.clear()
        else:
            print("unknown ast command")

    def show_transforms(self):
        for index, transformer_item in enumerate(self.controller.node_transformer_manager):
            print("transform[%d]: %s" % (index, transformer_item))

    def transform_command(self, command):
        fields = command.split()
        if len(fields) < 2 or fields[1].startswith("list"):
            self.show_transforms()
        elif fields[1].startswith("cle"):
            self.controller.node_transformer_manager.clear()
        else:
            print("unknown ast command")

    def apply_transform(self, command):
        fields = command.split()
        # try:
        ast_index = int(fields[1])
        transform_index = int(fields[2])

        self.controller.ast_tree_manager.create_transformed_child(
            self.controller.ast_tree_manager[ast_index],
            self.controller.node_transformer_manager[transform_index]
        )
        self.show_asts()
        # except Exception as e:
        #     print("command must have ast_index then transform_index %s" % e.message)
        #     raise e
        #     return

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

        last_input = None
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
            last_input = user_input

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AST Transform interpreter")
    parser.add_argument(
        '-i', '--interactive', help='interactive mode, allows direct communication with device', action="store_true"
    )
    parser.add_argument('-f', '--file', help='path to python source file')
    parser.add_argument('-v', '--verbose', help='show more debug than you like', action="store_true")

    args = parser.parse_args()

    if not args.port:
        usb_port_name = AstTransformInterpreter.guess_port()
        print("Using port %s" % usb_port_name)
    else:
        usb_port_name = args.port

    watt_reader = AstTransformInterpreter(args.file, verbose=False)

    if args.verbose:
        watt_reader.set_verbose(True)
    if args.clear:
        watt_reader.drain()

    if args.interactive:
        watt_reader.interactive_mode()
    else:
        parser.print_usage()
