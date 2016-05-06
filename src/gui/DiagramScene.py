from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

from model.AbstractItem import Connector

class DiagramScene(QtGui.QGraphicsScene):
    '''Drawing Area.
    
    :member editor: Parent `gui.DiagramEditor`.
    :member hovering: Flag determining, whether hovering is happening. (Workaround, since hovering is not forwarded).
    '''
    def __init__(self, parent=None):
        '''Create Diagram Scene.
        
        :param parent: Parent `gui.DiagramEditor`.
        '''
        super(DiagramScene, self).__init__(parent)
        self.editor=parent
        self.hovering = None
    #------------------------------------------------------------------------------------------------
    
    def mouseMoveEvent(self, event):
        '''Forward mouseMoveEvent during arc creation and reimplement hovering of `model.AbstractItem.Connector`.
        
        :param event: `QtGui.mouseMoveEvent`.
        '''
        hovering = None
        for item in self.items( event.scenePos() ):
            if issubclass(item.__class__, Connector):
                hovering = item
        # Left
        if hovering is None and self.hovering is not None:
            # Emit hoverLeave on self.slotHover
            self.hovering.hoverLeaveEvent(event)
        # Entered
        if hovering is not None and self.hovering is None:
            # Emit hoverEvent on hoverslot
            hovering.hoverEnterEvent(event)
        if hovering is not None and self.hovering is not None:
            self.hovering.hoverLeaveEvent(event)
            hovering.hoverEnterEvent(event)
                        
        # Save for next move
        self.hovering = hovering
        
        self.editor.sceneMouseMoveEvent(event)
        super(DiagramScene, self).mouseMoveEvent(event)
    #------------------------------------------------------------------------------------------------
    
#     def wheelEvent(self, event):
#         QtGui.QGraphicsScene.wheelEvent(self, event)
#     #------------------------------------------------------------------------------------------------
    
    def mouseReleaseEvent(self, event):
        '''Forward mouseReleaseEvent during arc creation.
        
        :param event: `QtGui.mouseReleaseEvent`.
        '''
        self.editor.sceneMouseReleaseEvent(event)
        super(DiagramScene, self).mouseReleaseEvent(event)
    #------------------------------------------------------------------------------------------------
    
#     def mouseDoubleClickEvent (self, event):
#         QtGui.QGraphicsScene.mouseDoubleClickEvent(self, event)
#     #-----------------------------------------------------------------------------------------------
    
    
#========================================================================================================================
