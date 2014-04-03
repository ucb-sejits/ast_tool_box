import unittest

from nose.tools import assert_equal
from nose.tools import assert_true, assert_false

from ast_viewer.util import Util


class TestUtil(unittest.TestCase):
    def test_is_package(self):
        file_name = "../ast_viewer"

        assert_true(Util.is_package(file_name))

        file_name = "../images"

        assert_false(Util.is_package(file_name))

    def test_path_to_path_and_package(self):
        file = "ast_viewer/test/sample.py"

        path, package = Util.path_to_path_and_package(file)

        assert_equal("ast_viewer/test", path)
        assert_equal(package, "sample")

        file = "../ast_viewer/transformers/identity_transform.py"
        # file = "../ast_viewer/models/ast_transformer.py"
        print "file %s" % __file__

        path, package = Util.path_to_path_and_package(file)

        assert_equal("..", path)
        assert_equal("ast_viewer.transformers.identity_transform", package)
