"""
   Program that shows the program on the right and its abstract syntax tree (ast) on the left.
"""
from __future__ import print_function

import sys
import argparse
import logging

from PySide import QtCore, QtGui

import ast_tool_box

from ast_tool_box.controllers.tree_transform_controller import TreeTransformController
from ast_tool_box.controllers.code_presenter import CodePresenter

from ast_tool_box.controllers.transform_presenter import TransformPresenter

QtCore.QCoreApplication.setOrganizationName("Aspire Lab")
QtCore.QCoreApplication.setOrganizationDomain("aspire.eecs.berkeley.edu")
QtCore.QCoreApplication.setApplicationName("AstToolBox")

DEBUGGING = False

PROGRAM_NAME = 'AstToolBox'
PROGRAM_VERSION = '1.0.0'
ABOUT_MESSAGE = u"""
%(prog)s version %(version)s
""" % {"prog": PROGRAM_NAME, "version": ast_tool_box.__version__}


def check_class(obj, target_class, allow_none=False):
    """ Checks that the  obj is a (sub)type of target_class. 
        Raises a TypeError if this is not the case.
    """
    if not isinstance(obj, target_class):
        if not (allow_none and obj is None):
            raise TypeError("obj must be a of type {}, got: {}"
                            .format(target_class, type(obj)))


def get_qapplication_instance():
    """ Returns the QApplication instance. Creates one if it doesn't exist.
    """
    app = QtGui.QApplication.instance()
    if app is None:
        # sys.argv[0] = PROGRAM_NAME
        print("here I am")
        app = QtGui.QApplication(sys.argv[1:])
        app.setStyle(QtGui.QMacStyle)
        QtGui.QApplication.setStyle(QtGui.QMacStyle())
    check_class(app, QtGui.QApplication)
    return app


def view(*args, **kwargs):
    """ Opens an AstViewer window"""
    app = get_qapplication_instance()

    window = AstToolBox(*args, **kwargs)
    window.show()
    window.activateWindow()
    if sys.platform == "darwin":
        window.raise_()

    logger.info("Starting the AST viewer...")
    exit_code = app.exec_()
    logger.info("AST viewer done...")
    return exit_code


def class_name(obj):
    """ Returns the class name of an object"""
    return obj.__class__.__name__


# The main window inherits from a Qt class, therefore it has many
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201, R0913 


class AstToolBox(QtGui.QMainWindow):
    """
    The main application.
    """

    default_left_frame_size = 900

    def __init__(self, file_name=None, mode='exec', packages=None, width=None, height=None):
        """ Constructor
            
            AST browser windows that displays the Abstract Syntax Tree
            of source_text code.
            
            The source_text can be given as text in the source_text parameter, or
            can be read from a file. The file_name parameter overrides
            the source_text parameter.
            
            The mode argument specifies what kind of code must be compiled; 
            it can be 'exec' if source_text consists of a sequence of statements,
            'eval' if it consists of a single expression, or 'single' if it 
            consists of a single interactive statement (in the latter case, 
            expression statements that evaluate to something other than None 
            will be printed).
            (see http://docs.python.org/2/library/functions.html#compile)
        """
        super(AstToolBox, self).__init__()

        valid_modes = ['exec', 'eval', 'single']
        if mode not in valid_modes:
            raise ValueError("Mode must be one of: {}".format(valid_modes))
        self._mode = 'exec'

        self.auto_expand_ast = True

        self.start_packages = packages if packages else []
        self.start_packages += [
            'ctree.transformations',
            # 'ctree.c.codegen',
            # 'ctree.ocl.codegen',
            # 'ctree.omp.codegen',
        ]

        self.settings = None

        # Set up the UI
        self.tree_transform_controller = TreeTransformController()

        # there is a little trick here so both presenters know about their partner
        self.code_presenter = CodePresenter(
            tree_transform_controller=self.tree_transform_controller
        )
        self.transform_presenter = TransformPresenter(
            tree_transform_controller=self.tree_transform_controller,
            start_packages=self.start_packages,
        )
        self.code_presenter.set_transform_presenter(self.transform_presenter)
        self.transform_presenter.set_code_presenter(self.code_presenter)

        self.code_presenter.new_item_from_file(file_name)
        self.transform_presenter.load_files(self.start_packages)

        central_splitter = QtGui.QSplitter(self, orientation=QtCore.Qt.Horizontal)
        self.setCentralWidget(central_splitter)
        central_layout = QtGui.QHBoxLayout()
        central_splitter.setLayout(central_layout)

        # Create base tree widget
        central_layout.addWidget(self.code_presenter.code_pane)

        central_layout.addWidget(self.transform_presenter.transform_pane)

        # Splitter parameters
        central_splitter.setCollapsible(0, True)
        central_splitter.setCollapsible(1, True)
        central_splitter.setSizes([AstToolBox.default_left_frame_size, 250])
        central_splitter.setStretchFactor(0, 0.5)
        central_splitter.setStretchFactor(1, 0.5)

        self._setup_menu()
        self.setWindowTitle('{}'.format(PROGRAM_NAME))

        self.read_settings()

        #
        # TODO: figure out where and how to set the focus of this thing as it starts up

    def write_settings(self):
        self.settings = QtCore.QSettings()
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.endGroup()

    def read_settings(self):
        self.settings = QtCore.QSettings()
        self.settings.beginGroup("MainWindow")
        self.resize(self.settings.value("size", QtCore.QSize(1100, 900)))
        self.move(self.settings.value("pos", QtCore.QPoint(200, 200)))
        self.settings.endGroup()

    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("&Open...", self.open_file, "Ctrl+O")
        #file_menu.addAction("C&lose", self.close_window, "Ctrl+W")
        file_menu.addAction("E&xit", AstToolBox.quit_application, "Ctrl+Q")

        view_menu = self.menuBar().addMenu("&View")

        self.auto_expand_ast = QtGui.QAction("Expand AST trees on create", self, checkable=True, checked=True)
        assert self.auto_expand_ast.toggled.connect(self.set_auto_expand)

        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)

    def set_auto_expand(self):
        self.tree_transform_controller.ast_tree_manager.set_auto_expand(self.auto_expand_ast.isChecked())

    def new_file(self):
        """ Clears the widgets """
        self.ast_tree.make_tree_from()

    def open_file(self, file_name=None):
        """ Opens a new file. Show the open file dialog if file_name is None.
        """
        if not file_name:
            file_name = self._get_file_name_from_dialog()

        self.code_presenter.new_file(file_name)

    def about(self):
        """ Shows the about message window. """
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def close_window(self):
        """ Closes the window """
        self.close()

    def closeEvent(self, event):
        self.write_settings()
        event.accept()

    @staticmethod
    def quit_application():
        """ Closes all windows """
        app = QtGui.QApplication.instance()
        app.closeAllWindows()


logger = logging.getLogger(__name__)


def main():
    """ Main program to test stand alone
    """
    sys.argv[0] = "AstToolBox"
    app = QtGui.QApplication(sys.argv) # to allow for Qt command line arguments
    remaining_argv = app.arguments()

    parser = argparse.ArgumentParser(description='Python abstract syntax tree viewer and transformer')
    parser.add_argument('file_name', help='Python input file')
    parser.add_argument('packages', metavar='P', nargs='*')

    parser.add_argument(
        '-l', '--log-level', dest='log_level', default='warn',
        choices=('debug', 'info', 'warn', 'error', 'critical'),
        help="Log level. Only log messages with a level higher or equal than this "
             "will be printed. Default: 'warn'"
    )

    args = parser.parse_args(args = remaining_argv[1:])

    ast_tool_box.logging_basic_config(args.log_level.upper())

    logger.info('Started {}'.format(PROGRAM_NAME))

    exit_code = view(
        file_name=args.file_name,
        packages=args.packages,
        width=1400, height=900
    )

    logging.info('Done {}'.format(PROGRAM_NAME))
    sys.exit(exit_code)


# pylint: enable=R0901, R0902, R0904, W0201

if __name__ == '__main__':
    main()
