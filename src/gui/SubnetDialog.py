from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

from gui.DiagramEditor import DiagramEditor

class SubnetDialog(QtGui.QDialog):
    '''Dialog for subnet creation'''
    def __init__(self, mainWindow, parent=None, superNet=None, subnet=None):
        '''Create net subnet editor widget.
        
        :param mainWindow: `gui.MainWindow`. Main application window.  
        :param parent: Parent `gui.DiagramEditor`.
        :param superNet:
        :param subnet: Subnet string name
        '''
        super(SubnetDialog, self).__init__(parent)
        self.parent = parent
        self.superNet = superNet
        self.subnet = subnet
        self.setWindowTitle("Subnet: %s"%self.subnet)
        
        vl = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom, parent=self)
        
        self.editor = DiagramEditor(mainWindow=mainWindow, parent=self, workingDir=self.parent.workingDir, subnet=self.subnet)
        self.editor.resize(700, 800)
        
        vl.addWidget(self.editor)
    #------------------------------------------------------------------------------------------------
    
    def closeEvent(self, event):
        '''
        
        :param event:
        '''
        self.close() 
    #-------------------------------------------------------------------------------------------------------------------------
    
    def cancel(self):
        '''
        
        '''
        self.close()
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================
