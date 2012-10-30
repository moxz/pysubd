# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/mainwindow.ui'
#
# Created: Tue Aug 21 19:37:13 2012
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(730, 350)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(730, 350))
        MainWindow.setMaximumSize(QtCore.QSize(730, 350))
        MainWindow.setAcceptDrops(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/Pi-symbol.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setAcceptDrops(True)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(10, 10, 591, 311))
        self.scrollArea.setAcceptDrops(True)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 587, 307))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.progressUpdate = QtGui.QTextBrowser(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressUpdate.sizePolicy().hasHeightForWidth())
        self.progressUpdate.setSizePolicy(sizePolicy)
        self.progressUpdate.setMaximumSize(QtCore.QSize(720, 16777215))
        self.progressUpdate.setStyleSheet(_fromUtf8("font: 10pt \"Serif\";\n"
"gridline-color: qconicalgradient(cx:0.5, cy:0.5, angle:0, stop:0 rgba(255, 255, 255, 255), stop:0.373979 rgba(255, 255, 255, 255), stop:0.373991 rgba(33, 30, 255, 255), stop:0.624018 rgba(33, 30, 255, 255), stop:0.624043 rgba(255, 0, 0, 255), stop:1 rgba(255, 0, 0, 255));"))
        self.progressUpdate.setLineWidth(0)
        self.progressUpdate.setObjectName(_fromUtf8("progressUpdate"))
        self.verticalLayout_2.addWidget(self.progressUpdate)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(610, 20, 114, 251))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lang_selector = QtGui.QComboBox(self.layoutWidget)
        self.lang_selector.setObjectName(_fromUtf8("lang_selector"))
        self.lang_selector.addItem(_fromUtf8(""))
        self.lang_selector.addItem(_fromUtf8(""))
        self.lang_selector.addItem(_fromUtf8(""))
        self.lang_selector.addItem(_fromUtf8(""))
        self.lang_selector.addItem(_fromUtf8(""))
        self.lang_selector.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.lang_selector)
        self.browseButton = QtGui.QPushButton(self.layoutWidget)
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.verticalLayout.addWidget(self.browseButton)
        self.cancelButton = QtGui.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.verticalLayout.addWidget(self.cancelButton)
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.foundlcdNumber = QtGui.QLCDNumber(self.layoutWidget)
        self.foundlcdNumber.setStyleSheet(_fromUtf8("background-color: rgb(15, 15, 15);"))
        self.foundlcdNumber.setNumDigits(5)
        self.foundlcdNumber.setObjectName(_fromUtf8("foundlcdNumber"))
        self.verticalLayout.addWidget(self.foundlcdNumber)
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.downloadedlcdNumber = QtGui.QLCDNumber(self.layoutWidget)
        self.downloadedlcdNumber.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 0);"))
        self.downloadedlcdNumber.setFrameShape(QtGui.QFrame.Box)
        self.downloadedlcdNumber.setNumDigits(5)
        self.downloadedlcdNumber.setObjectName(_fromUtf8("downloadedlcdNumber"))
        self.verticalLayout.addWidget(self.downloadedlcdNumber)
        self.authorLabel = QtGui.QLabel(self.centralwidget)
        self.authorLabel.setGeometry(QtCore.QRect(620, 280, 101, 16))
        self.authorLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.authorLabel.setTextFormat(QtCore.Qt.RichText)
        self.authorLabel.setObjectName(_fromUtf8("authorLabel"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 730, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "pysubd", None, QtGui.QApplication.UnicodeUTF8))
        self.lang_selector.setItemText(0, QtGui.QApplication.translate("MainWindow", "English", None, QtGui.QApplication.UnicodeUTF8))
        self.lang_selector.setItemText(1, QtGui.QApplication.translate("MainWindow", "Greek", None, QtGui.QApplication.UnicodeUTF8))
        self.lang_selector.setItemText(2, QtGui.QApplication.translate("MainWindow", "French", None, QtGui.QApplication.UnicodeUTF8))
        self.lang_selector.setItemText(3, QtGui.QApplication.translate("MainWindow", "Portuguese(Br)", None, QtGui.QApplication.UnicodeUTF8))
        self.lang_selector.setItemText(4, QtGui.QApplication.translate("MainWindow", "Italian", None, QtGui.QApplication.UnicodeUTF8))
        self.lang_selector.setItemText(5, QtGui.QApplication.translate("MainWindow", "Spanish", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setText(QtGui.QApplication.translate("MainWindow", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Video files found:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Downloaded Subs:", None, QtGui.QApplication.UnicodeUTF8))
        self.authorLabel.setText(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">By </span><a href=\"https://about.me/sahilgupta/\"><span style=\" font-family:\'MS Shell Dlg 2\'; text-decoration: underline; color:#0000ff;\">Sahil Gupta</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import resourcefile_rc
