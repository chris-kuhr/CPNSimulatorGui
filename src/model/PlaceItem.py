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


from model.AbstractItem import AbstractItem
from model.TokenItem import TokenItem
from model.PortItem import PortItem



class PlaceItem(QtGui.QGraphicsEllipseItem, AbstractItem):
    '''CPN Transition element.
    
        :member editor: `gui.DiagramEditor`. Editor to show in.
        :member name: Name of the CPN element assigned by the user. 
        :member subnet: Name of the subnet this transition is contained in.
        :member position: Position of this item in the `gui.DiagramScene`.
        :member port: `model.PortItem` if this is a port place, else None.
        :member portClone: A port place in the super net or None.   
        :member portDirection: Direction of the port, if this is a port place.
        :member uniqueName: Unique name of this transition used by the simulator.
        :member place: SNAKES place node with id `uniqueName`, except portClones. 
        :member initMarking: List of initial tokens present in this place.
        :member tokens: List ( deque ) of `model.TokenItem` s in this place.
        :member toolTipString: Information string containing the tokens present in this place.
    '''
    def __init__(self, editor, name, position, initMarking = [], uniqueName="p0", port=None, loadFromFile=False, portDirection=None, portClone=None, superNet=None, subnet=None):
        '''Create and initialize place item.
        
        :param editor: `gui.DiagramEditor`. Editor to show in.
        :param name: Name of the CPN element assigned by the user. 
        :param position: Position of this item in the `gui.DiagramScene`.
        :param initMarking: List of initial tokens present in this place.
        :param uniqueName: Unique name of this transition used by the simulator.
        :param port: `model.PortItem` if this is a port place, else None.
        :param loadFromFile: Flag determining, whether the place is loaded from file.
        :param portDirection: Direction of the port, if this is a port place.
        :param portClone: A port place in the super net or None.   
        :param superNe: The super net is used to determine the editor for port place clones.
        :param subnet: Name of the subnet this transition is contained in.
        '''
        super(PlaceItem, self).__init__(None)
        self.initMarking = initMarking
        self.uniqueName = uniqueName
        self.editor = editor
        self.port = port
        self.subnet = subnet
        self.superNet = superNet
        self.portClone = portClone 
        self.portDirection = portDirection
        self.toolTipString = ""
        self.tokens = deque()
        self.place = None
        self.setZValue(10)
        self.setPos(position)
        pos = self.scenePos()
        rect = self.boundingRect()    
        
        logging.debug("-------Create----Place-------------------%s---------%s----------"%(uniqueName, name))
        logging.debug( "editor %s position %s initMarking %s"%(editor, position, initMarking))
        logging.debug( "port %s loadFromFile %s portDirection %s portClone %s superNet %s subnet %s"%(port, loadFromFile, portDirection, portClone, superNet, subnet))
        logging.debug("-----------------------------------------------------------------------------------")
        
        w , h = self.createItem(editor, name, nodeType="place")
        
        if self.port is None:
            for token in self.initMarking:
                self.tokens.append( TokenItem( self.editor, token, 1, QtCore.QRectF( pos.x() + rect.width(), pos.y(), 10.0, 10.0),  parent=self) )
                self.editor.diagramScene.addItem(self.tokens[-1])
                self.editor.mainWindow.simulator.defineNewColour( token )  
            
            if not loadFromFile:
                self.place = Place( self.uniqueName , self.initMarking )
                self.editor.mainWindow.simulator.net.add_place( self.place )                 
                self.editor.mainWindow.simulator.places.append(self)
                     
            if self.subnet is not None and str( self.subnet ) != str("None") and self.portDirection is not None and str( self.portDirection ) != str("None"):
                if "i" in self.portDirection or "o" in self.portDirection:
                    self.port = PortItem(self.portDirection, self)
                    self.port.setDirection(self.portDirection)
                    self.portDirection = self.portDirection
                    rect = self.label.boundingRect() 
                    self.port.setPos( rect.width() + 20.0, rect.height() + 20.0 )
                    self.setPort( loadFromFile )
        else:            
            self.subnet = self.editor.subnet
            self.port = PortItem(self.portDirection, self)
            self.port.setDirection(self.portDirection)
            self.portDirection = self.portDirection
            rect = self.label.boundingRect() 
            self.port.setPos( rect.width() + 20.0, rect.height() + 20.0 )
                
        self.editor.visualPlaces.append(self)
        self.editor.diagramScene.addItem(self) 
        
#         logging.debug("place %s %s %s %s %s"%( self.uniqueName, self.port, self.portDirection, self.portClone, self.place ) )
 
    #------------------------------------------------------------------------------------------------    
    
    
    def setPortDiag(self):
        '''Callback function to modify the port.'''
        self.portDiag = NameDialog(title="Enter Direction", default="io" )
        self.portDiag.accepted.connect(self.setPort)
        self.portDiag.show()
    #-----------------------------------------------------------------------------------------------
    
    
    def setPort(self, loadFromFile=False):
        '''Create a new `model.PortItem` or edit the existing port.
        
        :param loadFromFile: Flag determining, whether the place is loaded from file.
        '''
        if self.port is None and not loadFromFile:
            self.port = PortItem(self.portDirection, self)
            rect = self.label.boundingRect() 
            self.port.setPos( rect.width() + 20.0, rect.height() + 20.0 )
            direction = self.portDiag.getName()
            self.port.setDirection( direction ) 
            self.portDirection = direction
            del self.portDiag    
            
        srcConnector = 0
        dstConnector = 0
        
        for editor in self.editor.mainWindow.editors:
            for transition in editor.visualTransitions:
                if str( self.subnet ) == str( transition.name ) and transition.substitutionTransition:
                    pos = transition.scenePos()
                    rect = transition.boundingRect()
                    if not isinstance(self.portClone, str) and self.portClone is not None:
                        editor.diagramScene.removeItem( self.portClone )
                    if str("i") == str( self.port.getDirection() ): 
                        self.portClone = PlaceItem( editor, self.name, QtCore.QPointF( pos.x() , pos.y() -100 )  , initMarking = self.initMarking, uniqueName=self.uniqueName, port=self.port, portDirection=self.portDirection )
                        srcConnector = 13
                        dstConnector = 2
                    elif str("o")  == str( self.port.getDirection() ):
                        self.portClone = PlaceItem( editor, self.name, QtCore.QPointF( pos.x() , pos.y() +100 )  , initMarking = self.initMarking, uniqueName=self.uniqueName, port=self.port, portDirection=self.portDirection )
                        srcConnector = 2
                        dstConnector = 13
                    elif str("io")  == str( self.port.getDirection() ):
                        self.portClone = PlaceItem( editor, self.name, QtCore.QPointF( pos.x() - 100 , pos.y() )  , initMarking = self.initMarking, uniqueName=self.uniqueName, port=self.port, portDirection=self.portDirection )
                        srcConnector = 7
                        dstConnector = 18
                    else:
                        break
                    self.portDirection = str( self.port.getDirection() )
                    editor.setPortConnection(self.portClone.connectorList[srcConnector], transition.connectorList[dstConnector])
                    if self.portClone is not None:
                        editor.diagramScene.addItem( self.portClone )
                        
    #------------------------------------------------------------------------------------------------
    
        
    def addToken(self):      
        '''Method to add a `model.TokenItem` to this place'''
        self.tokenDiag = TokenDialog(self.editor)
        self.tokenDiag.accepted.connect(self.newTokenValue)
        self.tokenDiag.show()      
    #------------------------------------------------------------------------------------------------
    
    
    def newTokenValue(self):
        '''Accept new token.'''
        if self.portClone is None:
            pos = self.scenePos()
            rect = self.boundingRect()  
            self.tmpToken = None
            self.tokens.append( TokenItem( self.editor, self.tokenDiag.getListEntry(), self.tokenDiag.getCountToken(), QtCore.QRectF( pos.x() + rect.width(), pos.y() , 15.0, 15.0 ),  parent=self ) )
            if self.tokenDiag.getInitMarking():
                self.initMarking = self.tokens[-1].token
            self.place.add(self.tokens[-1].token)
            self.editor.mainWindow.simulator.tokenAdded()
            self.editor.diagramScene.addItem(self.tokens[-1])
    #------------------------------------------------------------------------------------------------
        
        
    def stackTokens(self):        
        '''Method to order the visual stacking of different tokens.'''
        self.toolTipString = ""        
        self.setToolTip( self.toolTipString )
        self.descCanvas.setCanvasString( self.toolTipString )
        
        pos = self.scenePos()
        rect = self.boundingRect()
        lenTok = len( self.tokens )
        tokens = list( self.tokens )
        for idx in range(0, lenTok):
            token = tokens.pop()
            self.toolTipString += "%s' %s ++\n" %(token.countTokenLabel.toPlainText(), token.token)
            token.setPos( QtCore.QPointF( rect.x()  + (lenTok - idx)*10 , rect.y() - (lenTok - idx)*10 ) )
            self.setToolTip( self.toolTipString )
            self.editor.diagramScene.removeItem( self.descCanvas )
            self.descCanvas.setCanvasString( self.toolTipString )
            self.editor.diagramScene.addItem( self.descCanvas )
    #------------------------------------------------------------------------------------------------
    
    
    def mousePressEvent(self, event):        
        '''Prevents the movement of this item, when connections are drawn.
        
        :param event: `QtGui.mousePressEvent`
        '''
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            self.editor.startArc(self)
        QtGui.QGraphicsEllipseItem.mousePressEvent(self, event)
    #------------------------------------------------------------------------------------------------
        
        
    def mouseMoveEvent(self, event):
        '''Prevents the movement of this item, when connections are drawn.
        
        :param event: `QtGui.mouseMoveEvent`
        '''
        if not event.modifiers() & QtCore.Qt.ShiftModifier:    
            for token in self.tokens:
                QtGui.QGraphicsEllipseItem.mouseMoveEvent(token, event)                
            self.stackTokens()
            QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, event)  
    #------------------------------------------------------------------------------------------------
    
    
    def mouseReleaseEvent(self, event):
        '''Forward `QtGui.mouseReleaseEvent`.
        
        :param event: `QtGui.mouseReleaseEvent`
        '''
        self.stackTokens()
        QtGui.QGraphicsEllipseItem.mouseReleaseEvent(self, event)
    #------------------------------------------------------------------------------------------------
        
    def renameModifications(self, name):
        '''Make neccessary modification and renaming.
        
        :param name: Name of the CPN element assigned by the user. 
        '''
        if self.port is not None:
            for editor in self.editor.mainWindow.editors:
                for place in editor.visualPlaces:
                    if str( place.uniqueName ) == str( self.uniqueName ):                
                        place.name = name
                        place.label.setPlainText(name)       
        self.name = name        
        self.label.setPlainText(self.name)
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
        self.contextMenuPortSet = menu.addAction('Set Port')
        self.contextMenuPortSet.triggered.connect(self.setPortDiag)
        self.delete = menu.addAction('Delete')
        self.delete.triggered.connect(self.deleteItemLocal)
        menu.exec_(event.screenPos())
    #------------------------------------------------------------------------------------------------

#========================================================================================================================

