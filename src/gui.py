# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Thu Jul  7 00:46:09 2011
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
        MainWindow.resize(720, 335)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(720, 335))
        MainWindow.setMaximumSize(QtCore.QSize(720, 335))
        MainWindow.setAcceptDrops(True)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setAcceptDrops(True)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(10, 10, 591, 301))
        self.scrollArea.setAcceptDrops(True)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 587, 297))
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
        self.progressUpdate.setObjectName(_fromUtf8("progressUpdate"))
        self.verticalLayout_2.addWidget(self.progressUpdate)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(603, 20, 101, 281))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.browseButton = QtGui.QPushButton(self.widget)
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.verticalLayout.addWidget(self.browseButton)
        self.cancelButton = QtGui.QPushButton(self.widget)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.verticalLayout.addWidget(self.cancelButton)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.foundlcdNumber = QtGui.QLCDNumber(self.widget)
        self.foundlcdNumber.setStyleSheet(_fromUtf8("background-color: rgb(15, 15, 15);"))
        self.foundlcdNumber.setNumDigits(5)
        self.foundlcdNumber.setObjectName(_fromUtf8("foundlcdNumber"))
        self.verticalLayout.addWidget(self.foundlcdNumber)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.availablelcdNumber = QtGui.QLCDNumber(self.widget)
        self.availablelcdNumber.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 0);"))
        self.availablelcdNumber.setNumDigits(5)
        self.availablelcdNumber.setObjectName(_fromUtf8("availablelcdNumber"))
        self.verticalLayout.addWidget(self.availablelcdNumber)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.downloadedlcdNumber = QtGui.QLCDNumber(self.widget)
        self.downloadedlcdNumber.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 0);"))
        self.downloadedlcdNumber.setFrameShape(QtGui.QFrame.Box)
        self.downloadedlcdNumber.setNumDigits(5)
        self.downloadedlcdNumber.setObjectName(_fromUtf8("downloadedlcdNumber"))
        self.verticalLayout.addWidget(self.downloadedlcdNumber)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 720, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "pysubd", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setText(QtGui.QApplication.translate("MainWindow", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Total files found:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Available Subs:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Downloaded:", None, QtGui.QApplication.UnicodeUTF8))

