# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'flogger.ui'
#
# Created: Fri Feb  3 06:36:16 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuConfig = QtGui.QMenu(self.menubar)
        self.menuConfig.setObjectName(_fromUtf8("menuConfig"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuRun = QtGui.QMenu(self.menubar)
        self.menuRun.setObjectName(_fromUtf8("menuRun"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionConfig = QtGui.QAction(MainWindow)
        self.actionConfig.setObjectName(_fromUtf8("actionConfig"))
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionHelp_2 = QtGui.QAction(MainWindow)
        self.actionHelp_2.setObjectName(_fromUtf8("actionHelp_2"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionImport = QtGui.QAction(MainWindow)
        self.actionImport.setObjectName(_fromUtf8("actionImport"))
        self.actionExport = QtGui.QAction(MainWindow)
        self.actionExport.setObjectName(_fromUtf8("actionExport"))
        self.actionStart = QtGui.QAction(MainWindow)
        self.actionStart.setObjectName(_fromUtf8("actionStart"))
        self.actionStop = QtGui.QAction(MainWindow)
        self.actionStop.setObjectName(_fromUtf8("actionStop"))
        self.actionEdit = QtGui.QAction(MainWindow)
        self.actionEdit.setObjectName(_fromUtf8("actionEdit"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionQuit)
        self.menuConfig.addAction(self.actionNew)
        self.menuConfig.addAction(self.actionEdit)
        self.menuConfig.addAction(self.actionImport)
        self.menuConfig.addAction(self.actionExport)
        self.menuHelp.addAction(self.actionHelp_2)
        self.menuHelp.addAction(self.actionAbout)
        self.menuRun.addAction(self.actionStart)
        self.menuRun.addAction(self.actionStop)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuConfig.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL(_fromUtf8("activated()")), MainWindow.close)
        QtCore.QObject.connect(self.actionStart, QtCore.SIGNAL(_fromUtf8("activated()")), self.actionStart.trigger)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuConfig.setTitle(_translate("MainWindow", "Config", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.menuRun.setTitle(_translate("MainWindow", "Run", None))
        self.actionConfig.setText(_translate("MainWindow", "Config", None))
        self.actionHelp.setText(_translate("MainWindow", "Help", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionHelp_2.setText(_translate("MainWindow", "Help", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionNew.setText(_translate("MainWindow", "New", None))
        self.actionImport.setText(_translate("MainWindow", "Import", None))
        self.actionExport.setText(_translate("MainWindow", "Export", None))
        self.actionStart.setText(_translate("MainWindow", "Start", None))
        self.actionStop.setText(_translate("MainWindow", "Stop", None))
        self.actionEdit.setText(_translate("MainWindow", "Edit", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionQuit.setToolTip(_translate("MainWindow", "Quit Flogger", None))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))

