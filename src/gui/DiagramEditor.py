from PyQt4 import QtGui, QtCore, QtSvg, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import logging

import snakes.plugins
from snakes.nets import *

from collections import Counter, deque


from model import *
from model.AbstractItem import Connector
from model.PlaceItem import PlaceItem
from model.TransitionItem import TransitionItem
from model.TokenItem import TokenItem
from model.PortItem import PortItem
from model.ArcItem import ArcItem, LineItem

from gui.DiagramScene import DiagramScene
from gui.NameDialog import NameDialog
from gui.LibraryModel import LibraryModel

from inout.XMLIO import XMLIO


class EditorGraphicsView(QtGui.QGraphicsView):
    '''Viewport for the `gui.DiagramScene` s.
    
    It controls the zooming feature and drag and drop operations from the item library.
    
    :member parent: Parent editor widget.   
    :member scaleFactor: Zooming factor.
    '''
    def __init__(self, parent=None):        
        '''Create the Viewport.
        
        :param parent: Parent editor widget.
        '''
        QtGui.QGraphicsView.__init__(self, parent.diagramScene, parent)
        self.parent = parent
        self.scaleFactor = 1.0
    #------------------------------------------------------------------------------------------------
            
    def dragEnterEvent(self, event):
        '''Callback method, when an icon is dragged from the `libraryModelView` to `gui.diagramScene`.
        
        :param event: `QtGui.dragEnterEvent`.
        '''
        if event.mimeData().hasFormat('component/name'):
            self.nodeType = event.mimeData().data('component/name').toLower()
            event.accept()
    #------------------------------------------------------------------------------------------------
            
    def dragMoveEvent(self, event):
        '''Callback method, when an icon is moved over the `gui.diagramScene`.
        
        :param event: `QtGui.dragMoveEvent`.
        '''
        if event.mimeData().hasFormat('component/name'):
            event.accept()
    #------------------------------------------------------------------------------------------------
            
    def dropEvent(self, event):
        '''Callback method, when an icon is dropped on the `gui.diagramScene`.
        
        :param event: `QtGui.dropEvent`.
        '''
        if event.mimeData().hasFormat('component/name'):
            self.eventPosition = event.pos() 
            if "token" in self.nodeType:     
                self.validDrop()
            elif "transition" in self.nodeType:
                self.diag = NameDialog(parent=self, item="transition", title="Enter %s Name" % (self.nodeType[0].upper()+self.nodeType[1:]) , default="")
                self.diag.accepted.connect(self.validDrop)
                self.diag.show()
            elif "place" in self.nodeType:        
                self.diag = NameDialog(parent=self, item="place", title="Enter %s Name" % (self.nodeType[0].upper()+self.nodeType[1:]) , default="")
                self.diag.accepted.connect(self.validDrop)
                self.diag.show()    
            else:
                errorString = str( "no valid target, dropping aborted" )
                item = QtGui.QListWidgetItem( errorString )
                item.setTextColor(QtCore.Qt.yellow)
                self.logWidget.addItem( item )
                logging.warning(errorString)
                del self.diag
                del self.eventPosition
                del self.nodeType
                return
    #------------------------------------------------------------------------------------------------
    
    
    def wheelEvent(self, event):
        '''Callback method, when the mouse wheel is used.
        
        :param event: `QtGui.wheelEvent`.
        '''
        factor = 0.25
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            if event.delta() > 0:
                self.scaleFactor += factor
                self.parent.mainWindow.lineEdit_2.setText("{:3.0f}%".format(self.scaleFactor*100))    
                self.scale( 1/(1-factor), 1/(1-factor) )         
            else:
                if self.scaleFactor > factor:
                    self.scaleFactor -= factor
                    self.parent.mainWindow.lineEdit_2.setText("{:3.0f}%".format(self.scaleFactor*100))    
                    self.scale( (1-factor), (1-factor) )                     
                
            self.centerOn( event.pos() )        
            
        QtGui.QGraphicsView.wheelEvent( self, event )
    
    #------------------------------------------------------------------------------------------------
    
    def validDrop(self):       
        '''Callback method, when the drop on `gui.DiagramScene` was valid.'''
        if "token" in self.nodeType:     
            for item in self.items( self.eventPosition ):
                if isinstance(item, PlaceItem):
                    item.addToken()
        elif "transition" in self.nodeType:   
            if self.diag.checkBox.checkState() == 2:
                subnet = self.diag.getName()
                substitutionTransition = True
            else:
                subnet = self.parent.subnet
                substitutionTransition = False
            self.parent.mainWindow.simulator.uniqueNameBase += 1
#             b1 = TransitionItem( self.parent, self.diag.getName(),self.mapToScene( self.eventPosition ), guardExpression = "True", substitutionTransition=substitutionTransition, uniqueName="t%d"%self.parent.mainWindow.simulator.uniqueNameBase)
            b1 = TransitionItem( self.parent, self.diag.getName(),self.mapToScene( self.eventPosition ), guardExpression = "True", substitutionTransition=substitutionTransition, uniqueName="t%d"%self.parent.mainWindow.simulator.uniqueNameBase, subnet=subnet)
            
            self.parent.diagramScene.addItem(b1) 
        elif "place" in self.nodeType:  
            self.parent.mainWindow.simulator.uniqueNameBase += 1
#             b1 = PlaceItem( self.parent, self.diag.getName(),self.mapToScene( self.eventPosition ), initMarking = [], uniqueName="p%d"%self.parent.mainWindow.simulator.uniqueNameBase)
            b1 = PlaceItem( self.parent, self.diag.getName(),self.mapToScene( self.eventPosition ), initMarking = [], uniqueName="p%d"%self.parent.mainWindow.simulator.uniqueNameBase, subnet=self.parent.subnet)
            self.parent.diagramScene.addItem(b1) 
#         for place in self.parent.visualPlaces:
#             place.findItemsInPlanes() 
#         for transition in self.parent.visualTransitions:
#             transition.findItemsInPlanes()
        del self.eventPosition
        del self.nodeType
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================
    

class DiagramEditor(QtGui.QWidget):
    '''Editor widget, containing the `libraryModelView`, the `colorSetListView` and the `gui.DiagramScene`.
    
    :member mainWindow: `gui.MainWindow`. Main application window.  
    :member parent: Parent widget.
    :member workingDir: Working directory.      
    :member subnet: Name of visualized subnet, also window title.
    :member colorListItems: Defined colors.
    :member libItems: Visual library items, CPN elements.
    :member portConnections: List of connections between portClone port places and substitution transitions.
    :member visualPlaces: List of all `model.PlaceItem`s shown in this `gui.DiagramScene`.
    :member visualTransitions: List of all `model.TransitionItem`s shown in this `gui.DiagramScene`.
    :member visualConnectionList: List of all `model.ArcItem`s shown in this `gui.DiagramScene`.
    :member libraryModel: Library model for visual CPN elements. 
    :member mouseScreenPos: Recorded mouse position.
    :member diagramScene: Contained `gui.DiagramScene`.
    :member diagramView: `gui.DiagramView` controlling `gui.DiagramScene`.
    :member startedArc: Status, determining whether the creation of a connection has started.
    :member showCanvasInfos: Status variable for activation of the tooltip `model.AbstractItem.DescriptionCanvas` s. 
    '''
    def __init__(self, mainWindow=None, parent=None, workingDir="", subnet=None):
        '''Create editor widget.
        
        :param mainWindow: `gui.MainWindow`. Main application window.  
        :param parent=None:
        :param workingDir: Working directory.      
        :param subnet: Name of visualized subnet, also window title.
        '''
        QtGui.QWidget.__init__(self, parent)
        
        self.mainWindow = mainWindow         
        self.parent = parent
        self.workingDir = workingDir        
        self.subnet = subnet
        self.portConnections = []
        self.visualPlaces = []
        self.visualTransitions = []
        self.visualConnectionList = []
            
        self.mouseScreenPos = None       
                
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.verticalLayout = QtGui.QVBoxLayout()
        
        self.libraryBrowserView = QtGui.QListView(self)
        self.libraryBrowserView.setMinimumSize(QtCore.QSize(250, 75))
        self.libraryBrowserView.setMaximumSize(QtCore.QSize(250, 75))
        self.libraryModel = LibraryModel(self)
        self.libraryModel.setColumnCount(1)
                
        self.libItems = []
        self.libItems.append( self.createIcon("transition") )
        self.libItems.append( self.createIcon("place") )
        self.libItems.append( self.createIcon("token") )
        
        for i in self.libItems:
            self.libraryModel.appendRow(i)
        self.libraryBrowserView.setModel(self.libraryModel)
        self.libraryBrowserView.setViewMode(self.libraryBrowserView.IconMode)
        self.libraryBrowserView.setDragDropMode(self.libraryBrowserView.DragOnly)
        
        self.nodeLabel = QtGui.QLabel("Nodes and Tokens")
        self.verticalLayout.addWidget(self.nodeLabel)
        self.verticalLayout.addWidget(self.libraryBrowserView)

        self.colorListWidget = QtGui.QListWidget(self)
        self.colorListWidget.setMinimumSize(QtCore.QSize(250, 250))
        self.colorListWidget.setMaximumSize(QtCore.QSize(250, 875))
                
        self.colorListItems = []
        self.colorListItems.append( "add Color" )        
        
        for token in self.colorListItems:
            self.colorListWidget.addItem( QtGui.QListWidgetItem( token ) )
        self.colorListWidget.setDragDropMode(self.colorListWidget.DragOnly)

        self.colorListWidget.itemDoubleClicked.connect( self.newToken )
        
        self.colorLabel = QtGui.QLabel("Colors")
        self.verticalLayout.addWidget(self.colorLabel)
        self.verticalLayout.addWidget(self.colorListWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        
        self.diagramScene = None
        
        
        self.diagramScene = DiagramScene(self)
        self.diagramView = EditorGraphicsView(self)
        self.diagramView.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOn )
        self.diagramView.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOn )
        self.diagramView.setMouseTracking(True)
        
        self.horizontalLayout.addWidget(self.diagramView)
        
        gridV2 = QtGui.QGraphicsRectItem(0, 0, 10, 10)
        self.diagramScene.addItem(gridV2)
        
        self.startedArc = None
        self.tmpArc = None
        self.validArc = None
        self.showCanvasInfos = False
    #------------------------------------------------------------------------------------------------
    
    
    def setTokenForPlace(self, place, actualMarking):
        '''Show the tokens contained in place.
        
        :param place: `model.PlaceItem` to show the `model.TokenItem` for.
        :param actualMarking: SNAKES Marking to determine the tokens for `place`.
        '''
#         logging.debug( "%s %s"%( str( self.subnet ) , str( place.subnet ) ) )
#         for vPlace in self.visualPlaces:
#             if place == vPlace:    
#                 for tok in place.tokens:             
#                     self.diagramScene.removeItem( tok ) 
#                     break       

        for tok in place.tokens:             
            self.diagramScene.removeItem( tok ) 
            break               
            
        place.tokens = deque()
        pos = place.scenePos()
        rect = place.boundingRect()
        for token in actualMarking( place.uniqueName ):
            if token is not None:
                place.tokens.append( TokenItem( self, token, 1, QtCore.QRectF( pos.x() + rect.width(), pos.y(), 15.0, 15.0)  ) )
                self.diagramScene.addItem(place.tokens[-1])
            else:
                try:
                    place.place.remove(token)
                except ValueError:
                    pass
                except AttributeError:
                    pass
            
#             vPlace.tokens = deque()
#             pos = vPlace.scenePos()
#             rect = vPlace.boundingRect()
#             for token in actualMarking( vPlace.uniqueName ):
#                 if not "None" in str( token ):
#                     vPlace.tokens.append( TokenItem( self, token, 1, QtCore.QRectF( pos.x() + rect.width(), pos.y(), 15.0, 15.0)  ) )
#                     self.diagramScene.addItem(vPlace.tokens[-1])


    #------------------------------------------------------------------------------------------------
    
    def setPortConnection(self, portPlaceClone, transition):        
        '''Set a connection between a port place clone and a substitution transition.
        
        :param portPlaceClone: Port place clone `model.PlaceItem`. 
        :param transition: Substitutaion transition `model.TransitionItem`.
        '''
        portConnection = ArcItem(self, portPlaceClone, transition, isPortConnection=True)
        portConnection.setEndPos(transition.scenePos())  
        portConnection.setDestination(transition)   
        self.diagramScene.addItem( portConnection )
        self.portConnections.append( portConnection )
    #------------------------------------------------------------------------------------------------
    
    def setTokens(self, actualMarking): 
        '''Set tokens for `actualMarking`.
        
        :param actualMarking: SNAKES Marking to determine the tokens for `place`.
        '''
        for place in self.visualPlaces:
            self.setTokenForPlace(place, actualMarking)
    #------------------------------------------------------------------------------------------------
    
    
    def keyPressEvent(self, event): 
        '''Callback method, when a key is pressed on the keyboard.
        
        :param event: `QtGui.keyPressEvent`.
        '''
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            if event.key() == QtCore.Qt.Key_T:      
                self.nodeType = "transition"
            elif event.key() == QtCore.Qt.Key_P:      
                self.nodeType = "place"
            elif event.key() == QtCore.Qt.Key_M:    
                if not self.showCanvasInfos:
                    self.showCanvasInfos = True
                else:
                    self.showCanvasInfos = False
                              
                for place in self.visualPlaces:
                    place.descCanvas.setVisibility( self.showCanvasInfos )

                for transition in self.visualTransitions:
                    transition.descCanvas.setVisibility( self.showCanvasInfos )

                return
            else:
                return
            self.diag = NameDialog(parent=self, item="transition", title="Enter %s Name" % (self.nodeType[0].upper()+self.nodeType[1:]) , default="")
                
#             self.diag = NameDialog(parent=self, title="Enter %s Name" % (self.nodeType[0].upper()+self.nodeType[1:]), default="unnamed")
            self.diag.accepted.connect(self.shortcutCreateNode)
            self.diag.show()
        elif event.key() == QtCore.Qt.Key_Delete: 
            self.deleteItems( self, self.diagramScene.selectedItems() )
            pass
    #------------------------------------------------------------------------------------------------
    
    
    def wheelEvent(self, event):
        '''Callback method, when the mouse wheel is used.
        
        :param event: `QtGui.wheelEvent`.
        '''
        QtGui.QWidget.wheelEvent(self, event)
    
    #------------------------------------------------------------------------------------------------
    
    def sceneMouseMoveEvent(self, event):
        '''Catch sceneMouseMoveEvent during arc creation.
        
        :param event: `QtGui.sceneMouseMoveEvent`.
        '''
        if self.startedArc:            
            self.startedArc.setEndPos(event.scenePos() )
        self.mouseScreenPos = event.screenPos()
    #------------------------------------------------------------------------------------------------
            
            
    def sceneMouseReleaseEvent(self, event):
        '''Catch `QtGui.sceneMouseReleaseEvent` on arc completion.
        
        :param event: `QtGui.sceneMouseReleaseEvent`.
        '''
        self.mouseScreenPos = event.screenPos()
        if self.startedArc:
            pos = event.scenePos()
            for item in  self.diagramScene.items( pos ):
                if type(item) is Connector:
                    if type(item.parent) is TransitionItem and type(self.startedArc.srcConnector.parent) is PlaceItem:
                        self.startedArc.setDestination(item)                                        
                        self.startedArc.dstConnector.connectionArc = self.startedArc
                        self.tmpArc = self.startedArc                    
                        self.diag = NameDialog(parent=self, item=item, title="Enter Variable for Input Arc", default="a")
                        self.diag.accepted.connect(self.validConnection)
                        self.diag.show()
                        
                    elif type(item.parent) is PlaceItem and type(self.startedArc.srcConnector.parent) is TransitionItem:
                        self.startedArc.setDestination(item)                                     
                        self.startedArc.dstConnector.connectionArc = self.startedArc
                        self.tmpArc = self.startedArc                    
                        self.diag = NameDialog(parent=self, item=item, title="Enter Variable or Expression for Output Arc", default="a")
                        self.diag.accepted.connect(self.validConnection)
                        self.diag.show()
                            
            if self.startedArc.dstConnector == None:
                self.startedArc.delete()
            
            self.startedArc = None
    #------------------------------------------------------------------------------------------------
    
    
    def createIcon(self, nodeType):
        '''Create Icons for `libraryModel`.
        
        :param nodeType: Type of icon to create.
        '''
        pixmap = QtGui.QPixmap(60, 60)
        pixmap.fill()
        painter = QtGui.QPainter(pixmap)
        if nodeType == "transition":
            painter.setBrush(QtCore.Qt.white)
            painter.drawRect(5, 10, 50, 30)
        elif nodeType == "place":           
            painter.setBrush(QtCore.Qt.white)
            painter.drawEllipse(5, 10, 50, 30) 
        elif nodeType == "token":           
            painter.setBrush(QtCore.Qt.green)
            painter.drawEllipse(15, 15, 30, 30) 

        painter.end()
        return QtGui.QStandardItem( QtGui.QIcon(pixmap), nodeType[0].upper() + nodeType[1:] )
    #------------------------------------------------------------------------------------------------
        
        
    def newToken(self, item):
        '''Callback method, when `add Token` is clicked in `colorListView`.
        
        :param item: `colorListView` item.
        '''
        if item is self.colorListWidget.item( self.colorListWidget.count()-1 ) :
            self.diag = NameDialog(title="Token", default="")
            self.diag.accepted.connect(self.defineNewToken)
            self.diag.show()  
    #------------------------------------------------------------------------------------------------
        
        
    def defineNewToken(self):
        '''Define a new color set.'''
        self.mainWindow.simulator.defineNewColour( self.diag.getName() )            
    #-------------------------------------------------------------------------------------------------
        
    
    def shortcutCreateNode(self):
        '''Create CPN elements with keyboard shortcuts.'''
        if "transition" in self.nodeType:
            if self.diag.checkBox.checkState() == 2:
                subnet = self.diag.getName()
                substitutionTransition = True
            else:
                subnet = self.subnet
                substitutionTransition = False
            self.mainWindow.simulator.uniqueNameBase += 1
            
            b1 = TransitionItem( self, self.diag.getName(),QtCore.QPointF(), guardExpression = "True", substitutionTransition=substitutionTransition, uniqueName="t%d"%self.mainWindow.simulator.uniqueNameBase, subnet=subnet)

#             b1 = TransitionItem( self, self.diag.getName(), self.mouseScreenPos, net=self.mainWindow.simulator.net, guardExpression = "True", uniqueName="t%d"%self.mainWindow.simulator.uniqueNameBase)
            self.mainWindow.simulator.uniqueNameBase += 1
        elif "place" in self.nodeType:            
            b1 = PlaceItem( self, self.diag.getName(), self.mouseScreenPos, initMarking = [], uniqueName="p%d"%self.mainWindow.simulator.uniqueNameBase, subnet=self.subnet)
            self.mainWindow.simulator.uniqueNameBase += 1
        else:
            errorString = str( "no valid target, dropping aborted" )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.yellow)
            self.logWidget.addItem( item ) 
            logging.warning(errorString)
            return
        self.diagramScene.addItem(b1) 
        del self.diag
        del self.nodeType
        pass
    #------------------------------------------------------------------------------------------------
        
    def deleteSubnet(self, editor):
        '''Recursivly delete subnet editor and their content.
        
        :param editor: Root `gui.DiagramEditor` for deletion. 
        '''
        self.deleteItems( editor, editor.visualTransitions + editor.visualPlaces )
        for connection in list( editor.visualConnectionList ):
            if connection in self.mainWindow.simulator.connectionList:
                self.mainWindow.simulator.connectionList.remove( connection )  
            editor.diagramScene.removeItem( connection[1].label )
            editor.diagramScene.removeItem( connection[1].arcLine )
            editor.diagramScene.removeItem( connection[1].arrowPolygonObject )
            editor.diagramScene.removeItem( connection[1] )
            editor.visualConnectionList.remove( connection ) 
        
        self.mainWindow.editors.remove(editor) 
    #------------------------------------------------------------------------------------------------    
        
    def deleteTransition(self, editor, transition):
        '''Delete transitions, substitution transitions and their subnets.
        
        :param editor: `gui.DiagramEditor` containing the `transition`. 
        :param transition: `model.TransitionItem` for deletion.
        '''
        if not transition.substitutionTransition:
            tmpList = list(editor.visualConnectionList)
            for connection in tmpList:  
                for srcConnect in transition.connectorList:
                    if connection[0] == srcConnect:
                        self.deleteArc( editor, connection )
                for dstConnect in transition.connectorList:
                    if connection[2] == dstConnect:
                        self.deleteArc( editor, connection )
                         
            self.mainWindow.simulator.net.remove_transition( transition.uniqueName )
            self.mainWindow.simulator.transitions.remove( transition ) 
            editor.visualTransitions.remove(transition)
        else:                            
            for editor2 in list( self.mainWindow.editors ):
                if str( editor2.subnet ) == str( transition.name ):
                    self.deleteSubnet( editor2 )  
            editor.visualTransitions.remove(transition)        
        editor.diagramScene.removeItem( transition ) 
        del transition        
        
    #------------------------------------------------------------------------------------------------
    
    def deletePlace(self, editor, place, portClone=False):
        '''Delete places, port places and port clone places.
        
        :param editor: `gui.DiagramEditor` containing the `place`. 
        :param place: `model.PlaceItem` for deletion.
        :param portClone: Flag determining whether a port clone place shall be deleted.
        '''
        tmpList = list(editor.visualConnectionList)
        for connection in tmpList:  
            for srcConnect in place.connectorList:
                if connection[0] == srcConnect:
                    self.deleteArc( editor, connection )
            for dstConnect in place.connectorList:
                if connection[2] == dstConnect:
                    self.deleteArc( editor, connection )
        
        if portClone:   
            for token in place.tokens:
                editor.diagramScene.removeItem( token )
                break
            editor.visualPlaces.remove( place )      
            
            
            editor.diagramScene.removeItem( place )   
            
        else:
            if place.port is None and place.portClone is None:
                for token in place.tokens:
                    editor.diagramScene.removeItem( token )
                    break
                
                self.mainWindow.simulator.net.remove_place( place.uniqueName )   
                self.mainWindow.simulator.places.remove( place )
                editor.visualPlaces.remove( place )      
                editor.diagramScene.removeItem( place )   
            else:
                if place.portClone is not None:
                    for editor2 in self.mainWindow.editors:
                        if isinstance( place.portClone, PlaceItem ):
                            if str( editor2.subnet ) == str( place.portClone.editor.subnet ):
                                self.deletePlace( editor2, place.portClone, portClone=True ) 
                                for connection in editor2.portConnections:
                                    if connection.srcConnector.parent == place.portClone:
                                        editor.diagramScene.removeItem( connection.label )
                                        editor.diagramScene.removeItem( connection.arcLine )
                                        editor.diagramScene.removeItem( connection.arrowPolygonObject )                                    
                                        editor.diagramScene.removeItem( connection )  
                                        editor2.portConnections.remove( connection )
                        if isinstance( place.portClone, str ):
                            for editor3 in self.mainWindow.editors[1:]:
                                for place2 in editor3.visualPlaces:
                                    if str( place2.uniqueName ) ==  str( place.portClone ):
                                        if str( editor2.subnet ) == str( place2.uniqueName ):
                                            self.deletePlace( editor2, place2 , portClone=True ) 
                                            for connection in editor2.portConnections:
                                                if connection.srcConnector.parent == place2:
                                                    editor.diagramScene.removeItem( connection.label )
                                                    editor.diagramScene.removeItem( connection.arcLine )
                                                    editor.diagramScene.removeItem( connection.arrowPolygonObject )                                    
                                                    editor.diagramScene.removeItem( connection )  
                                                    editor2.portConnections.remove( connection )
    
                        for portOrigin in editor2.visualPlaces:
                            if str( place.uniqueName ) == str( portOrigin.uniqueName ):
                                portOrigin.portClone = None
                                           
                    for token in place.tokens:
                        editor.diagramScene.removeItem( token )
                        break
                    self.mainWindow.simulator.net.remove_place( place.uniqueName ) 
                    self.mainWindow.simulator.places.remove( place )
                    
                    editor.visualPlaces.remove( place )      
                    editor.diagramScene.removeItem( place )
                                                 
        del place
        
    #------------------------------------------------------------------------------------------------
        
        
    def deleteToken(self, editor, token):
        '''Delete a token.
        
        :param editor: `gui.DiagramEditor` containing the `place`. 
        :param token: `model.TokenItem` for deletion.
        '''
        for place in editor.visualPlaces:
            newDeque = deque()
            for tok in place.tokens:
                if token == tok:
                    if place.place is not None:
                        self.mainWindow.simulator.net.place( place.uniqueName ).remove( token.token )
#                     place.tokens.remove( token )
                    self.mainWindow.simulator.getActualMarking( self.mainWindow.simulator.net.get_marking() )
                else:
                    newDeque.append(token)
            place.tokens = newDeque    
        
    #------------------------------------------------------------------------------------------------
        
        
    def deleteItems(self, editor, items):  
        '''Delete items.
        
        :param editor: `gui.DiagramEditor` containing the `items`. 
        :param items: List with items (selection) to delete.
        '''
        for item in items:
            if isinstance( item, TokenItem ):
                self.deleteToken( editor, item )  
                
            if isinstance( item, TransitionItem ):
                self.deleteTransition( editor, item )  
                    
            elif isinstance( item, PlaceItem ): 
                self.deletePlace( editor, item )
                
            elif type(item) is LineItem:   
                tmpList = list(self.visualConnectionList)
                for connection in tmpList:  
                    if connection[1] == item.parent:
                        self.deleteArc( editor, connection )                
    #------------------------------------------------------------------------------------------------
    
    
    def deleteArc(self, editor, connection):
        '''Delete arc.
        
        :param editor: `gui.DiagramEditor` containing the `connection`. 
        :param connection: `model.ArcItem` for deletion.
        '''
        for c in self.mainWindow.simulator.connectionList:
            if c == connection:
                self.mainWindow.simulator.connectionList.remove( connection )  
        editor.visualConnectionList.remove( connection )  
        
        editor.diagramScene.removeItem( connection[1].label )
        editor.diagramScene.removeItem( connection[1].arcLine )
        editor.diagramScene.removeItem( connection[1].arrowPolygonObject )

        try:
            if isinstance( connection[2].parent, TransitionItem ):
                self.mainWindow.simulator.net.remove_input( connection[0].parent.uniqueName , connection[2].parent.uniqueName )
            elif isinstance( connection[2].parent, PlaceItem ):     
                self.mainWindow.simulator.net.remove_output( connection[2].parent.uniqueName , connection[0].parent.uniqueName )
            editor.diagramScene.removeItem( connection[1] )
             
        except snakes.ConstraintError:
            errorString = str( "Constraint Error: %s"%(sys.exc_info()[1] ))
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.mainWindow.logWidget.addItem( item ) 
            logging.warning(errorString)
        except snakes.NodeError:
            errorString = str( "Node Error: %s"%(sys.exc_info()[1] ))
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.mainWindow.logWidget.addItem( item ) 
            logging.warning(errorString)
        
    #------------------------------------------------------------------------------------------------
    
    
    def startArc(self, nodeItem):
        '''Start an arc conneciton.
        
        :param nodeItem: `model.AbstractItem` source element.
        '''
        self.startedArc = ArcItem(self, nodeItem, None)
    #------------------------------------------------------------------------------------------------
    
    
    def validConnection(self):
        '''Callback method, when a valid arc connection was created.'''
        if type(self.diag.getItem().parent) is TransitionItem:          
            if self.tmpArc.setArcAnnotation( annotationText=self.diag.getName() )    :   
                self.tmpArc.setName( self.diag.getName() )  
            else:
                self.diagramScene.removeItem(self.tmpArc)
                del self.tmpArc
        elif type(self.diag.getItem().parent) is PlaceItem:       
            if self.tmpArc.setArcAnnotation( annotationText=self.diag.getName() ):       
                self.tmpArc.setName( self.diag.getName() ) 
            else:
                self.diagramScene.removeItem(self.tmpArc)
                del self.tmpArc    
            
        del self.diag
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================
