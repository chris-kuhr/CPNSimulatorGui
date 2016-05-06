from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

class LibraryModel(QtGui.QStandardItemModel):
    '''Abstract class for drag and drop support'''
    def __init__(self, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
    #------------------------------------------------------------------------------------------------
        
    def mimeTypes(self):
        return ['component/name']
    #------------------------------------------------------------------------------------------------
    
    def mimeData(self, idxs):
        mimedata = QtCore.QMimeData()
        for idx in idxs:
            if idx.isValid():
                txt = self.data(idx, QtCore.Qt.DisplayRole)
                mimedata.setData('component/name', txt)
        return mimedata
    #------------------------------------------------------------------------------------------------    
    
#========================================================================================================================
