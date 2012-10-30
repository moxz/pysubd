#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QObject, pyqtSlot
from gui.widgets import FileDialog
from SubtitleDownload import SubtitleDownload
import sys
import platform
if platform.system() == 'Windows' and platform.release() == '7':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('PySubD')

import utils
logger = utils.logger
communicator = utils.communicator

class PySubD(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = uic.loadUi('gui/mainwindow.ui', self)
        self.tobeSearched = []
        self.ui.progressUpdate.append('-----------------------------------PySubD Subtitle Downloader-----------------------------------'
                )
        self.ui.progressUpdate.append('----------------------Drag and drop your movie files or folders here------------------------'
                )
        self.subd = SubtitleDownload()
        
        self.connect(self.subd, QtCore.SIGNAL('updateAvailable()'),
                     self.updateAvailable)
        #New style PyQT signal and slots
        self.ui.cancelButton.clicked.connect(self.cancelDownload)
        self.ui.browseButton.clicked.connect(self.openFileDialog)
        self.ui.lang_selector.currentIndexChanged.connect(self.changeLanguage)
        
        communicator.updategui.connect(self.append_updates)
        communicator.found_video_file.connect(self.update_found_files)
        communicator.downloaded_sub.connect(self.update_downloaded_subs)
        communicator.all_download_complete.connect(self.download_complete)

        self.cancelled = False
        self.lang = str(self.ui.lang_selector.currentText())
        self.ui.authorLabel.setOpenExternalLinks(True)
        self.ui.cancelButton.setDisabled(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.cancelled = False
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))

            self.ui.cancelButton.setEnabled(True)
            
            if self.tobeSearched:
                self.tobeSearched.extend(links)
            else:
                self.tobeSearched.extend(links)
                self.ui.lang_selector.setDisabled(True)
                self.subd.init(links, self.lang)
        else:
            event.ignore()

    @pyqtSlot()
    def openFileDialog(self):
        self.cancelled = False
        d = FileDialog()
        d.exec_()
        x = d.filesSelected()

        if x:
            self.ui.cancelButton.setEnabled(True)
            self.ui.browseButton.setDisabled(True)
            self.tobeSearched.extend(x)
            self.ui.lang_selector.setDisabled(True)
            self.subd.init(x, self.lang)

    @pyqtSlot()
    def cancelDownload(self):
        self.cancelled = True
        self.subd.stopTask()
        self.ui.cancelButton.setDisabled(True)
        self.ui.browseButton.setEnabled(True)
        self.ui.lang_selector.setEnabled(True) 

    @pyqtSlot()
    def changeLanguage(self):
        language = str(self.ui.lang_selector.currentText())
        self.lang = language
    
    @pyqtSlot(object)
    def download_complete(self, donepaths):
        for path in donepaths:
            self.tobeSearched.remove(path)
        if self.tobeSearched and not self.cancelled:
            self.ui.browseButton.setDisabled(True)
            self.ui.lang_selector.setDisabled(True) 
            self.ui.cancelButton.setEnabled(True)
            self.subd.init(self.tobeSearched, self.lang)
        else:
            self.ui.cancelButton.setDisabled(True)
            self.ui.lang_selector.setEnabled(True)
            self.ui.browseButton.setEnabled(True)

    @pyqtSlot(object)
    def append_updates(self, update):
        logger.info(update)
        self.ui.progressUpdate.append(update)
        self.ui.scrollArea.verticalScrollBar().setValue(self.ui.scrollArea.verticalScrollBar().maximum())

    @pyqtSlot()
    def update_found_files(self):
        self.ui.foundlcdNumber.display(int(self.ui.foundlcdNumber.value()) + 1)

    @pyqtSlot()
    def updateAvailable(self):
        self.ui.availablelcdNumber.display(int(self.ui.availablelcdNumber.value()) + 1)

    @pyqtSlot()
    def update_downloaded_subs(self):
        self.ui.downloadedlcdNumber.display(int(self.ui.downloadedlcdNumber.value()) + 1)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = PySubD()
    window.show()
    sys.exit(app.exec_())
