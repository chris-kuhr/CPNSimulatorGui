from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import inspect
import math
from collections import Counter, deque

import snakes.plugins
from snakes.nets import *

class TokenItem(QtGui.QGraphicsEllipseItem):
    '''A String Token. 
        
    :member editor: Referenced editor.
    :member countToken: Number of tokens.
    :member countTokenLabel: Visible representation of the number of tokens.
    :member token: String value of token, shown in tooltip     
    '''
    def __init__(self, editor, token, count, qpos, parent=None):        
        '''Create a token.
        
        :param editor: DiagramEditor. Editor to show in. 
        :param token: Token value.
        :param count: Number of Tokens to create.
        :param qpos: Parent top right position.  
        :param parent=None: Parent Place Element
        '''
        QtGui.QGraphicsEllipseItem.__init__(self, qpos, parent)
        self.editor = editor
        self.setZValue(19)
        self.countToken = count
        self.countTokenLabel = QtGui.QGraphicsTextItem("%d"%self.countToken, self)
        self.countTokenLabel.setPos(QtCore.QPointF( qpos.x()-1, qpos.y()-4 ))
        self.setBrush(QtGui.QBrush(QtCore.Qt.green))
        self.token = token
        self.setToolTip( str(self.token) )
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable )
    #------------------------------------------------------------------------------------------------
            
            
    def setCountToken(self, count):
        '''Token count, shown in green circle.
        
        :param count: Number to show.
        '''
        self.countToken = count
        self.countTokenLabel.setPlainText("%d"%self.countToken)
    #------------------------------------------------------------------------------------------------
    
    
    def deleteItemLocal(self):
        '''Capture delete event and call editor delete function.'''
        self.editor.deleteItems(self.editor, [self])
    #------------------------------------------------------------------------------------------------


    def contextMenuEvent(self, event):
        '''Generate Context menu on context menu event.
        
        :param event: QContextMenuEvent.   
        '''
        menu = QtGui.QMenu()
        self.delete = menu.addAction('Delete')
        self.delete.triggered.connect(self.deleteItemLocal)
        menu.exec_(event.screenPos())
    #------------------------------------------------------------------------------------------------

#========================================================================================================================
if __name__ == "__main__":
    import doctest
    print( doctest.testmod() )
