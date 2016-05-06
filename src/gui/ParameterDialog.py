from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class ParameterDialog(QtGui.QDialog):
    def __init__(self, node, parent=None):
        super(ParameterDialog, self).__init__(parent)
        self.button = QtGui.QPushButton('Ok', self)
        self.button2 = QtGui.QPushButton('Cancel', self)
        self.lineEdit = QtGui.QPushButton(node.getName(), self)
        vl = QtGui.QVBoxLayout(self)
        
        hl = QtGui.QVBoxLayout(self)
        hl.addWidget(self.button)
        hl.addWidget(self.button2)
        
        vl.addLayout(hl)
        self.button.clicked.connect(self.OK)
    #------------------------------------------------------------------------------------------------
        
    def OK(self):
        self.close()
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================
