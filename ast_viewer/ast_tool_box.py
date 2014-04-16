"""
   Program that shows the program on the right and its abstract syntax tree (ast) on the left.
"""
from __future__ import print_function

import sys
import logging
import ast
import traceback
import copy

from PySide import QtCore, QtGui

import ast_viewer
from ast_viewer.views.ast_tree_widget import AstTreeWidget
from ast_viewer.views.ast_tree_tabs import AstTreePane
from ast_viewer.views.ast_transform_viewer import AstTransformViewer

from ast_viewer.controllers.tree_transform_controller import TreeTransformController


logger = logging.getLogger(__name__)

DEBUGGING = False

PROGRAM_NAME = 'AST Toolkit'
PROGRAM_VERSION = '1.0.0'
ABOUT_MESSAGE = u"""
%(prog)s version %(version)s
""" % {"prog": PROGRAM_NAME, "version": ast_viewer.__version__}


def logging_basic_config(level):
    """ Setup basic config logging. Useful for debugging to quickly setup a useful logger"""
    fmt = '%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level=level, format=fmt)


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
        app = QtGui.QApplication(sys.argv)
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


from ast_viewer.controllers.code_presenter import CodePresenter
from ast_viewer.controllers.transform_presenter import TransformPresenter

QtCore.QCoreApplication.setOrganizationName("Aspire Lab")
QtCore.QCoreApplication.setOrganizationDomain("aspire.eecs.berkeley.edu")
QtCore.QCoreApplication.setApplicationName("AstToolBox")

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
            of source code. 
            
            The source can be given as text in the source parameter, or
            can be read from a file. The file_name parameter overrides
            the source parameter.
            
            The mode argument specifies what kind of code must be compiled; 
            it can be 'exec' if source consists of a sequence of statements, 
            'eval' if it consists of a single expression, or 'single' if it 
            consists of a single interactive statement (in the latter case, 
            expression statements that evaluate to something other than None 
            will be printed).
            (see http://docs.python.org/2/library/functions.html#compile)
            
            If width and height are both set, the window is resized.
        """
        super(AstToolBox, self).__init__()

        valid_modes = ['exec', 'eval', 'single']
        if mode not in valid_modes:
            raise ValueError("Mode must be one of: {}".format(valid_modes))
        self._mode = 'exec'

        self.start_packages = packages if packages else []

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

        central_splitter = QtGui.QSplitter(self, orientation=QtCore.Qt.Horizontal)
        self.setCentralWidget(central_splitter)
        central_layout = QtGui.QHBoxLayout()
        central_splitter.setLayout(central_layout)

        # Create base tree widget
        central_layout.addWidget(self.code_presenter.code_pane)

        # central_layout.addWidget(self.editor)

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

        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.my_test, "Ctrl+T")

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

        self._update_widgets(file_name)


    def _get_file_name_from_dialog(self):
        """ Opens a file dialog and returns the file name selected by the user
        """
        file_name, _ = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                                                         '', "Python Files (*.py);;All Files (*)")
        return file_name


    def _update_widgets(self, file_name):
        """ Reads source from a file and updates the tree and editor widgets.. 
        """
        if file_name:
            self._load_file(file_name)

        self.setWindowTitle('{} - {}'.format(PROGRAM_NAME, self._file_name))
        # self.editor.setPlainText(self._source_code)

        try:
            self._fill_ast_tree_widget()
        except StandardError, ex:
            if DEBUGGING:
                raise
            else:
                stack_trace = traceback.format_exc()
                msg = "Unable to parse file: {}\n\n{}\n\n{}" \
                    .format(self._file_name, ex, stack_trace)
                logger.exception(ex)
                QtGui.QMessageBox.warning(self, 'error', msg)

    def _load_file(self, file_name):
        """
        Opens a file and sets self._file_name and self._source code if successful
        """
        logger.debug("Opening {!r}".format(file_name))

        in_file = QtCore.QFile(file_name)
        if in_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            text = in_file.readAll()
            try:
                source_code = str(text, encoding='ascii')  # Python 3
            except TypeError:
                source_code = str(text)  # Python 2

            self._file_name = file_name
            self._source_code = source_code

        else:
            msg = "Unable to open file: {}".format(file_name)
            logger.warn(msg)
            QtGui.QMessageBox.warning(self, 'error', msg)

    def add_tree_tab(self, ast_tree=None, transformer=None, name=None):
        """
        Adds a new ast tab after running the specified transformer
        on the current tab's ast
        """
        if not ast_tree:
            ast_tree = self.ast_tree_tabs.current_ast()

        if transformer:
            new_ast_tree = copy.deepcopy(ast_tree)
            # print("got transformer %s" % transformer)
            try:
                transformer.visit(new_ast_tree)
            except Exception as e:
                print("Exception calling transformer %s" % e.message)

        new_tree_tab = AstTreeWidget(self, main_window=self)
        new_tree_tab.make_tree_from(new_ast_tree)

        if not name:
            name = "Tree %d" % (self.ast_tree_tabs.count() + 1)

        self.ast_tree_tabs.addTab(new_tree_tab, name)
        self.ast_tree_tabs.setCurrentWidget(new_tree_tab)

    @QtCore.Slot(QtGui.QTreeWidgetItem, QtGui.QTreeWidgetItem)
    def highlight_node(self, current_item, _previous_item):
        """ Highlights the node if it has line:col information.
        """
        highlight_str = current_item.text(AstTreeWidget.COL_HIGHLIGHT)
        from_line_str, from_col_str, to_line_str, to_col_str = highlight_str.split(":")

        try:
            from_line_col = (int(from_line_str), int(from_col_str))
        except ValueError:
            from_line_col = None

        try:
            to_line_col = (int(to_line_str), int(to_col_str))
        except ValueError:
            to_line_col = None

        logger.debug("Highlighting ({!r}) : ({!r})".format(from_line_col, to_line_col))
        self.select_text(from_line_col, to_line_col)

    def select_text(self, from_line_col, to_line_col):
        """ Selects a text in the range from_line:col ... to_line:col
            from_line_col and to_line_col should be a (line, column) tuple
            If from_line_col is None, the selection starts at the beginning of the document
            If to_line_col is None, the selection goes to the end of the document
        """
        text_cursor = self.editor.textCursor()

        if from_line_col is None:
            text_cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        else:
            from_line, from_col = from_line_col
            # findBlockByLineNumber seems to be 0-based.
            from_text_block = self.editor.document().findBlockByLineNumber(from_line - 1)
            from_pos = from_text_block.position() + from_col
            text_cursor.setPosition(from_pos, QtGui.QTextCursor.MoveAnchor)

        if to_line_col is None:
            text_cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
        else:
            to_line, to_col = to_line_col
            to_text_block = self.editor.document().findBlockByLineNumber(to_line - 1)
            to_pos = to_text_block.position() + to_col
            text_cursor.setPosition(to_pos, QtGui.QTextCursor.KeepAnchor)

        self.editor.setTextCursor(text_cursor)

    def search_box_changed(self):
        # print("search_box is now '%s'" % self.search_box.text())

        if not self.search_box.text():
            return

        current_tree = self.ast_tree_tabs.currentWidget()
        # print("current tree %s" % current_tree)
        #
        # for widget_index in range(self.ast_tree_tabs.count()):
        #     widget = self.ast_tree_tabs.widget(widget_index)
        #     print("widget %s ast_tree %s" % (widget, widget.ast_root))

        items = current_tree.findItems(
            self.search_box.text(),
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive,
            column=AstTreeWidget.COL_NODE
        )
        # print("Found %d items" % len(items))
        if len(items) > 0:
            print(items[0])
            current_tree.setCurrentItem(items[0])
            current_tree.expandItem(items[0])

    def my_test(self):
        """ Function for testing """
        pass

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

# pylint: enable=R0901, R0902, R0904, W0201

if __name__ == '__main__':
    sys.exit(view(source_code="print a + 5 + 6  / 3.7", mode='eval', width=800, height=600))
