__author__ = 'Chick Markley'

import os


class Util(object):
    @staticmethod
    def is_package(directory):
        print "is_package testing %s" % os.path.join(directory, "__init__.py")
        return os.path.isfile(os.path.join(directory, "__init__.py"))

    @staticmethod
    def path_to_path_and_package(file_path, package_name=None):
        """
         converts a file name into a path and a package name
        """
        # print "ptpap got %s and %s" % (file_path, package_name)
        if package_name is None:
            file_path, package_name = os.path.split(file_path)
            if package_name.endswith(".py"):
                package_name = ".".join(package_name.split(".")[:-1])

        if Util.is_package(file_path):
            file_path2, file_name2 = os.path.split(file_path)
            return Util.path_to_path_and_package(file_path2, ".".join([file_name2, package_name]))
        else:
            if file_path == "":
                file_path = '.'
            return file_path, package_name