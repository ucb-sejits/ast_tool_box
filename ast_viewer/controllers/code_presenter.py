from __future__ import print_function

from ast_viewer.controllers.tree_transform_controller import TreeTransformController
import ast_viewer.models.code_models.code_model as code_model
import ast_viewer.models.transform_models.transform_model as transform_model
import ast_viewer.controllers.transform_presenter as transform_controllers

from ast_viewer.views.code_views.code_pane import CodePane
import ast


class CodePresenter(object):
    def __init__(self, tree_transform_controller=None):
        assert isinstance(tree_transform_controller, TreeTransformController)

        self.code_items = []
        self.transform_presenter = None
        self.tree_transform_controller = tree_transform_controller

        self.code_pane = CodePane(code_presenter=self)

    def set_transform_presenter(self, transform_presenter):
        assert isinstance(transform_presenter, transform_controllers.TransformPresenter)
        self.transform_presenter = transform_presenter

    def clear(self):
        self.code_items = []

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

    def apply_transform(self, code_item, transform_item):
        """
        transform some kind of code thing into another kind of code thing
        using some kind of transform thing, update views accordingly
        """
        assert isinstance(code_item, code_model.CodeItem)
        assert isinstance(transform_item, transform_model.TransformItem)

        def apply_codegen_transform(ast_root):
            """
            Code generates each file in the project
            """
            import ctree.nodes
            assert isinstance(ast_root, ctree.nodes.Project), \
                "apply_code_gen root of tree not Project is a %s" % ast_root

            # TODO: stay more in line with ctree and use ResolveGeneratedPathRefs

            # transform all files a combined source string
            combined_source = ""
            for f in ast_root.files:
                combined_source += "File %s\n" % f.name
                combined_source += f.codegen()
            return combined_source

        if isinstance(code_item, code_model.FileItem):
            self.show_error("Transformation cannot be applied to source code")
        elif isinstance(code_item, code_model.AstTreeItem):
            if isinstance(transform_item, transform_model.AstTransformItem):
                new_tree = transform_item.get_instance().visit(code_item.ast_tree)
                new_ast_tree_item = code_model.AstTreeItem(
                    new_tree,
                    name=transform_item.name(),
                    parent_link=code_model.CodeTransformLink(code_item=code_item, transform_item=transform_item),
                )
                self.add_code_item(new_ast_tree_item)
            elif isinstance(transform_item, transform_model.CodeGeneratorItem):
                # new_code = transform_item.get_instance().visit(code_item.ast_tree)
                new_code = apply_codegen_transform(code_item.ast_tree)
                new_code_item = code_model.GeneratedCodeItem(
                    new_code,
                    parent_link=code_model.CodeTransformLink(code_item=code_item, transform_item=transform_item),
                )
                self.add_code_item(new_code_item)
            else:
                self.show_error("Cannot transform\n%s\n with\n%s" % (code_item, transform_item))
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

    def delete(self, ast_tree_item):
        """
        delete an ast tree from manager
        ast_tree_item can be AstTreeWidgetItem or index or string
        representing index
        """
        if isinstance(ast_tree_item, code_model.CodeItem):
            self.fix_derived_items_before_delete(ast_tree_item)
            self.code_items.remove(ast_tree_item)
            return True
        else:
            index = self.get_valid_index(ast_tree_item)
            if index:
                self.fix_derived_items_before_delete(self.code_items[index])
                self.code_items.remove(self.code_items[index])
                return True
        return False
