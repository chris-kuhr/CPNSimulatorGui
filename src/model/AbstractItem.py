from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import inspect
import math
from collections import Counter, deque
import logging

import snakes.plugins
from snakes.nets import *

from gui.NameDialog import NameDialog
from gui.TokenDialog import TokenDialog
from gui.ParameterDialog import ParameterDialog

    

class Connector(QtGui.QGraphicsRectItem):
    '''Connector for visual arcs. 
    
    A connector is a socket, to or from which a visual arc may be connected.
    
    :member parent: Parent port place.
    :member orientation: Orientation relative to its parent: "N","NE","E","SE","S","SW","W","NW".
    :member idx: Index assinged from parent.
    :member connectionArc: Reference to the arc connected to this Connector.
    :member posCallbacks: List of callback functions, to calculate position changes.
    :member position: Position relative to parent.
    '''
    def __init__(self, parent, idx):
        '''Create a connector.
        
        :param parent: Parent AbstractItem.
        :param idx: Absolut number in the parent list of connectors.
        '''
        super(Connector, self).__init__(parent)
        self.parent = parent
        self.orientation = None
        self.idx = idx
        self.connectionArc = None
        self.posCallbacks = []
        rect = self.parent.boundingRect()
        self.setFlags(self.ItemIsSelectable | self.ItemSendsScenePositionChanges)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        connectorWidth = rect.width()/6
        connectorHeight = rect.height()/6
        
        self.setPen(QtGui.QPen(QtCore.Qt.gray, 1))
        self.setBrush(QtGui.QBrush(QtCore.Qt.gray))
        self.setAcceptHoverEvents(True)
        self.setFlag( self.ItemStacksBehindParent , True )
        self.setOpacity(0.1)
        self.setZValue(11)
        
        self.position = QtCore.QPointF( 0.0 , 0.0 )
        
        
        if idx == 0:
            self.orientation = ["northWest"]
        elif self.idx == 1:
            self.orientation = ["northWest", "north"]
        elif self.idx == 2 or self.idx == 3:
            self.orientation = ["north"]
        elif self.idx == 4:
            self.orientation = ["north", "northEast"]
        elif self.idx == 5:
            self.orientation = ["northEast"]
        elif self.idx == 6:
            self.orientation = ["northEast", "east"]
        elif self.idx == 7 or self.idx == 8:
            self.orientation = ["east"]
        elif self.idx == 9:
            self.orientation = ["east", "southEast"]
        elif self.idx == 10:
            self.orientation = ["southEast"]
        elif self.idx == 11:
            self.orientation = ["south", "southEast"]
        elif self.idx == 12 or self.idx == 13:
            self.orientation = ["south"]
        elif self.idx == 14:
            self.orientation = ["south", "southWest"]
        elif self.idx == 15:
            self.orientation = ["southWest"]
        elif self.idx == 16:
            self.orientation = ["southWest", "west"]
        elif self.idx == 17 or self.idx == 18:
            self.orientation = ["west"]
        elif self.idx == 19:
            self.orientation = ["west", "northWest"]
            
        
        if self.idx >= 0 and self.idx <= 5:
            self.position = QtCore.QPointF( rect.x() + self.idx * connectorWidth , rect.y() )
            
        elif self.idx > 5 and self.idx < 10:
            self.position = QtCore.QPointF( rect.width() - connectorWidth , rect.y() + ( self.idx - 5 ) * connectorHeight )
            
        elif self.idx >= 10 and self.idx <= 15:
            self.position = QtCore.QPointF( rect.width() - connectorWidth * ( self.idx - 9 ) , rect.height() - connectorHeight )
            
        elif self.idx > 15:
            self.position = QtCore.QPointF( rect.x(), rect.y() + ( 20 - self.idx ) * connectorHeight)       
            
        self.setRect(self.position.x(), self.position.y(), connectorWidth, connectorHeight)
        
    #------------------------------------------------------------------------------------------------
    
    def mousePressEvent(self, event):        
        '''Capture QtGui.mousePressEvent with **Shift-Key** modifier.
        
        :param event: QtGui.mousePressEvent
        '''
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            self.parent.parent.startArc(self)
#         QtGui.QGraphicsRectItem.mousePressEvent(self, event)

    #------------------------------------------------------------------------------------------------
    
    def hoverEnterEvent(self, event):
        '''Make connector visible on hoverEnterEvent.  
        
        :param event: hoverEnterEvent
        '''
        self.setFlag( self.ItemStacksBehindParent , False )
        self.setOpacity(1.0)
        self.setZValue(11)
        self.update()
    #------------------------------------------------------------------------------------------------
    
    
    def hoverLeaveEvent(self, event):
        '''Make connector invisible on hoverLeaveEvent.  
        
        :param event: hoverLeaveEvent
        '''
        self.setFlag( self.ItemStacksBehindParent , True )
        self.setOpacity(0.1)
        self.setZValue(0)
        self.update()
    #------------------------------------------------------------------------------------------------
    
    
    def itemChange(self, change, value):                    
        '''Item position has changed, calculate new position.
        
        :param change: Change event.
        :param value: QtCore.QPointF().
        :return value: QtCore.QPointF(x, y) or super(Connector, self).itemChange(change, value).
        '''
        if change == self.ItemScenePositionHasChanged:
            for cb in self.posCallbacks:                
                cb( value )
            return value
        return super(Connector, self).itemChange(change, value)
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================

class DescriptionCanvas(QtGui.QGraphicsRectItem):
    '''Description area for tokens, exceptions and modes. Toggle with **Ctrl**+**M**. 
    
    In this canvas label, detailed information about the CPN element is shown.
    Firstly the unique name used by the simulator is shown, followed by the visual name, 
    that is assigned by the user. The latter does not have to be unique.
    
    :member parent: Parent CPN element.
    :member label: Visual representation of the information about the CPN element.
    :member text: Unique name of parent CPN element.
    :member visibility: Switch for the visibility of the description canvas.
    '''
    def __init__(self, parent=None):  
        '''Create description canvas.
        
        :param parent: Abstract CPN element.
        '''
        super(DescriptionCanvas, self).__init__(parent)
        self.parent = parent
        self.text = self.parent.uniqueName
        self.setPen(QtGui.QPen(QtCore.Qt.darkYellow, 1))
        self.setBrush(QtGui.QBrush(QtCore.Qt.darkYellow))
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsScenePositionChanges )
        self.label = QtGui.QGraphicsTextItem( "%s: %s"%(self.parent.uniqueName, self.parent.name), parent=self )  
#         self.label.setFlag(self.ItemIsMovable, True)
        rect = self.label.boundingRect()
        self.setRect(rect.x() + 30, rect.y() + 20, rect.width(), rect.height())
        self.label.setPos(rect.x() + 30, rect.y() + 20)
        self.label.setZValue(21)   
        self.setZValue(20)      
        self.visibility = False
        self.setVisibility( self.visibility ) 
    #------------------------------------------------------------------------------------------------
    
    def setVisibility(self, visible):
        '''Set visibility of DescriptionCanvas.
        
        :param visible: True if visible, False if invisible.
        '''
        self.visibility = visible
        self.setVisible( visible )   
        self.label.setVisible( visible )
    #------------------------------------------------------------------------------------------------

    
    def setCanvasString(self, infoString):
        '''Set info string, that appended to the first line.
        
        :param infoString: Info string, may contain line breaks.
        '''
#         self.parent.editor.diagramScene.removeItem(self.label)
        self.label.setPlainText( "%s: %s\n%s"%(self.parent.uniqueName, self.parent.name, infoString))  
#         self.label.setFlag(self.ItemIsMovable, True)
#         self.parent.editor.diagramScene.addItem(self.label)
        rect = self.label.boundingRect()
        pos = self.parent.scenePos()
        self.setRect(pos.x() + 30, pos.y() + 20, rect.width(), rect.height()) 
        self.label.setPos(pos.x() + 30, pos.y() + 20)
#         self.label.setZValue(21)   
#         self.setZValue(20)       
        self.setVisibility(self.visibility)
            
    #------------------------------------------------------------------------------------------------
        
    
#========================================================================================================================

              


class AbstractItem(QtGui.QGraphicsItem):
    '''Base class of the CPN elements transition and place.
    
    :member parent: `gui.DiagramEditor`. Editor to show in. 
    :member tokens: List of `model.TokenItem` s, if inheriting class is `model.PlaceItem` else None
    :member name: Name of the CPN element. 
    :member posCallbacks: List of callback functions, to calculate position changes.
    :member connectorList: List of 20 `Connector` s
    :member planeMap: Dictionary->Set(), mapping the relative orientation of an any other `model.AbstractItem` in the containing editor. 
    :member connectorMap: Dictionary->List(), mapping the relative orientation of the 20 `model.AbstractItem.Connector` s.
    :member nodeType: Determining the type of the item at creation time.        
    :member superNet: The super net is used to determine the editor for port place clones.
    :member label: `QtGui.QGraphicsTextItem`, visual representation of the `model.AbstractItem` s name.     
    :member descCanvas: `gui.AbstractItem.DescriptionCanvas`, showing detailed information.    
    '''
    def __init__(self, parent = None):  
        '''Create abstract item.
        
        :param parent: `gui.DiagramEditor`. Editor to show in. 
        '''
        self.parent = parent
        super(AbstractItem, self).__init__(parent)
        self.tokens = None        
        self.name = ""
        self.posCallbacks = []
        self.connectorList = []
        
        self.setPen(QtGui.QPen(QtCore.Qt.black, 2))
        self.setBrush(QtGui.QBrush(QtCore.Qt.white))
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsScenePositionChanges)
        
        self.planeMap = {
                         "northWest":set(),
                         "north":set(),
                         "northEast":set(),
                         "east":set(),
                         "southEast":set(),
                         "south":set(),
                         "southWest":set(),
                         "west":set()
                         }
        self.connectorMap = {
                         "northWest":[],
                         "north":[],
                         "northEast":[],
                         "east":[],
                         "southEast":[],
                         "south":[],
                         "southWest":[],
                         "west":[]
                         }
    #------------------------------------------------------------------------------------------------
        
        
    def createItem(self, editor, name='Untitled', nodeType="undefined" ):
        '''Create the typed item.
        
        :param editor:  `gui.DiagramEditor`. Editor to show in. 
        :param name: Name of the CPN element. 
        :param nodeType: Determining the type of the item at creation time.        
        :return w, h: Width and height of CPN element, depending on the label length. 
        '''
        self.parent = editor
        self.name = name
        self.nodeType = nodeType        
        self.superNet = self.parent.subnet
        
        self.label = QtGui.QGraphicsTextItem( name, self )        
        
        self.descCanvas = DescriptionCanvas(self)
        
        rect = self.label.boundingRect()        
        w = rect.width() + 20.0
        h = rect.height() + 20.0
        if h < 20:
            h = 20
        if w < 40:
            w = 40
             
        self.setRect(0.0, 0.0, w, h)
        rect = self.label.boundingRect()
        lw, lh = rect.width(), rect.height()
        lx = (w - lw) / 2
        ly = (h - lh) / 2
        self.label.setPos(lx, ly)
        
        rect = self.boundingRect()
        pos = self.scenePos()
        
        for idx in range(0,20):
            connector = Connector(self, idx)
            self.connectorList.append( connector )
            for orientation in connector.orientation:
                self.connectorMap[orientation].append(connector)
        
        if self.tokens is not None:
            for token in self.tokens:
                token.setRect( pos.x() + rect.width(), pos.y(), 10.0, 10.0)
                break      
        return w, h          
    #------------------------------------------------------------------------------------------------
    
    
    def checkItem(self, item, orientation):
        '''Check `item` is of propper type.
        
        :param item: `model.AbstractItem` to lookup.
        :param orientation: Orientation to assign, if type check is passed.
        '''
        try:
            if ( str( item.nodeType )  == str("transition") or str( item.nodeType )  == str("place") ) and item is not self:
                self.planeMap[orientation].add( item )
        except AttributeError:
            pass
    #------------------------------------------------------------------------------------------------
        
    def findItemsInPlanes(self):
        '''Finds the orientation of any other item in the `gui.DiagramScene`.'''
        rect = self.boundingRect()
        
        sceneRect = self.editor.diagramScene.itemsBoundingRect() 
               
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF( 0, -rect.height(), -sceneRect.width(), -sceneRect.height() ) ), mode=QtCore.Qt.ContainsItemShape ):
            self.checkItem( item, "northWest")
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF( 0, -rect.height(), rect.width(), -sceneRect.height() ) ), mode=QtCore.Qt.IntersectsItemShape ):
            self.checkItem( item, "north")     
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF( rect.width(), -rect.height(), sceneRect.width(), -sceneRect.height() ) ), mode=QtCore.Qt.ContainsItemShape ):
            self.checkItem( item, "northEast")            
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF( rect.width(), 0, sceneRect.width(), -rect.height() ) ), mode=QtCore.Qt.IntersectsItemShape ):
            self.checkItem( item, "east")     
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF( rect.width(), 0, +sceneRect.width(), +sceneRect.height() ) ), mode=QtCore.Qt.ContainsItemShape ):
            self.checkItem( item, "southEast") 
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF( 0, 0, rect.width(), +sceneRect.height() ) ), mode=QtCore.Qt.IntersectsItemShape ):
            self.checkItem( item, "south") 
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF(  0, 0, -sceneRect.width(), +sceneRect.height() ) ), mode=QtCore.Qt.ContainsItemShape ):
            self.checkItem( item, "southWest")
        for item in self.editor.diagramScene.items( self.mapToScene( QtCore.QRectF( 0, 0, -sceneRect.width(), -rect.height() ) ), mode=QtCore.Qt.IntersectsItemShape  ):
            self.checkItem( item, "west")
        
#         logging.debug("----------------------------------------------------------")
#         logging.debug(self.planeMap)        
#         logging.debug( "---------------------------------------------Planes of %s"%( self.name  ))
#         logging.debug( "plane northWest" )
#         for item in self.planeMap["northWest"]:            
#             logging.debug( item.name )
#         logging.debug( "plane north" )
#         for item in self.planeMap["north"]:
#             logging.debug( item.name )
#         logging.debug( "plane northEast" )
#         for item in self.planeMap["northEast"]:
#             logging.debug( item.name )
#         logging.debug( "plane east" )
#         for item in self.planeMap["east"]:
#             logging.debug( item.name )
#         logging.debug( "plane southEast" )
#         for item in self.planeMap["southEast"]:
#             logging.debug( item.name )
#         logging.debug( "plane south" )
#         for item in self.planeMap["south"]:
#             logging.debug( item.name )
#         logging.debug( "plane southWest" )
#         for item in self.planeMap["southWest"]:
#             logging.debug( item.name )
#         logging.debug( "plane west" )
#         for item in self.planeMap["west"]:
#             logging.debug( item.name )

    #------------------------------------------------------------------------------------------------
            
            
    def mouseDoubleClickEvent (self, event):
        '''Edit visual name on `QtGui.mouseDoubleClickEvent`.
        
        :param event: `QtGui.mouseDoubleClickEvent`.
        '''
        self.diag = NameDialog( parent=self.parent, title="Rename %s %s"%( type(self), self.name ), default=self.name)
        self.diag.accepted.connect(self.renameElement)
        self.diag.show()
    #-----------------------------------------------------------------------------------------------
    
    
        
    def renameElement(self):         
        '''Capture rename event and call virtual function of `model.PlaceItem` or `model.TrasnitionItem`.'''
        self.renameModifications(self.diag.getName())             
        del self.diag        
    #-----------------------------------------------------------------------------------------------
    
    
    def deleteItemLocal(self):
        '''Capture delete event and call editor delete function.'''
        self.parent.deleteItem([self])   
    #------------------------------------------------------------------------------------------------
        
    
#     def itemChange(self, change, value):                    
#         if change == self.ItemScenePositionHasChanged:
#             rect = self.boundingRect()
#             pos = self.scenePos()
#             for cb in self.posCallbacks:                
#                 for connection in self.parent.visualConnectionList:
#                     if connection[0] is self or connection[2] is self:
#                         inputCoordinates = QtCore.QPointF(connection[0].x(), connection[0].y())
#                         outputCoordinates = QtCore.QPointF(connection[2].x(), connection[2].y())
#                         if connection[0] is self:                        
#                             value = self.determineBorder( connection[1], connection[2], rect, pos, inputCoordinates, outputCoordinates )  
#                         if connection[2] is self:
#                             value = self.determineBorder( connection[1], connection[0], rect, pos, outputCoordinates, inputCoordinates )     
#                 cb(value)
#             return value
#         return super(AbstractItem, self).itemChange(change, value)
#     #-----------------------------------------------------------------------------------------------
    
#========================================================================================================================
