from __future__ import print_function

import copy

from ast_tool_box.controllers.tree_transform_controller import TreeTransformController
import ast_tool_box.models.code_models.code_model as code_model
import ast_tool_box.models.transform_models.transform_file as transform_model
import ast_tool_box.controllers.transform_presenter as transform_controllers

from ast_tool_box.views.code_views.code_pane import CodePane
import ast


class CodePresenter(object):
    def __init__(self, tree_transform_controller=None):
        print("tree_transform_controller %s" % tree_transform_controller)
        print("type is                   %s" % TreeTransformController)
        assert isinstance(tree_transform_controller, TreeTransformController), "got %s" % tree_transform_controller

        self.code_items = []
        self.transform_presenter = None
        self.tree_transform_controller = tree_transform_controller

        self.code_pane = CodePane(code_presenter=self)

    def new_file(self, file_name):
        self.clear()
        self.new_item_from_file(file_name)

    def set_transform_presenter(self, transform_presenter):
        assert isinstance(transform_presenter, transform_controllers.TransformPresenter)
        self.transform_presenter = transform_presenter

    def clear(self):
        while len(self.code_items) > 0:
            self.delete_last_item()
        self.code_pane.clear()

    def delete_last(self):
        self.delete(len(self.code_items)-1)

    def count(self):
        return len(self.code_items)

    def delete_last_item(self):
        self.code_items.remove(self.code_items[-1])

    def __getitem__(self, item):
        return self.code_items[item]

    def __iter__(self):
        return iter(self.code_items)

    def get_valid_index(self, index):
        """
        convenience method for checking index,
        if index is a string it will be converted to int
        None returned if failed to convert or index out of range
        """
        if not isinstance(index, int):
            try:
                index = int(index)
            except ValueError:
                return None

        if index >= 0:
            if index < len(self.code_items):
                return index
        return None

    def current_item(self):
        return self.code_items[-1]

    def add_code_item(self, code_item):
        self.code_items.append(code_item)
        self.code_pane.add_code_item(code_item)

    def resolve_transform_args(self, transform_thing):
        return self.code_pane.resolve_transform_arguments(transform_thing)

    def apply_transform(self, code_item, transform_item):
        """
        transform some kind of code thing into another kind of code thing
        using some kind of transform thing, update views accordingly
        """
        if isinstance(code_item, ast.AST):
            code_item = code_model.AstTreeItem(code_item)

        assert isinstance(code_item, code_model.CodeItem)
        if transform_item is not None:
            assert isinstance(transform_item, transform_model.TransformThing), "bad type %s" % transform_item

        def apply_codegen_transform(ast_root, argument_list):
            """
            Code generates each file in the project
            """
            import ctree.nodes
            assert isinstance(ast_root, ctree.nodes.Project), \
                "apply_code_gen root of tree not Project is a %s" % ast_root

            # TODO: stay more in line with ctree and use ResolveGeneratedPathRefs

            # transform all files a combined source_text string
            combined_source = ""
            if ast_root.files and len(ast_root.files) > 0:
                for f in ast_root.files:
                    combined_source += "File %s\n" % f.name
                    combined_source += f.codegen()
                return combined_source
            else:
                return ast_root.codegen()

        if isinstance(code_item, code_model.FileItem):
            self.show_error("Transformation cannot be applied to source_text code")
        elif isinstance(code_item, code_model.AstTreeItem):
            if isinstance(transform_item, transform_model.AstTransformItem):
                argument_values = []
                if transform_item.has_args():
                    argument_values = self.resolve_transform_args(transform_item)
                    if not argument_values:
                        return
                    for a in argument_values:
                        print("got arg %s" % a)
                    argument_values = [eval(x) for x in argument_values]

                tree_copy = copy.deepcopy(code_item.ast_tree)
                new_tree = transform_item.get_instance(argument_values).visit(tree_copy)
                new_ast_tree_item = code_model.AstTreeItem(
                    new_tree,
                    name=transform_item.name(),
                    parent_link=code_model.CodeTransformLink(code_item=code_item, transform_item=transform_item),
                )
                self.add_code_item(new_ast_tree_item)
            elif isinstance(transform_item, transform_model.CodeGeneratorItem):
                # new_code = transform_item.get_instance().visit(code_item.ast_tree)
                argument_values = []
                if transform_item.has_args():
                    argument_values = self.resolve_transform_args(transform_item)
                    if not argument_values:
                        return
                    for a in argument_values:
                        print("got arg %s" % a)
                    argument_values = [eval(x) for x in argument_values]

                tree_copy = copy.deepcopy(code_item.ast_tree)
                new_code = apply_codegen_transform(tree_copy)
                new_code_item = code_model.GeneratedCodeItem(
                    new_code,
                    parent_link=code_model.CodeTransformLink(code_item=code_item, transform_item=transform_item),
                )
                self.add_code_item(new_code_item)
            elif transform_item is None:
                new_tree = code_item.ast_tree
                new_ast_tree_item = code_model.AstTreeItem(
                    new_tree,
                    name="SubTree",
                    parent_link=code_model.CodeTransformLink(
                        code_item=code_item,
                        transform_item=None
                    ),
                )
                self.add_code_item(new_ast_tree_item)
            else:
                self.show_error("Cannot transform\n%s\n with\n%s" % (code_item, transform_item))
                raise Exception()
        else:
            self.show_error("Unknown transform of\n%s\n with\n%s" % (code_item, transform_item))

    def show_error(self, message):
        self.code_pane.show_error(message)

    def new_item_from_source(self, source_text):
        new_code_item = code_model.FileItem(code=source_text)
        parser_item = transform_model.AstParseItem()
        new_tree_item = code_model.AstTreeItem(
            ast.parse(source_text),
            name=parser_item.name(),
            parent_link=code_model.CodeTransformLink(new_code_item, parser_item)
        )
        self.add_code_item(new_code_item)
        self.add_code_item(new_tree_item)

    def new_item_from_file(self, file_name):
        with open(file_name, "r") as file_handle:
            source_text = file_handle.read()
            new_code_item = code_model.FileItem(code=source_text, file_name=file_name)
            parser_item = transform_model.AstParseItem()
            new_tree_item = code_model.AstTreeItem(
                ast.parse(source_text),
                name=parser_item.name(),
                parent_link=code_model.CodeTransformLink(new_code_item, parser_item)
            )
            self.add_code_item(new_code_item)
            self.add_code_item(new_tree_item)

    def fix_derived_items_before_delete(self, item_to_delete):
        for other_item in self.code_items:
            if other_item != item_to_delete:
                if other_item.parent_link:
                    if other_item.parent_link.parent_ast_tree == item_to_delete:
                        other_item.parent_link = None

    def delete(self, index):
        """
        delete an ast tree from manager
        ast_tree_item can be AstTreeWidgetItem or index or string
        representing index
        """
        if index < len(self.code_items):
            # self.fix_derived_items_before_delete(self.code_items[index])
            self.code_items.remove(self.code_items[index])
            self.code_pane.delete_at(index)
            return True
        else:
            self.show_error("Tried to delete non-existing code panel %s" % index)
            return False
