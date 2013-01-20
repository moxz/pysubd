from PyQt4 import QtCore, QtGui
import os

class FileDialog(QtGui.QFileDialog):
    def __init__(self, *args):
        QtGui.QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QtGui.QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QtGui.QTreeView)
        self.selectedFiles = []

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                pth = str(self.directory().absoluteFilePath(i.data().toString()))
                if os.path.isdir(pth):
                    pth = pth + '/'
                files.append(pth)
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles
