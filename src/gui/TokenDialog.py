# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TokenDialog.ui'
#
# Created: Fri Apr  1 12:15:48 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys


class TokenDialog(QtGui.QDialog):
    '''Dialog to choose a color for new token'''
    def __init__(self, parent=None, title="Choose Colour and Amount of the Token"):
        '''Create token dialog.
        
        :param parent: Parent `gui.DiagramEditor`.
        :param title: Window Tilte
        '''
        super(TokenDialog, self).__init__(parent)
        self.setWindowTitle(title)
        
        self.editor = parent
            
        self.resize(361, 213)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setMargin(0)
        self.listWidget = QtGui.QListWidget(self)
        self.verticalLayout.addWidget(self.listWidget)
        
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.checkBox = QtGui.QCheckBox(self)
        self.checkBox.setText("Initial Marking")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.spinBox = QtGui.QSpinBox(self)
        self.spinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.spinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.horizontalLayout_2.addWidget(self.spinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.pushButton = QtGui.QPushButton(self)
        self.pushButton.setText("Ok")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtGui.QPushButton(self)
        self.pushButton_2.setText("Cancel")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.listEntry = ""
        self.initMarking = False
        self.countToken = 1
        
        self.spinBox.setValue(self.countToken)
        
        for idx in range(0, self.editor.colorListWidget.count()-1 ):
            self.listWidget.addItem( QtGui.QListWidgetItem( self.editor.colorListWidget.item(idx) ) )
            
        self.listWidget.itemSelectionChanged.connect(self.setListEntry)
        self.checkBox.stateChanged.connect(self.setInitMarking)
        self.spinBox.valueChanged.connect(self.setCountToken)
        self.pushButton.clicked.connect(self.ok)
        self.pushButton_2.clicked.connect(self.cancel)
    #------------------------------------------------------------------------------------------------
    
    def setCountToken(self, value):
        '''Set token count.
        
        :param value:
        '''
        self.countToken = value
    #------------------------------------------------------------------------------------------------

    def getCountToken(self):
        '''
        :return self.countToken:
        '''
        return self.countToken
    #------------------------------------------------------------------------------------------------
    
    def setInitMarking(self, value):
        '''Set initial Marking.
        
        :param value:
        '''
        if value == 2:
            self.initMarking = True
    #------------------------------------------------------------------------------------------------

    def getInitMarking(self):
        '''
        :return self.initMarking:
        '''
        return self.initMarking
    #------------------------------------------------------------------------------------------------
        
    def setListEntry(self):
        '''Add new color to list.
        
        '''
        self.listEntry = self.listWidget.currentItem().data(QtCore.Qt.DisplayRole)        
    #------------------------------------------------------------------------------------------------
    
    def getListEntry(self):        
        '''
        :return self.listEntry:
        '''
        return self.listEntry
    #------------------------------------------------------------------------------------------------
    
    def ok(self):  
        '''
        
        '''
        if len( self.listWidget.selectedItems() ) > 0:
            self.accept()
    #------------------------------------------------------------------------------------------------
    
    def cancel(self):
        '''
        
        '''
        self.close()
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================



