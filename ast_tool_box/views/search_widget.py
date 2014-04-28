__author__ = 'Chick Markley'

from PySide import QtGui, QtCore


class SearchLineEdit(QtGui.QLineEdit):
    def __init__(self, parent=None, on_changed=None, on_next=None):
        QtGui.QLineEdit.__init__(self, parent)

        self.clear_button = QtGui.QToolButton(self)
        self.clear_button.setIcon(
            QtGui.QIcon.fromTheme(
                "system-close",
                fallback=QtGui.QIcon(QtGui.QPixmap(r"images/close_icon.png"))
            )
        )
        #self.clear_button.setIconSize(clear_pixmap.size())
        self.clear_button.setCursor(QtCore.Qt.ArrowCursor)
        self.clear_button.setStyleSheet("QToolButton { border: none; padding: 0px;}")
        self.clear_button.hide()
        self.clear_button.clicked.connect(self.clear)
        self.textChanged.connect(self.updateCloseButton)
        if on_changed:
            self.textChanged.connect(on_changed)

        self.search_button = QtGui.QToolButton(self)
        self.search_button.setIcon(
            QtGui.QIcon.fromTheme(
                "system-search",
                fallback=QtGui.QIcon(QtGui.QPixmap(r"images/search_icon.png"))
            )
        )
        self.search_button.setToolTip("Clicking this will advance search to next item")
        self.search_button.setStyleSheet("QToolButton { border: none; padding: 0px;}")

        if on_next:
            self.search_button.clicked.connect(on_next)
            self.returnPressed.connect(on_next)

        frame_width = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet(
            "QLineEdit { padding-left: %spx; padding - right: % spx;} " %
            (self.search_button.sizeHint().width() + frame_width + 1, self.clear_button.sizeHint().width() + frame_width + 1)
        )
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(),
        self.search_button.sizeHint().width() +
        self.clear_button.sizeHint().width() + frame_width * 2 + 2),
        max(msz.height(),
        self.clear_button.sizeHint().height() + frame_width * 2 + 2))

    #        self.searchMenu = QtGui.QMenu(self.search_button)
    #        self.search_button.setMenu(self.searchMenu)
    #        self.searchMenu.addAction("Google")
    #        self.search_button.setPopupMode(QtGui.QToolButton.InstantPopup)

    def resizeEvent(self, event):
        sz = self.clear_button.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.clear_button.move(self.rect().right() - frameWidth -
                          sz.width(),
                          (self.rect().bottom() + 1 - sz.height()) / 2)
        self.search_button.move(self.rect().left() + 1,
                           (self.rect().bottom() + 1 - sz.height()) / 2)

    def updateCloseButton(self, text):
        if text:
            self.clear_button.setVisible(True)
        else:
            self.clear_button.setVisible(False)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = SearchLineEdit(
        QtGui.QPixmap(r"images/search_icon.png"),
        QtGui.QPixmap(r"images/search_icon.png")
    )
    w.show()
    app.exec_()
