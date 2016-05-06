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

class TransitionItem(QtGui.QGraphicsRectItem, AbstractItem):
    '''CPN Transition element.
    
        :member editor: `gui.DiagramEditor`. Editor to show in.
        :member name: Name of the CPN element assigned by the user.
        :member substitutionTransition: Flag indication a substitutaion transition. 
        :member uniqueName: Unique name of this transition used by the simulator.
        :member transition: SNAKES transition node with id `uniqueName`, only if `substitutionTransition` is `False` else None.
        :member subnet: Name of the subnet this transition is contained in.
        :member position: Position of this item in the `gui.DiagramScene`.
        :member enabled: Flag determining if this transition is enabled.
        :member guardExpression: The guard expression for this transition.
        :member subnetBorder: Second border indicating a substitution transition. 
        :member exceptionString: Exception string containing simulator errors.
        :member modeString: Mode string containing the enabled modes for this transition
    '''
    def __init__(self, editor, name, position, guardExpression = None, uniqueName="t0", loadFromFile=False, substitutionTransition=False, subnet=None):
        '''Create transition item.
        
        :param editor: `gui.DiagramEditor`. Editor to show in.
        :param name: Name of the CPN element assigned by the user. 
        :param position: Position of this item in the `gui.DiagramScene`.
        :param guardExpression: The guard expression for this transition.
        :param uniqueName: Unique name of this transition used by the simulator.
        :param loadFromFile: Flag determining, whether the transition is loaded from file.
        :param substitutionTransition: Flag indication a substitutaion transition.
        :param subnet: Name of the subnet this transition is contained in.
        '''
        super(TransitionItem, self).__init__(None)
        self.editor = editor
        self.name = name
        self.substitutionTransition = substitutionTransition
        self.subnet = subnet
#         self.superNet = editor.subnet
        self.position = position
        self.uniqueName = uniqueName
        self.enabled = False
        self.guardExpression = guardExpression
        self.subnetBorder = None
        self.exceptionString = ""
        self.modeString = ""
        self.setBrush(QtGui.QBrush(QtCore.Qt.white))
        
        logging.debug("-------Create----Transition-------------------%s---------%s----------"%(uniqueName, name))
        logging.debug( "editor %s position %s Guard Expression %s"%(editor, position, guardExpression))
        logging.debug( "loadFromFile %s substitution Transition %s subnet %s"%(loadFromFile, substitutionTransition, subnet))
        logging.debug("-----------------------------------------------------------------------------------")
        
        if not self.substitutionTransition:
            if not loadFromFile:
                self.guardDiag = NameDialog(title="Enter Guard Expression", default="True")
                self.guardDiag.accepted.connect( self.acceptEditGuard )
                self.guardDiag.show()    
                try:
                    self.transition = Transition( self.uniqueName, Expression(self.guardExpression) )
                    self.editor.mainWindow.simulator.net.add_transition( self.transition ) 
                    self.editor.mainWindow.simulator.transitions.append( self )
                except SyntaxError:
                    item = QtGui.QListWidgetItem( str( sys.exc_info()[1] ) )
                    item.setTextColor(QtCore.Qt.red)
                    self.editor.mainWindow.logWidget.addItem( item )
        self.initTransition(loadFromFile)
    #-------------------------------------------------------------------------------------------------
    
    
    
    
    def initTransition(self, loadFromFile):  
        '''Initialize transition.
        
        :param loadFromFile: Flag determining, whether the transition is loaded from file.
        '''
        pos = self.scenePos()        
        self.createItem(self.editor, self.name, nodeType="transition")   
        rect = self.boundingRect()    
        
        if not self.substitutionTransition:    
            self.guardLabel = QtGui.QGraphicsTextItem(self.guardExpression, self)
            self.guardLabel.setFlags( self.ItemIsSelectable | self.ItemIsMovable )   
            self.guardLabel.setPos(pos.x() + rect.width()/2, pos.y() - 20)
            self.guardLabel.setPlainText( self.guardExpression )
        else:            
            if not loadFromFile:
                self.editor.mainWindow.addSubnetEditor(self.name)
            self.subnetBorder = QtGui.QGraphicsRectItem( pos.x() - 5, pos.y()-5, rect.width()+9, rect.height()+9, parent=self )
            self.subnetBorder.setFlag( self.ItemStacksBehindParent, True ) 
            self.subnetBorder.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            self.subnetBorder.setBrush(QtGui.QBrush(QtCore.Qt.white))
            self.subnetBorder.setZValue(11)
            self.guardExpression = ""
                
        self.setPos(self.position)
        self.setZValue(10)
        
        self.editor.visualTransitions.append(self)
        self.editor.diagramScene.addItem(self)
    #------------------------------------------------------------------------------------------------
     
        
    def editGuard(self):       
        '''Callback function to modify the guard expression.'''
        if not self.substitutionTransition:
            self.guardDiag = NameDialog(title="Enter Guard Expression", default=self.guardExpression)
            self.guardDiag.accepted.connect(self.acceptEditGuard)
            self.guardDiag.show()  
            
    #------------------------------------------------------------------------------------------------
    
    
    def setInfoString(self, stringInfo): 
        '''Set the string for the `gui.AbstractItem.DescritionCanvas`
        
        :param stringInfo: String appended to the first line of its `gui.AbstractItem.DescritionCanvas`.
        '''
        self.toolTipString = stringInfo
        self.setToolTip( self.toolTipString )
        self.editor.diagramScene.removeItem( self.descCanvas )
        self.descCanvas.setCanvasString( self.toolTipString )
        self.editor.diagramScene.addItem( self.descCanvas )
    #------------------------------------------------------------------------------------------------

    def renameModifications(self, name):
        '''Make neccessary modification and renaming.
        
        :param name: Name of the CPN element assigned by the user. 
        '''
        if self.substitutionTransition:
            for editor in self.editor.mainWindow.editors:
                if str( editor.subnet ) == str( self.name ):
                    editor.subnet = str( name )
#                     for place in editor.visualPlaces:
#                         place.subnet = name
#                     for transition in editor.visualTransitions:
#                         if not transition.substitutionTransition:
#                             transition.subnet = name                                   
        self.name = name        
#         self.subnet = self.name
        self.label.setPlainText(self.name)
    #------------------------------------------------------------------------------------------------


    def acceptEditGuard(self):
        '''Apply modified guard expression, after `gui.NameDialog`.
        '''
        guardExpression = self.guardDiag.getName()
        self.guardExpression = guardExpression
        self.guardLabel.setPlainText(self.guardExpression) 
        self.transition.guard = Expression( self.guardExpression )
        del self.guardDiag
    #------------------------------------------------------------------------------------------------
    
    
    def openSubnet(self):
        '''Forward menu action `Open Subnet` to `gui.DiagramEditor`.'''
        self.editor.mainWindow.openSubnet(self)
    #------------------------------------------------------------------------------------------------
    
    
    def importSubnet(self):
        '''Forward menu action `Import Subnet` to `gui.DiagramEditor`.'''
        self.editor.mainWindow.importSubnet(self)
    #------------------------------------------------------------------------------------------------
    
    
    def mousePressEvent(self, event):        
        '''Prevents the movement of this item, when connections are drawn.
        
        :param event: `QtGui.mousePressEvent`
        '''
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            self.editor.startArc(self)
        QtGui.QGraphicsRectItem.mousePressEvent(self, event)
    #------------------------------------------------------------------------------------------------
         
             
    def mouseMoveEvent(self, event):
        '''Prevents the movement of this item, when connections are drawn.
        
        :param event: `QtGui.mouseMoveEvent`
        '''
        if not event.modifiers() & QtCore.Qt.ShiftModifier:
            QtGui.QGraphicsRectItem.mouseMoveEvent(self, event)
    #------------------------------------------------------------------------------------------------
    
    
    def mouseReleaseEvent(self, event):
        '''Forward `QtGui.mouseReleaseEvent`.
        
        :param event: `QtGui.mouseReleaseEvent`
        '''
        QtGui.QGraphicsRectItem.mouseReleaseEvent(self, event)
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
        if self.substitutionTransition:
            self.contextMenuOpen = menu.addAction('Open Subnet')
            self.contextMenuOpen.triggered.connect(self.openSubnet)
            self.contextMenuImport = menu.addAction('Import Subnet')
            self.contextMenuImport.triggered.connect(self.importSubnet)
        else:
            self.contextMenuGurad = menu.addAction('Edit Guard Expression')
            self.contextMenuGurad.triggered.connect(self.editGuard)
        self.delete = menu.addAction('Delete Item')
        self.delete.triggered.connect(self.deleteItemLocal)
        menu.exec_(event.screenPos())
    #------------------------------------------------------------------------------------------------

#========================================================================================================================