"""
   Program that shows the program on the right and its abstract syntax tree (ast) on the left.
"""
from __future__ import print_function

import sys
import logging
import ast
import traceback
import ast_viewer

from PySide import QtCore, QtGui

from ast_viewer.search_widget import SearchLineEdit
from ast_viewer.ast_tree_widget import AstTreeWidget

logger = logging.getLogger(__name__)

DEBUGGING = False

PROGRAM_NAME = 'ast_viewer'
ABOUT_MESSAGE = u"""%(prog)s version %(version)s
""" % {"program": PROGRAM_NAME, "version": ast_viewer.__version__}


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
    """
    Returns the QApplication instance. Creates one if it doesn't exist.
    """
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    check_class(app, QtGui.QApplication)
    return app


def view(*args, **kwargs):
    """ Opens an AstViewer window
    """
    app = get_qapplication_instance()

    window = AstViewer(*args, **kwargs)
    window.show()

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

class AstViewer(QtGui.QMainWindow):
    """ The main application.
    """

    def __init__(self, file_name='', source_code='', mode='exec',
                 width=None, height=None):
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
        super(AstViewer, self).__init__()

        valid_modes = ['exec', 'eval', 'single']
        if mode not in valid_modes:
            raise ValueError("Mode must be one of: {}".format(valid_modes))

        # default references to later instantiated stuff
        self.ast_tree = None

        # Models
        self._file_name = '<source>'
        self._source_code = source_code
        self._mode = mode

        # Views
        self._setup_actions()
        self._setup_menu()
        self._setup_views()
        self.setWindowTitle('{}'.format(PROGRAM_NAME))

        # Update views
        self.col_field_action.setChecked(False)
        self.col_class_action.setChecked(False)
        self.col_value_action.setChecked(False)

        if file_name and source_code:
            logger.warn("Both the file_name and source_code are defined: source_code ignored.")

        if not file_name and not source_code:
            file_name = self._get_file_name_from_dialog()

        self._update_widgets(file_name)

        if width and height:
            self.resize(width, height)

        self.tool_bar = self.addToolBar('Exit')
        self.search_box = SearchLineEdit(
            QtGui.QPixmap(r"images/search_icon.png"),
            QtGui.QPixmap(r"images/search_icon.png"),
            on_changed=self.search_box_changed
        )
        self.tool_bar.addWidget(self.search_box)

    def _setup_actions(self):
        """ Creates the MainWindow actions.
        """
        self.col_field_action = QtGui.QAction(
            "Show Field Column", self, checkable=True, checked=True,
            statusTip="Shows or hides the Field column")
        self.col_field_action.setShortcut("Ctrl+1")
        assert self.col_field_action.toggled.connect(self.show_field_column)

        self.col_class_action = QtGui.QAction(
            "Show Class Column", self, checkable=True, checked=True,
            statusTip="Shows or hides the Class column")
        self.col_class_action.setShortcut("Ctrl+2")
        assert self.col_class_action.toggled.connect(self.show_class_column)

        self.col_value_action = QtGui.QAction(
            "Show Value Column", self, checkable=True, checked=True,
            statusTip="Shows or hides the Value column")
        self.col_value_action.setShortcut("Ctrl+3")
        assert self.col_value_action.toggled.connect(self.show_value_column)

        self.col_pos_action = QtGui.QAction(
            "Show Line:Col Column", self, checkable=True, checked=True,
            statusTip="Shows or hides the 'Line : Col' column")
        self.col_pos_action.setShortcut("Ctrl+4")
        assert self.col_pos_action.toggled.connect(self.show_pos_column)

        self.search_box = SearchLineEdit(QtGui.QPixmap(r"images/search_icon.png"), QtGui.QPixmap(r"images/search_icon.png"))

    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("&New", self.new_file, "Ctrl+N")
        file_menu.addAction("&Open...", self.open_file, "Ctrl+O")
        #file_menu.addAction("C&lose", self.close_window, "Ctrl+W")
        file_menu.addAction("E&xit", self.quit_application, "Ctrl+Q")

        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.my_test, "Ctrl+T")

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.col_field_action)
        view_menu.addAction(self.col_class_action)
        view_menu.addAction(self.col_value_action)
        view_menu.addAction(self.col_pos_action)

        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)

    def _setup_views(self):
        """ Creates the UI widgets. 
        """
        central_splitter = QtGui.QSplitter(self, orientation=QtCore.Qt.Horizontal)
        self.setCentralWidget(central_splitter)
        central_layout = QtGui.QHBoxLayout()
        central_splitter.setLayout(central_layout)

        # Create base tree widget
        self.ast_tree = AstTreeWidget()
        central_layout.addWidget(self.ast_tree)

        # Editor widget
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(13)

        self.editor = QtGui.QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(font)
        self.editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.editor.setStyleSheet("selection-color: black; selection-background-color: yellow;")
        central_layout.addWidget(self.editor)

        # Splitter parameters
        central_splitter.setCollapsible(0, False)
        central_splitter.setCollapsible(1, False)
        central_splitter.setSizes([500, 500])
        central_splitter.setStretchFactor(0, 0.5)
        central_splitter.setStretchFactor(1, 0.5)

        # Connect signals
        assert self.ast_tree.currentItemChanged.connect(self.highlight_node)


    def new_file(self):
        """ Clears the widgets """
        self._file_name = ""
        self._source_code = ""
        self.editor.clear()
        # self._fill_ast_tree_widget()
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
        self.editor.setPlainText(self._source_code)

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
        """ Opens a file and sets self._file_name and self._source code if succesful
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

    def _fill_ast_tree_widget(self):
        """
        Populates the tree widget.
        """
        syntax_tree = ast.parse(self._source_code, filename=self._file_name, mode=self._mode)
        self.ast_tree.make_tree_from(syntax_tree)


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
        print("search_box is now '%s'" % self.search_box.text())

        items = self.ast_tree.findItems(
            self.search_box.text(),
            QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive,
            column=AstTreeWidget.COL_NODE
        )
        print( "Found %d items" % len(items))
        if len(items) > 0:
            print(items[0])
            self.ast_tree.setCurrentItem(items[0])
            self.ast_tree.expandItem(items[0])



    @QtCore.Slot(int)
    def show_field_column(self, checked):
        """ Shows or hides the field column"""
        self.ast_tree.setColumnHidden(AstTreeWidget.COL_FIELD, not checked)

    @QtCore.Slot(int)
    def show_class_column(self, checked):
        """ Shows or hides the class column"""
        self.ast_tree.setColumnHidden(AstTreeWidget.COL_CLASS, not checked)

    @QtCore.Slot(int)
    def show_value_column(self, checked):
        """ Shows or hides the value column"""
        self.ast_tree.setColumnHidden(AstTreeWidget.COL_VALUE, not checked)

    @QtCore.Slot(int)
    def show_pos_column(self, checked):
        """ Shows or hides the line:col column"""
        self.ast_tree.setColumnHidden(AstTreeWidget.COL_POS, not checked)

    def my_test(self):
        """ Function for testing """
        pass

    def about(self):
        """ Shows the about message window. """
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def close_window(self):
        """ Closes the window """
        self.close()

    def quit_application(self):
        """ Closes all windows """
        app = QtGui.QApplication.instance()
        app.closeAllWindows()

# pylint: enable=R0901, R0902, R0904, W0201

if __name__ == '__main__':
    sys.exit(view(source_code="print a + 5 + 6  / 3.7", mode='eval', width=800, height=600))
