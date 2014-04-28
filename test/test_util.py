import unittest

from nose.tools import assert_equal
from nose.tools import assert_true, assert_false

from ast_tool_box.util import Util


class TestUtil(unittest.TestCase):
    def test_is_package(self):
        file_name = "../ast_tool_box"

        assert_true(Util.is_package(file_name))

        file_name = "../images"

        assert_false(Util.is_package(file_name))

    def test_path_to_path_and_package(self):
        file = "ast_tool_box/test/sample.py"

        path, package = Util.path_to_path_and_package(file)

        assert_equal("ast_tool_box/test", path)
        assert_equal(package, "sample")

        file = "../ast_tool_box/transformers/identity_transform.py"
        # file = "../ast_tool_box/models/ast_transformer.py"
        print "file %s" % __file__

        path, package = Util.path_to_path_and_package(file)

        assert_equal("..", path)
        assert_equal("ast_tool_box.transformers.identity_transform", package)
