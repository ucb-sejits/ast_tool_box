__author__ = 'Chick Markley'

import sys

from PySide import QtGui


app = QtGui.QApplication(sys.argv)

wid = QtGui.QWidget()
wid.resize(250, 150)
wid.setWindowTitle('Simple')

# NOTICE: the difference
QtGui.QIcon.setThemeSearchPaths(["/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources"])
print "search paths", QtGui.QIcon.themeSearchPaths()
print "themeName:", QtGui.QIcon.themeName()
print "hasThemeIcon:", QtGui.QIcon.hasThemeIcon("edit-undo")

# qutils.config_theme_path()

print "themeName:", QtGui.QIcon.themeName()
print "hasThemeIcon:", QtGui.QIcon.hasThemeIcon("edit-undo")
print

my_online = QtGui.QIcon("/path/to/my_online.png")

icon = QtGui.QIcon.fromTheme("user-online", my_online)
print "icon not found:", icon.isNull()
print "availableSizes:", icon.availableSizes()


wid.setWindowIcon(
    QtGui.QIcon.fromTheme("system-open")
)
wid.show()

sys.exit(app.exec_())