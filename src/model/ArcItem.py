from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import inspect
import logging

import math

import snakes.plugins
from snakes.nets import *

from gui.NameDialog import NameDialog
from model.PlaceItem import PlaceItem
from model.TransitionItem import TransitionItem

            
class LineItem(QtGui.QGraphicsLineItem):
    '''Visual representation of the line itself.
    
    :member parent: Parent `model.ArcItem`.
    '''
    def __init__(self, parent):
        '''Create line.
        
        :param parent: Parent `model.ArcItem`.
        '''
        super(LineItem, self).__init__(None)
        self.parent = parent
        self.setPen(QtGui.QPen(QtCore.Qt.black,2))
        self.setFlag(self.ItemIsSelectable, True)
    #------------------------------------------------------------------------------------------------
            
    def mouseDoubleClickEvent (self, event):
        '''Edit arc annotation on `QtGui.mouseDoubleClickEvent`.
        
        :param event: `QtGui.mouseDoubleClickEvent`.
        '''
#         pos = event.pos()
        self.parent.diag = NameDialog( parent=self.parent.editor, title="Rename %s %s"%( type(self.parent), self.parent.name ), default=self.parent.name)
        self.parent.diag.accepted.connect(self.parent.rename)
        self.parent.diag.show()
        QtGui.QGraphicsLineItem.mouseDoubleClickEvent(self, event)
    #-----------------------------------------------------------------------------------------------
    
#========================================================================================================================
    
    
class ArcItem(QtGui.QGraphicsItem):
    '''CPN arc connection element.
    
    :member editor: `gui.DiagramEditor`. Editor to show in.
    :member srcConnector: Source `model.AbstractItem.Connector`.
    :member dstConnector: Destination `model.AbstractItem.Connector`.
    :member isPortConnection: Flag that determines, whether the arc represents the connection between a substitution transition and a port place..
    :member name: Expression of the CPN arc assigned by the user. 
    :member arcDefined: Flag that determines, whether an arc creation was successful (internal).
    :member variable: SNAKES Variable. 
    :member expression: SNAKES Expression.  
    :member pos1: Point of origin of the arc.
    :member pos2: Point of destination of the arc.
    :member arrowPolygon: `QtGui.QPolygonF` showing the direction of the arc.        
    '''
    def __init__(self, editor, srcConnector, dstConnector, name="undefined", isPortConnection=False):
        '''
        
        :param editor: `gui.DiagramEditor`. Editor to show in.
        :param srcConnector: Source `model.AbstractItem.Connector`.
        :param dstConnector: Destination `model.AbstractItem.Connector`.
        :param name: Expression of the CPN arc assigned by the user. 
        :param isPortConnection: Flag that determines, whether the arc represents the connection between a substitution transition and a port place..
        '''
        QtGui.QGraphicsItem.__init__(self, None)
        self.editor = editor
        self.srcConnector = srcConnector
        self.dstConnector = dstConnector 
        self.isPortConnection = isPortConnection
        self.name = ""
        self.arcDefined = False
        self.variable = None
        self.expression = None
        self.diag = None        
        self.pos1 = None
        self.pos2 = None
        self.arrowPolygon = None
#         self.subnet = subnet
        self.setZValue(12)
        
        if self.srcConnector:            
            rect = self.srcConnector.rect()
            pos = self.mapFromItem( self.srcConnector, self.srcConnector.position )
            self.pos1 = QtCore.QPointF(pos.x() + rect.width()/2, pos.y() + rect.height()/2  )
            self.srcConnector.posCallbacks.append(self.setBeginPos)
            self.srcConnector.connectionArc = self
        
        self.arcLine = LineItem(self)
        self.editor.diagramScene.addItem(self.arcLine)  
        self.arrowPolygon = QtGui.QPolygonF( [ 
                                         QtCore.QPointF(  0.0,  0.0),
                                         QtCore.QPointF(  0.0, 10.0), 
                                         QtCore.QPointF( 10.0,  5.0)
                                         ] )
        self.arrowPolygonObject = self.editor.diagramScene.addPolygon( self.arrowPolygon )  
        self.label = QtGui.QGraphicsTextItem(name, self)
        self.label.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.editor.diagramScene.addItem(self.label)   
        
    #------------------------------------------------------------------------------------------------
        
    def setPolygon(self):
        '''Calculate position and rotation of the arc arrow head.'''
        rotDeg = 0            
        xlength = self.pos1.x() - self.pos2.x()
        ylength = self.pos1.y() - self.pos2.y()
        d = math.sqrt( math.pow( xlength , 2) + math.pow( ylength , 2) )        
        if d > 0:
            beta = math.acos( xlength / d )
            rotDeg = math.degrees( beta ) 
        
        self.arrowPolygonObject.setPolygon( QtGui.QPolygonF( [
                                                 QtCore.QPointF( (self.pos2.x() -10),  (self.pos2.y() +5)), 
                                                 QtCore.QPointF( (self.pos2.x() -10) , (self.pos2.y() -5)), 
                                                 QtCore.QPointF(       self.pos2.x() ,      self.pos2.y())
                                                 ] ) ) 
        
        self.arrowPolygonObject.setBrush( QtGui.QBrush(QtCore.Qt.black) )
        
        """ self.angle()!!!!!!!!!"""
#         self.arcLinePolygon.angle()
#         self.arcLinePolygon.rotate(rotDeg)
#         self.arcLinePolygon.setPos( self.pos2 ) 

    #------------------------------------------------------------------------------------------------
        
    def getName(self):
        '''Return the annotation of this arc.'''
        return self.name
    #------------------------------------------------------------------------------------------------
    
    def setName(self, name):
        '''Set the annotation of this arc.
        
        :param name: New annotation.
        '''
        self.name = name
        rect = self.arcLine.boundingRect()
        
        self.label.setPos(rect.center().x() + 10, rect.center().y() - 10)
        self.label.setPlainText(self.name)       
        self.setPolygon() 
    #------------------------------------------------------------------------------------------------
    
            
    def setDestination(self, dstConnector):
        '''Sets the destination `model.AbstractItem.Connector`.
        
        :param dstConnector: Destination `model.AbstractItem.Connector`.
        '''
        self.dstConnector = dstConnector
        if self.dstConnector:
            self.setZValue(12)
            
            if not self.isPortConnection: 
                
#                 self.editor.mainWindow.simulator.connectionList.append( [ self.srcConnector.parent, self, self.dstConnector.parent, self.srcConnector.idx, self.dstConnector.idx ] )
                self.editor.visualConnectionList.append( [ self.srcConnector, self, self.dstConnector, self.srcConnector.idx, self.dstConnector.idx ] )
            
            self.dstConnector.connectionArc = self  
            self.dstConnector.posCallbacks.append(self.setEndPos)
    #------------------------------------------------------------------------------------------------
        
    def setEndPos(self, endpos):
        '''Callback method to keep `pos2` up to date.
        
        :param endpos: `QtCore.QPointF()`.
        '''
        rect = self.srcConnector.rect()
        if self.dstConnector is not None:
            pos = self.mapFromItem( self.dstConnector, self.dstConnector.position )
            self.pos2 = QtCore.QPointF(pos.x() + rect.width()/2, pos.y() + rect.height()/2  )
        else:
            self.pos2 = endpos
                
        self.arcLine.setLine(QtCore.QLineF(self.pos1, self.pos2))
        self.setName(self.name)        
    #------------------------------------------------------------------------------------------------
        
    def setBeginPos(self, pos1):
        '''Callback method to keep `pos1` up to date.
        
        :param pos1: `QtCore.QPointF()`.
        '''
        rect = self.srcConnector.rect()
        pos = self.mapFromItem( self.srcConnector, self.srcConnector.position )
        self.pos1 = QtCore.QPointF(pos.x() + rect.width()/2, pos.y() + rect.height()/2  )
#         self.pos1 = pos1
        self.setName(self.name)                    
        self.arcLine.setLine(QtCore.QLineF(self.pos1, self.pos2))
    #------------------------------------------------------------------------------------------------
        
    
    def checkForExpression(self, text):
        '''Check whether the annotation is intended to be an expression or a variable.
        
        :param text: Annotation text.
        :return ret: True/False.
        '''
        if "<" in text:
            pass
        elif ">" in text:
            pass
        elif "=" in text:
            pass
        elif "+" in text:
            pass
        elif "-" in text:
            pass
        elif "*" in text:
            pass
        elif "/" in text:
            pass
        elif "!" in text:
            pass
        elif " if " in text:
            pass
        elif " else " in text:
            pass
        else:
            return False
        return True
    #------------------------------------------------------------------------------------------------
    
    
    def rename(self):
        '''Rename arc and apply changes to simulator and visual representation.'''
        if self.diag is not None and not self.isPortConnection:
            multiArc = False
            
            if str(self.diag.getName()).startswith("(") and  "," in self.diag.getName() and  str(self.diag.getName()).endswith(")"):
                multiArc = True
                multiArcAnnotations = self.diag.getName().replace("(", "").replace(")", "").split(",")
                    
                
            if isinstance( self.dstConnector.parent, TransitionItem ):
                self.editor.mainWindow.simulator.net.remove_input( self.srcConnector.parent.uniqueName , self.dstConnector.parent.uniqueName )
                
                if multiArc:
                    self.multiInput( multiArcAnnotations )
                else:
                    if self.checkForExpression( self.diag.getName() ):  
                        try:   
                            infoString = str( "Expression %s"%self.diag.getName() )
                            item = QtGui.QListWidgetItem( infoString )
                            item.setTextColor(QtCore.Qt.black)
                            self.editor.mainWindow.logWidget.addItem( item )
                            expression = Expression( str( self.diag.getName() ) )   
                            self.singleInput(expression)    
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                        except SyntaxError:
                            errorString = str( "Expression must contain a conditional expression %s" %( sys.exc_info()[1] ) )
                            item = QtGui.QListWidgetItem( errorString )
                            item.setTextColor(QtCore.Qt.red)
                            self.editor.mainWindow.logWidget.addItem( item )
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                    else:  
                        infoString = str( "Variable %s"%self.diag.getName() )
                        item = QtGui.QListWidgetItem( infoString )
                        item.setTextColor(QtCore.Qt.black)
                        self.editor.mainWindow.logWidget.addItem( item )
                        variable = Variable( str( self.diag.getName() ) )
                        self.singleInput( variable )
                        self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                    
            elif isinstance( self.dstConnector.parent, PlaceItem ):                      
                if multiArc:
                    errorString = str( "Multiarc is not defined for Transition Outputs: %s"%self.diag.getName() )
                    item = QtGui.QListWidgetItem( errorString )
                    item.setTextColor(QtCore.Qt.red)
                    self.editor.mainWindow.logWidget.addItem( item )
                    self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                    return  
                self.editor.mainWindow.simulator.net.remove_output( self.dstConnector.parent.uniqueName , self.srcConnector.parent.uniqueName )
                
                if self.checkForExpression( self.diag.getName() ): 
                    try:   
                        infoString = str( "Expression %s"%self.diag.getName() )
                        item = QtGui.QListWidgetItem( infoString )
                        item.setTextColor(QtCore.Qt.black)
                        self.editor.mainWindow.logWidget.addItem( item )
                        expression = Expression( str( self.diag.getName() ) ) 
                        self.singleOutput(expression)
                        self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                    except SyntaxError:
                        errorString = str( "Expression must contain a conditional expression %s" %( sys.exc_info()[1] ) )
                        item = QtGui.QListWidgetItem( errorString )
                        item.setTextColor(QtCore.Qt.red)
                        self.editor.mainWindow.logWidget.addItem( item )
                        self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                else:  
                    infoString = str( "Variable %s"%self.diag.getName() )
                    item = QtGui.QListWidgetItem( infoString )
                    item.setTextColor(QtCore.Qt.black)
                    self.editor.mainWindow.logWidget.addItem( item )
                    variable = Variable( str( self.diag.getName() ) )   
                    self.singleOutput(variable)
                    self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                    
        self.name = self.diag.getName()
        self.label.setPlainText(self.name)
        del self.diag
    #------------------------------------------------------------------------------------------------
    
    
    
    def singleInput(self, variableExpression):          
        '''Register a single input arc in the simulator.
        
        :param variableExpression: SNAKES Variable or Expression.
        '''
        try:      
            self.editor.mainWindow.simulator.net.add_input( self.srcConnector.parent.uniqueName, self.dstConnector.parent.uniqueName, variableExpression)
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
        except ValueError:
            errorString = str( "ValueError must contain valid Python Syntax: e.g. x>1, %s" %( sys.exc_info()[1] ) )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.editor.mainWindow.logWidget.addItem( item )
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
            del self
            return False
        except SyntaxError:
            errorString = str( "Expression must contain valid Python Syntax: e.g. x>1, %s" %( sys.exc_info()[1] ) )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.editor.mainWindow.logWidget.addItem( item )
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
            del self
            return False
        except snakes.ConstraintError:
            errorString = str( "ConstraintError: already connected to %s" %(self.dstConnector.parent.name) )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.editor.mainWindow.logWidget.addItem( item )
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
            del self
            return False
        return True
    #------------------------------------------------------------------------------------------------
    
    
    def multiInput(self, multiArcAnnotations):
        '''Register a multi input arc in the simulator.
        
        :param multiArcAnnotations: SNAKES MultiArc annotation.
        '''
        multiArcExpressions = []
        for annotation in multiArcAnnotations:
            if self.checkForExpression( annotation ):      
                multiArcExpressions.append( Expression( annotation ) )
            else:
                multiArcExpressions.append( Variable( annotation ) )
                
        self.singleInput( MultiArc( multiArcExpressions ) )
        return True
    #------------------------------------------------------------------------------------------------
    
    def singleOutput(self, variableExpression):
        '''Register a multi input arc in the simulator.
        
        :param variableExpression: SNAKES Variable or Expression.
        '''
        try:           
            self.editor.mainWindow.simulator.net.add_output( self.dstConnector.parent.uniqueName, self.srcConnector.parent.uniqueName, variableExpression)
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
        except ValueError:
            errorString = str( "ValueError: %s" %(sys.exc_info()[1]) )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.editor.mainWindow.logWidget.addItem( item )
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
            del self
            return False
        except SyntaxError:
            errorString = str( "SyntaxError: %s" %(sys.exc_info()[1]) )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.editor.mainWindow.logWidget.addItem( item )
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
            del self
            return False
        except snakes.ConstraintError:
            errorString = str( "ConstraintError: already connected to %s" %(self.dstConnector.parent.name) )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.red)
            self.editor.mainWindow.logWidget.addItem( item )
            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
            del self
            return False
        return True
    #------------------------------------------------------------------------------------------------
    
    
    def setArcAnnotation(self, annotationText=None):
        '''Finalize arc creation and set annotation.
        
        :param annotationText: String arc annotation.
        :return self.arcDefined: Flag that determines, whether an arc creation was successful (internal).
        '''
        if not self.arcDefined and not self.isPortConnection:
            multiArc = False
            text = annotationText
            if text is not None:
                if "(" in text and  "," in text and  ")" in text:
                    multiArc = True
                    multiArcAnnotations = text.replace("(", "").replace(")", "").split(",")
            if type(self.dstConnector.parent) is TransitionItem:
                if multiArc:
                    self.multiInput( multiArcAnnotations)
                else:
                    if self.checkForExpression( text ):      
                        if "==[]" in str( text ):
                            inhibitString = str( text ).split("==")[0]
                            infoString = str( "Inhibitor %s"%text )
                            
                            item = QtGui.QListWidgetItem( infoString )
                            item.setTextColor(QtCore.Qt.black)
                            self.editor.mainWindow.logWidget.addItem( item )
                            inhibitor = Inhibitor( Variable( inhibitString ) )
                            if self.singleInput( inhibitor ):
                                self.label.setPlainText( str( text ) )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                            else:
                                errorString = str( "Annotation %s could not be applied!"%text )
                                item = QtGui.QListWidgetItem( errorString )
                                item.setTextColor(QtCore.Qt.red)
                                self.editor.mainWindow.logWidget.addItem( item )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                            
                        else:
                            infoString = str( "Expression %s"%text )
                            item = QtGui.QListWidgetItem( infoString )
                            item.setTextColor(QtCore.Qt.black)
                            self.editor.mainWindow.logWidget.addItem( item )
                            expression = Expression( str( text ) )   
                            if self.singleInput( expression ):    
                                self.label.setPlainText( str( text ) )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                            else:
                                errorString = str( "Annotation %s could not be applied!"%text )
                                item = QtGui.QListWidgetItem( errorString )
                                item.setTextColor(QtCore.Qt.red)
                                self.editor.mainWindow.logWidget.addItem( item )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                    
                    else:  
                        infoString = str( "Variable %s"%text )
                        item = QtGui.QListWidgetItem( infoString )
                        item.setTextColor(QtCore.Qt.black)
                        self.editor.mainWindow.logWidget.addItem( item )
                        variable = Variable( str( text ) )
                        if self.singleInput( variable ):
                            self.label.setPlainText( str( text ) )
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                        else:
                            errorString = str( "Annotation %s could not be applied!"%text )
                            item = QtGui.QListWidgetItem( errorString )
                            item.setTextColor(QtCore.Qt.red)
                            self.editor.mainWindow.logWidget.addItem( item )
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                            
            elif type(self.dstConnector.parent) is PlaceItem:                            
                if multiArc:
                    errorString = str( "Multiarc is not defined for Transition Outputs: %s"%str( text ) )
                    item = QtGui.QListWidgetItem( errorString )
                    item.setTextColor(QtCore.Qt.red)
                    self.editor.mainWindow.logWidget.addItem( item )
                    self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                    del self
                    return False 
                else:
                    if self.checkForExpression( text ):    
                        infoString = str( "Expression %s"%text )
                        item = QtGui.QListWidgetItem( infoString )
                        item.setTextColor(QtCore.Qt.black)
                        self.editor.mainWindow.logWidget.addItem( item )
                        expression = Expression( str( text ) )  
                        if self.singleOutput( expression):    
                            self.label.setPlainText( str( text ) )
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                        else:
                            errorString = str( "Annotation %s could not be applied!"%text )
                            item = QtGui.QListWidgetItem( errorString )
                            item.setTextColor(QtCore.Qt.red)
                            self.editor.mainWindow.logWidget.addItem( item )
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                    else:  
                        infoString = str( "Variable %s"%text )
                        item = QtGui.QListWidgetItem( infoString )
                        item.setTextColor(QtCore.Qt.black)
                        self.editor.mainWindow.logWidget.addItem( item )
                        variable = Variable( str( text ) )   
                        if self.singleOutput( variable):
                            self.label.setPlainText( str( text ) )
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                        else:
                            errorString = str( "Annotation %s could not be applied!"%text )
                            item = QtGui.QListWidgetItem( errorString )
                            item.setTextColor(QtCore.Qt.red)
                            self.editor.mainWindow.logWidget.addItem( item )
                            self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                        
                    enabled = False
                    for connection in self.editor.mainWindow.simulator.connectionList: 
                        if connection[2] == self.srcConnector.parent:
                            try:
                                for mode in self.editor.mainWindow.simulator.net.transition( self.srcConnector.parent.uniqueName ).modes():
                                    if not enabled: 
                                            enabled =self.editor.mainWindow.simulator.net.transition( self.srcConnector.parent.uniqueName ).enabled( mode )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.black,2))
                            except NameError:
                                errorString = str( "Name Error: %s" %( sys.exc_info()[1] ) )
                                item = QtGui.QListWidgetItem( errorString )
                                item.setTextColor(QtCore.Qt.red)
                                self.editor.mainWindow.logWidget.addItem( item )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                                del self
                                return False
                            except ValueError:
                                errorString = str( "Value Error: must contain valid Python Syntax: e.g. x>1, %s" %( sys.exc_info()[1] ) )
                                item = QtGui.QListWidgetItem( errorString )
                                item.setTextColor(QtCore.Qt.red)
                                self.editor.mainWindow.logWidget.addItem( item )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                                del self
                                return False
                            except SyntaxError:
                                errorString = str( "Syntax Error: Expression must contain valid Python Syntax: e.g. x>1, %s" %( sys.exc_info()[1] ) )
                                item = QtGui.QListWidgetItem( errorString )
                                item.setTextColor(QtCore.Qt.red)
                                self.editor.mainWindow.logWidget.addItem( item )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                                del self
                                return False
                            except snakes.ConstraintError:
                                errorString = str(  "Constraint Error: already connected to %s" %(self.dstConnector.parent.name)  )
                                item = QtGui.QListWidgetItem( errorString )
                                item.setTextColor(QtCore.Qt.red)
                                self.editor.mainWindow.logWidget.addItem( item )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                                del self
                                return False
                            except snakes.DomainError: 
                                errorString = str( "Domain Error: unbound variable %s" %(sys.exc_info()[1]) )
                                item = QtGui.QListWidgetItem( errorString )
                                item.setTextColor(QtCore.Qt.red)
                                self.editor.mainWindow.logWidget.addItem( item )
                                self.arcLine.setPen(QtGui.QPen(QtCore.Qt.red,2))
                                del self
                                return False
                    if enabled:
                        self.srcConnector.parent.setPen(QtGui.QPen(QtCore.Qt.green, 4))
                        
                    self.srcConnector.parent.enabled = enabled
                    
            self.arcDefined = True
            
        
            logging.debug("-------Create----Arc----------------------------%s----------"%(self.name))
            logging.debug( "editor %s Start Pos: %s End Pos: %s Source %s Destination %s"%(self.editor, self.pos1, self.pos2, self.srcConnector.parent.uniqueName, self.dstConnector.parent.uniqueName))
            logging.debug( "is a Port Connection %s Variable %s Expression %s"%(self.isPortConnection, self.variable, self.expression))
            logging.debug("-----------------------------------------------------------------------------------")
            return self.arcDefined
        del self.arrowPolygon
        return self.arcDefined
    #------------------------------------------------------------------------------------------------
    
    
    def deleteItemLocal(self):
        '''Capture delete event and call editor delete function.'''
        self.editor.deleteItems(self.editor, [self])
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================
