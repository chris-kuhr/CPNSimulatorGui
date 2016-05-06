'''
Created on Apr 15, 2016

@author: christoph
'''

from PyQt4 import QtGui, QtCore, QtSvg, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
import math

            
class LineItem(QtGui.QGraphicsLineItem):
    def __init__(self, parent):
        super(LineItem, self).__init__(None)
        self.parent = parent
        self.setPen(QtGui.QPen(QtCore.Qt.black,2))
#         self.setFlags( self.ItemIsSelectable | self.ItemIsMoveable ) 
        
    #------------------------------------------------------------------------------------------------
        
#========================================================================================================================
    
class ArcItem(QtGui.QGraphicsItem):
    def __init__(self, parent=None, scene=None):
        super(ArcItem, self).__init__(None)
        self.scene = scene
        self.parent = parent
        self.arcLine = LineItem(self)
        self.parent.diagramScene.addItem(self.arcLine)  
        arrowPolygon = QtGui.QPolygonF( [ 
                                         QtCore.QPointF(  0.0,  0.0),
                                         QtCore.QPointF(  0.0, 10.0), 
                                         QtCore.QPointF( 10.0,  5.0)
                                         ] )
        self.arcLinePolygon = self.parent.diagramScene.addPolygon( arrowPolygon ) 
        self.pos1 = QtCore.QPointF(20,20)
        self.pos2 = QtCore.QPointF(200,200)
#         self.setFlags( self.ItemIsSelectable | self.ItemIsMoveable )
    
    def setPolygon(self):
        rotDeg = 0            
        xlength = self.pos1.x() - self.pos2.x()
        ylength = self.pos1.y() - self.pos2.y()
        d = math.sqrt( math.pow( xlength , 2) + math.pow( ylength , 2) )        
        if d > 0:
            beta = math.acos( xlength / d )
            rotDeg = math.degrees( beta ) 
        
        self.arcLinePolygon.setPolygon( QtGui.QPolygonF( [
                                                 QtCore.QPointF( (self.pos2.x() -10),  (self.pos2.y() +5)), 
                                                 QtCore.QPointF( (self.pos2.x() -10) , (self.pos2.y() -5)), 
                                                 QtCore.QPointF(       self.pos2.x() ,      self.pos2.y())
                                                 ] ) ) 
        
        self.arcLinePolygon.setBrush( QtGui.QBrush(QtCore.Qt.black) )
        
        """ self.angle()!!!!!!!!!"""
#         self.arcLinePolygon.angle()
#         self.arcLinePolygon.rotate(rotDeg)
#         self.arcLinePolygon.setPos( self.pos2 ) 
    #------------------------------------------------------------------------------------------------
        
    
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()    
        self.diagramScene = QtGui.QGraphicsScene(self)  
        uic.loadUi('arrow.ui', self)  
        self.graphicsView.setScene( self.diagramScene )
        t1 = QtGui.QGraphicsRectItem(QtCore.QRectF(20,20,100,50 )) 
        t1.setBrush(QtGui.QBrush(QtCore.Qt.white))
#         t1.setFlag( QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMoveable )
        self.diagramScene.addItem(t1) 
        p1 = QtGui.QGraphicsEllipseItem(QtCore.QRectF(200,200,100,50))
        p1.setBrush(QtGui.QBrush(QtCore.Qt.white))
#         p1.setFlags( QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMoveable )
        arc1 = ArcItem(self, self.diagramScene)
        arc1.arcLine.setLine(20,20,200,200)
        arc1.setPolygon()
        self.diagramScene.addItem(p1)
        self.show()
        pass
    
    
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow( )    
    sys.exit(app.exec_())
    pass