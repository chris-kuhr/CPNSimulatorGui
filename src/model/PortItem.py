from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class PortItem(QtGui.QGraphicsEllipseItem):
    '''Port place indicator. 
    
    The label indicates the port direction of the port place.
    
    :member direction: Port direction: (i)nput, (o)utput, (io) bidirectional.
    :member parent: Parent port place.
    :member label: Visual representation of direction.
    '''
    def __init__(self, direction, parent=None):
        '''Create a port
        
        :param direction:  Port direction: (i)nput, (o)utput, (io) bidirectional.
        :param parent: Parent port place.
        '''
        super(PortItem, self).__init__(QtCore.QRectF(-4.0,-4.0,17.0,17.0), parent)
        self.posChangeCallbacks = []
        self.setBrush(QtGui.QBrush(QtCore.Qt.white))
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsScenePositionChanges)
        self.label = QtGui.QGraphicsTextItem("", self)
        self.label.setPos(QtCore.QPointF( -4, -7))
        self.direction = direction
        self.setZValue(9)
    #------------------------------------------------------------------------------------------------

    def setDirection(self, direction):
        '''Set direction of the port.
        
        :param direction: Direction of port: "i", "o", "io".
        '''
        self.direction = direction
        self.label.setPlainText("%s"%self.direction)
    #------------------------------------------------------------------------------------------------
    def getDirection(self):
        '''Return direction of the port: "i", "o", "io".'''
        return self.direction
    #------------------------------------------------------------------------------------------------

           
    def editPort(self):
        '''Edit port direction.'''
        self.portDiag = NameDialog(title="Enter Direction", default=self.label.plainText() )
        self.portDiag.accepted.connect(self.setPort)
        self.portDiag.show()  
    #------------------------------------------------------------------------------------------------
           
    def setPort(self):        
        '''Is this really neccessary?'''
        self.port = PortItem(self)
        rect = self.label.boundingRect() 
        self.port.setPos( rect.width() + 20.0, rect.height() + 20.0 )
        self.setDirection( self.portDiag.getName() )  
        del self.portDiag   
        pass
    #------------------------------------------------------------------------------------------------
    
    def contextMenuEvent(self, event):
        '''Generate Context menu on context menu event.
        
        :param event: QContextMenuEvent.
        '''
        menu = QtGui.QMenu()
        self.delete = menu.addAction('Delete')
        self.delete.triggered.connect(self.deleteItemLocal)
        self.contextMenuEditPort = menu.addAction('Edit Port')
        self.contextMenuEditPort.triggered.connect(self.editPort)
        menu.exec_(event.screenPos())
    #------------------------------------------------------------------------------------------------
    
    
    def itemChange(self, change, value):
        '''Item position has changed, calculate new position.
        
        :param change: Change value.
        :param value: QtCore.QPointF().
        :return value: QtCore.QPointF(x, y) or super(PortItem, self).itemChange(change, value).
        '''
        if change == self.ItemPositionChange:
            x, y = value.x(), value.y()
            # TODO: make this a signal?
            # This cannot be a signal because this is not a QObject
            for cb in self.posChangeCallbacks:
                res = cb(x, y)
                if res:
                    x, y = res
                    value = QtCore.QPointF(x, y)
            
            return value
        # Call superclass method:
        return super(PortItem, self).itemChange(change, value)
    #------------------------------------------------------------------------------------------------
    
#========================================================================================================================
    