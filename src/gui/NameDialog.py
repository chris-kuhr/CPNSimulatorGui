from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

class NameDialog(QtGui.QDialog):
    '''
    
    '''
    def __init__(self, parent=None, item=None, title="Unnamed", default="a"):
        '''
        
        :param parent: Parent `gui.DiagramEditor`.
        :param item: Store item for later processing.
        :param title: Window title.
        :param default: Default string text.
        '''
        super(NameDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setText( default )
        self.lineEdit.setFocus( )
        self.button = QtGui.QPushButton('Ok', self)
        self.button2 = QtGui.QPushButton('Cancel', self)
        vl = QtGui.QHBoxLayout(self)
        vl.addWidget(self.lineEdit)
        if isinstance(item, str):
            if "transition" in item:
                self.checkBox = QtGui.QCheckBox("Subnet")
                vl.addWidget(self.checkBox)
            
        hl = QtGui.QHBoxLayout()
        hl.addWidget(self.button)
        hl.addWidget(self.button2)
        vl.addLayout(hl)
        self.button.clicked.connect(self.ok)
        self.button2.clicked.connect(self.cancel)
        self.item = item        
    #------------------------------------------------------------------------------------------------
    
    def getItem(self):
        '''
        :return self.item:
        '''
        return self.item
    #------------------------------------------------------------------------------------------------

    def getName(self):
        '''
        :return self.lineEdit.text():
        '''
        return self.lineEdit.text()
    #------------------------------------------------------------------------------------------------
        
    def ok(self):        
        '''
        
        '''
        self.accept()
    #------------------------------------------------------------------------------------------------
    
    def cancel(self):
        '''
        
        '''
        self.close()
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================
