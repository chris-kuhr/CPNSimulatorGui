# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TokenDialog.ui'
#
# Created: Fri Apr  1 13:33:57 2016
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

class Ui_TokenDialog(object):
    def setupUi(self, TokenDialog):
        TokenDialog.setObjectName(_fromUtf8("TokenDialog"))
        TokenDialog.resize(361, 213)
        self.centralwidget = QtGui.QWidget(TokenDialog)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 361, 211))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.listWidget = QtGui.QListWidget(self.verticalLayoutWidget)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.checkBox = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.spinBox = QtGui.QSpinBox(self.verticalLayoutWidget)
        self.spinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.spinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.horizontalLayout_2.addWidget(self.spinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        TokenDialog.setCentralWidget(self.centralwidget)

        self.retranslateUi(TokenDialog)
        QtCore.QMetaObject.connectSlotsByName(TokenDialog)

    def retranslateUi(self, TokenDialog):
        TokenDialog.setWindowTitle(_translate("TokenDialog", "MainWindow", None))
        self.checkBox.setText(_translate("TokenDialog", "Initial Marking", None))
        self.pushButton.setText(_translate("TokenDialog", "PushButton", None))
        self.pushButton_2.setText(_translate("TokenDialog", "PushButton", None))

