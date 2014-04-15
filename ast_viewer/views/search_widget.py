__author__ = 'Chick Markley'

from PySide import QtGui, QtCore


class SearchLineEdit(QtGui.QLineEdit):
    def __init__(self, parent=None, on_changed=None, on_next=None):
        QtGui.QLineEdit.__init__(self, parent)

        self.clearButton = QtGui.QToolButton(self)
        self.clearButton.setIcon(
            QtGui.QIcon.fromTheme(
                "system-close",
                fallback=QtGui.QIcon(QtGui.QPixmap(r"images/close_icon.png"))
            )
        )
        #self.clearButton.setIconSize(clear_pixmap.size())
        self.clearButton.setCursor(QtCore.Qt.ArrowCursor)
        self.clearButton.setStyleSheet("QToolButton { border: none; padding: 0px;}")
        self.clearButton.hide()
        self.clearButton.clicked.connect(self.clear)
        self.textChanged.connect(self.updateCloseButton)
        if on_changed:
            self.textChanged.connect(on_changed)

        self.searchButton = QtGui.QToolButton(self)
        self.searchButton.setIcon(
            QtGui.QIcon.fromTheme(
                "system-search",
                fallback=QtGui.QIcon(QtGui.QPixmap(r"images/search_icon.png"))
            )
        )
#        self.searchButton.setIcon(QtGui.QIcon(search_pixmap))
        #self.searchButton.setIconSize(search_pixmap.size())
        self.searchButton.setStyleSheet("QToolButton { border: none; padding: 0px;}")
        if on_next:
            self.searchButton.clicked.connect(on_next)

        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet(
            "QLineEdit { padding-left: %spx; padding - right: % spx;} " %
            (self.searchButton.sizeHint().width() + frameWidth + 1, self.clearButton.sizeHint().width() + frameWidth + 1)
        )
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(),
        self.searchButton.sizeHint().width() +
        self.clearButton.sizeHint().width() + frameWidth * 2 + 2),
        max(msz.height(),
        self.clearButton.sizeHint().height() + frameWidth * 2 + 2))

    #        self.searchMenu = QtGui.QMenu(self.searchButton)
    #        self.searchButton.setMenu(self.searchMenu)
    #        self.searchMenu.addAction("Google")
    #        self.searchButton.setPopupMode(QtGui.QToolButton.InstantPopup)

    def resizeEvent(self, event):
        sz = self.clearButton.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.clearButton.move(self.rect().right() - frameWidth -
                          sz.width(),
                          (self.rect().bottom() + 1 - sz.height()) / 2)
        self.searchButton.move(self.rect().left() + 1,
                           (self.rect().bottom() + 1 - sz.height()) / 2)

    def updateCloseButton(self, text):
        if text:
            self.clearButton.setVisible(True)
        else:
            self.clearButton.setVisible(False)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = SearchLineEdit(
        QtGui.QPixmap(r"images/search_icon.png"),
        QtGui.QPixmap(r"images/search_icon.png")
    )
    w.show()
    app.exec_()
