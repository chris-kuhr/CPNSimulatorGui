#!/usr/bin/python3

from PyQt4 import QtGui, QtCore, QtSvg, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from collections import Counter, deque
import logging


import snakes.plugins
from snakes.nets import *

from io import StringIO, BytesIO

from inout.XMLIO import XMLIO

from gui.DiagramEditor import DiagramEditor
from gui.SubnetDialog import SubnetDialog
from gui.DiagramScene import DiagramScene
from gui.NameDialog import NameDialog
from gui.LibraryModel import LibraryModel

from model.AbstractItem import Connector
from model.PlaceItem import PlaceItem
from model.TransitionItem import TransitionItem
from model.TokenItem import TokenItem
from model.PortItem import PortItem
from model.ArcItem import ArcItem

from inout.XMLIO import XMLIO
from model.CPNSimulator import CPNSimulator

    
class MainWindow(QtGui.QMainWindow):
    """The MainWindow is loaded by the application main loop.
    
    :member workingDir: Working directory.
    :member editors: List of all editors: `gui.DiagramEditor`.
    :member editorwidgets: List of all editor widgets.    
    :member logWidget: Log widget.
    :member tabWidget: Widget containing `editors[0]`, and the `logWidget`.
    :member simulator: `model.CPNSimulator` instance.   
    :member timer: Simulation timer.    
    """
    
    def __init__(self, workingDir):
        '''Create the main window.
        
        The Class is initialized with the Layout, 
        specified in the CPNSimGui.ui file in the directory: workingDir/gui/. 
        
        :param workingDir: Working directory.
        '''
        
        self.workingDir = workingDir          
        
        super(QtGui.QMainWindow, self).__init__()         
        uic.loadUi('%s/gui/CPNSimGui.ui'%(self.workingDir), self)  
        
        self.editors = []
        self.editorwidgets = []    
        self.editorwidgets.append(None)          
        
        self.tabWidget = QtGui.QTabWidget(self)    
               
        self.editors.append( DiagramEditor(mainWindow=self, parent=self, workingDir=self.workingDir) )
        self.editors[0].resize(700, 800)  
        self.tabWidget.addTab(self.editors[0], "Net")
        
        self.logWidget = QtGui.QListWidget(self)         
        self.tabWidget.addTab(self.logWidget, "Log")   
        self.verticalLayout.addWidget(self.tabWidget) 
        
        self.setMinimumSize(QtCore.QSize(800, 600))
        self.setMaximumSize(QtCore.QSize(1980, 1080))
        self.centralwidget.setMinimumSize(QtCore.QSize(799, 599))
        self.centralwidget.setMaximumSize(QtCore.QSize(1979, 1079))
        
        self.pushButton_4.setCheckable(True)
        self.radioButton_2.toggle() 
        
        self.simulator = CPNSimulator(self)   
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.simulator.forwardStep)
        self.pushButton.connect(self.pushButton, QtCore.SIGNAL("pressed()"),self.simulator.back2beginning)
        self.pushButton_2.connect(self.pushButton_2, QtCore.SIGNAL("pressed()"),self.simulator.backStep)
        self.pushButton_3.connect(self.pushButton_3, QtCore.SIGNAL("pressed()"),self.simulator.stopSim)
#         self.pushButton_4.connect(self.pushButton_4, QtCore.SIGNAL("toggled(bool)"),self.editor.startSim)
        self.pushButton_4.connect(self.pushButton_4, QtCore.SIGNAL("pressed()"),self.simulator.startSim)
        self.pushButton_5.connect(self.pushButton_5, QtCore.SIGNAL("pressed()"),self.simulator.forwardStep)
        self.pushButton_6.connect(self.pushButton_6, QtCore.SIGNAL("pressed()"),self.simulator.forward2lastStep)
        self.pushButton_7.connect(self.pushButton_7, QtCore.SIGNAL("pressed()"),self.simulator.resetSimulator)
        self.actionNew_Net.connect(self.actionNew_Net, QtCore.SIGNAL("triggered()"), self.newNet)
        self.actionOpen_Net.connect(self.actionOpen_Net, QtCore.SIGNAL("triggered()"), self.loadNet)
        self.actionSave_Net.connect(self.actionSave_Net, QtCore.SIGNAL("triggered()"), self.saveNet)
        self.actionExport_Step_as_SVG.connect(self.actionExport_Step_as_SVG, QtCore.SIGNAL("triggered()"), self.export_Step_as_SVG)
        
        self.lineEdit_2.setText( "%d %%" %( int( self.editors[0].diagramView.scaleFactor*100 ) ) )
        self.lineEdit.setText( "%d/%d"%( self.simulator.displayStep, self.simulator.simulationStep ) )
        self.newNet(True)
        
        self.showMaximized()
    #-------------------------------------------------------------------
    
    
    def newNet(self, init=False):
        '''Create a new Petrinet.                
        
        This method resets the main editor widget. It deletes 
        the previously loaded Petrinet, as well as any hierarchical subnet.  
                
        @param init: Load on startup?
        '''
        
        for transition in self.editors[0].visualTransitions:
            if transition.substitutionTransition:
                self.editors[0].deleteItems(self.editors[0], [transition])
                
        for editor in self.editors[1:]:
            self.editors.remove(editor)  
        for editorWidget in self.editorwidgets[1:]:
            del editorWidget.editor
            self.editorwidgets.remove(editorWidget) 
            
            
        self.simulator.connectionList = []
        self.simulator.transitions = []
        self.simulator.places = []
        
        if init:
            self.simulator.subnets = []
        else:
            self.simulator.subnets = [["None",[]]]
           
                
        self.editors[0].visualTransitions = []
        self.editors[0].visualPlaces = []
        self.editors[0].visualConnectionList = []
        self.editors[0].portConnections = []
        self.editors[0].diagramScene.clear()
        
        self.simulator.net = PetriNet("Default")                 
        self.simulator.initialMarking = self.simulator.net.get_marking()
        self.simulator.uniqueNameBase = int("0DDF00D", 16)
                
        self.simulator.resetSimulator()
        self.setWindowTitle("pyPetriNets - %s"%( str(self.simulator.net) ) )
                      
        
        if not init:                             
            self.diag = NameDialog(title="PetriNet Name", default="unnamed")
            self.diag.accepted.connect(self.simulator.setNetName)
            self.diag.show()  
            
    #------------------------------------------------------------------------------------------------
    
    def addSubnetEditor(self, subnet):
        '''Create a subnet editor.
        
        @param subnet: The string name of the substitution transition, name of the subnet
        '''
        self.editorwidgets.append( SubnetDialog(mainWindow=self, parent=self, subnet=subnet) )
        self.editors.append( self.editorwidgets[-1].editor )
        self.editors[-1].tokenListItems = []
        self.editors[-1].colorListWidget.clear()
        for item in reversed( self.editors[0].tokenListItems ):
            self.editors[-1].colorListWidget.addItem( QtGui.QListWidgetItem( str( item ) ) )
    #------------------------------------------------------------------------------------------------
    
    
    def openSubnet(self, transition):
        '''Open subnet editor.
        
        :param transition: Substitution transition `model.TransitionItem`.
        '''
        for editorWidget in self.editorwidgets[1:]:            
            for editor in self.editors:
                if editorWidget.editor == editor:
                    if editor.subnet == transition.name:
                        editorWidget.show()
                                              
    #------------------------------------------------------------------------------------------------
            
            
    def importSubnet(self, transition):
        '''Import subnet into editor.
        
        :param transition: Substitution transition `model.TransitionItem`.
        '''
        filename = QtGui.QFileDialog.getOpenFileName( self, "Import Subnet", "%s/output/cpn/"%(self.workingDir) , "*.xml" )
        if filename is "":
            return  
                
        for editor in self.editors[1:]: 
            if str( editor.subnet ) == str( transition.name ):
                self.loadNet(editor=editor, filename=filename, subnet=transition.name, importSubnet=True)
    #------------------------------------------------------------------------------------------------
    
    
    def saveNet(self):
        '''Save Petrinet with respect to subnets to XML file.'''
        filename = QtGui.QFileDialog.getSaveFileName( self, "Save Net", "%s/output/cpn/"%(self.workingDir) , "*.xml" )
        if filename is "":
            return    
        xmlnet = XMLIO(self.simulator, rootElementName="ColouredPetriNet")
        
        for editor in self.editors:               
            newVisualConnectionList = []
            for arc in editor.visualConnectionList:
                if isinstance( arc, ArcItem ):
                    newVisualConnectionList.append( [ arc.srcConnector, arc, arc.dstConnector, arc.srcConnector.idx, arc.dstConnector.idx ] )
                else:
                    newVisualConnectionList.append( arc )
            
            cpn = xmlnet.netToXML(editor.subnet, editor.visualPlaces, editor.visualTransitions, newVisualConnectionList)
            
            logStringList = []
            for idx in range( 0, self.logWidget.count() ):
                lineItem = self.logWidget.item( idx )
                logStringList.append( str( lineItem.text() ) )
            
            xmlnet.saveLog(logStringList)        
        xmlnet.saveNet( filename )        
    #------------------------------------------------------------------------------------------------
    
    
    def loadNet( self, editor=None, filename=None, subnet=None, importSubnet=False):
        '''Load a net with subnets or import subnets from file.
        
        :param editor: `gui.DiagramEditor` to fill with the subnet. `editors[0]` if editor=none
        :param filename: The filename that is used when a new net is loaded.
        :param subnet: Subnet string name.
        :param importSubnet: Flag determining, whethera new net is loaded or a subnet is imported.
        '''
        if filename is None:                
            filename = QtGui.QFileDialog.getOpenFileName( self, "Open Net", "%s/output/cpn/"%(self.workingDir) , "*.xml" )
            if filename is "":
                return        
            self.newNet(init=True)  

        self.connectArcs = []   
        tmpSubnets = []    
                
        xmlnet = XMLIO(self)     
        ret = xmlnet.loadNet(filename)   
        
        subnetNames = ret[1]
        serConnections = ret[2]
        serPlaces = ret[3]
        serTransitions = ret[4]
             
        if importSubnet:              
            importUniqueNameList = []
            for _, place in serPlaces:
                unameContained = False
                for uName in importUniqueNameList:
                    if str( place[0] ) == str( uName ):
                        unameContained = True
                if not unameContained:
                    importUniqueNameList.append( place[0] )
                
            for _, transition in serTransitions:
                unameContained = False
                for uName in importUniqueNameList:
                    if str( transition[0] ) == str( uName ):
                        unameContained = True
                if not unameContained:
                    importUniqueNameList.append( transition[0] )
                           
            newSerPlaces = []
            newSerTransitions = []
            newSerConnectionsFlagged = []
            
            for connection in serConnections:                
                newSerConnectionsFlagged.append( 
                                                [ connection, False, False ] 
                                                )    
            for uName in importUniqueNameList:                                
                self.simulator.uniqueNameBase += 1   
                             
                for place in serPlaces:
                    if str( uName ) == str( place[1][0] ):
                        place[1][0] = "p%d"%self.simulator.uniqueNameBase 
                        if str( uName ) == str( place[1][2] ): 
                            place[1][2] = None
                        newSerPlaces.append( place )
                        serPlaces.remove( place )
                        for idx, connectionFlagged in enumerate( newSerConnectionsFlagged ):
                            if str( uName ) == str( connectionFlagged[0][1][0] ) and not connectionFlagged[1]: 
                                newSerConnectionsFlagged[idx][0][1][0] = "p%d"%self.simulator.uniqueNameBase    
                                newSerConnectionsFlagged[idx][1] = True
                            if str( uName ) == str( connectionFlagged[0][1][1] ) and not connectionFlagged[2]: 
                                newSerConnectionsFlagged[idx][0][1][1] = "p%d"%self.simulator.uniqueNameBase   
                                newSerConnectionsFlagged[idx][2] = True  
                            
                for transition in serTransitions:
                    if str( uName ) == str( transition[1][0] ): 
                        transition[1][0] = "t%d"%self.simulator.uniqueNameBase  
                        newSerTransitions.append( transition )
                        serTransitions.remove( transition )                           
                        for idx, connectionFlagged in enumerate( newSerConnectionsFlagged ):
                            if str( uName ) == str( connectionFlagged[0][1][0] ) and not connectionFlagged[1]: 
                                newSerConnectionsFlagged[idx][0][1][0] = "t%d"%self.simulator.uniqueNameBase     
                                newSerConnectionsFlagged[idx][1] = True
                            if str( uName ) == str( connectionFlagged[0][1][1] ) and not connectionFlagged[2]: 
                                newSerConnectionsFlagged[idx][0][1][1] = "t%d"%self.simulator.uniqueNameBase     
                                newSerConnectionsFlagged[idx][2] = True
                    
            serPlaces = newSerPlaces
            serTransitions = newSerTransitions
            serConnections = []
            
            for connectionFlagged in newSerConnectionsFlagged:
                serConnections.append(connectionFlagged[0])
                    
                  
            for subnetName  in subnetNames: 
                if str( subnetName ) == None or str( subnetName ) == str("None"):       
                    tmpSubnets.append([editor.subnet])                    
                    for idx, transition in enumerate( serTransitions ): 
                        if str( transition[0] ) == None or str( transition[0] ) == str("None"): 
                            serTransitions[idx][0] = editor.subnet 
                    for idx, place in enumerate( serPlaces ): 
                        if str( place[0] ) == None or str( place[0] ) == str("None"): 
                            serPlaces[idx][0] = editor.subnet    
                    for idx, connection in enumerate( serConnections ):
                        if str( connection[0] ) == None or str( connection[0] ) == str("None"): 
                            serConnections[idx][0] = editor.subnet       
                    continue      
                
                for editor2 in self.editors[1:]:
                    if str( subnetName ) == str( editor2.subnet ):
                        newName = "%s_2"%subnetName  
                        for idx, transition in enumerate( serTransitions ):     
                            if str( transition[0] ) == str( subnetName ):
                                serTransitions[idx][0] = newName  
                            if str( transition[1][1] ) == str( subnetName ):
                                serTransitions[idx][1][1] = newName 
                                serTransitions[idx][1][4] = newName 
                                
                        for idx, place in enumerate( serPlaces ): 
                            if str( place[0] ) == str( subnetName ):
                                serPlaces[idx][0] = newName    
                        for idx, connection in enumerate( serConnections ): 
                            if str( connection[0] ) == str( subnetName ):
                                serConnections[idx][0] = newName 
                                   
                        tmpSubnets.append([newName])                        
            tmpSubnets = self.createSubnetItemLists( tmpSubnets, serPlaces, serTransitions, serConnections )            
                        
        else:                    
            for subnetName in subnetNames:
                tmpSubnets.append([subnetName])
            tmpSubnets = self.createSubnetItemLists( tmpSubnets, serPlaces, serTransitions, serConnections ) 
                
        
                
        subnetConnections = self.createItemsAssignToEditor( editor, subnet, tmpSubnets, importSubnet=importSubnet )
        
        
            
        for connection in subnetConnections:
            for c in connection:
                logging.debug(str(c))
              
        subnetConnections = self.lookupSubstitutionConnectors( subnetConnections )
                
        self.simulator.uniqueNameBase += 1
        self.simulator.initialMarking = self.simulator.net.get_marking()
        self.simulator.resetSimulator(init=True)            
        self.simulator.getActualMarking(self.simulator.initialMarking)  
        
        if not importSubnet:
            self.simulator.subnets = tmpSubnets
        else:
            self.simulator.subnets += tmpSubnets
            
    #------------------------------------------------------------------------------------------------
    
    
    def createSubnetItemLists(self, tmpSubnets, serPlaces, serTransitions, serConnections):
        '''Assign subnet to items.
        
        :param tmpSubnets: List of subnet names
        :param serPlaces: List with parameters for the Place generation: [[uniqueName, name, portClone, port, [pos], [initMarking]],...].
        :param serTransitions: List with parameters for the Transition generation: [[uniqueName, name, [pos], guardExpression, subnet],...].
        :param serConnections: List with parameters for the Connection generation: [[uniqueNameSRC, uniqueNameDST, name, sourceConnector, destinationConnector],...].
        :return newTmpSubnets: List of subnet names and corresponding items ["subnet",[items]].
        '''
        newTmpSubnets = list( tmpSubnets )
        for idx, subnetList in enumerate( newTmpSubnets ):   
            for subnetRef, place in serPlaces:
                if str( subnetRef ) == str( subnetList[0] ):
                    newTmpSubnets[idx].append( place )           
            for subnetRef, transition in serTransitions:
                if str( subnetRef ) == str( subnetList[0] ):
                    newTmpSubnets[idx].append( transition )           
            for subnetRef, connection in serConnections:
                if str( subnetRef ) == str( subnetList[0] ):
                    newTmpSubnets[idx].append( connection )
        return newTmpSubnets
    #------------------------------------------------------------------------------------------------
    
            
    
    def initNetFromFile(self, editor, subnetList):     
        '''Create all items for a subnet.
        
        :param editor: `gui.DiagramEditor` subnet.
        :param subnetList: "subnet",[items].
        :return places, transitions, connectionsInSubnet: List of visual places, List of visual Transitions, list of visualk connections.
        '''
        places = []
        transitions = []
        connectionsInSubnet = []
                
        for item in subnetList[1:]:
            if isinstance( item[4], list ): 
                if str( item[2] ) == str("None"):
                    tokens = deque()
                    for token in item[5]:
                        tokens.append( str(token))
                    p = PlaceItem(editor, item[1], QtCore.QPointF(float(item[4][0]),float(item[4][1])), initMarking=tokens, uniqueName=item[0], loadFromFile=True, portDirection=item[3], subnet=editor.subnet)
                    places.append( [editor.subnet, p] )
                
            elif isinstance( item[2], list ):  
                if str( item[3] ) != str("None"):
                    t = TransitionItem(editor, item[1],  QtCore.QPointF(float(item[2][0]),float(item[2][1])), guardExpression=item[3], uniqueName=item[0], loadFromFile=True, subnet=editor.subnet)
                else:
                    t = TransitionItem(editor, item[1],  QtCore.QPointF(float(item[2][0]),float(item[2][1])), guardExpression=item[3], uniqueName=item[0], loadFromFile=True, subnet=item[4], substitutionTransition=True)
                transitions.append( [editor.subnet, t] ) 
                
            else: 
                self.connectArcs.append( [editor.subnet, item] )
                connectionsInSubnet.append( item )

        higherNameBase = True
        highestNameBase = self.simulator.uniqueNameBase
        oldNameBase = self.simulator.uniqueNameBase
         
        while higherNameBase:                     
            for place in places:
                pId = int( str( place[1].uniqueName ).split("p")[1] )
                if pId > highestNameBase:
                    highestNameBase = pId
                                   
            for transition in transitions:
                tId = int( str( transition[1].uniqueName ).split("t")[1] )
                if tId > highestNameBase:
                    highestNameBase = tId
                                                 
            if oldNameBase == highestNameBase:
                higherNameBase = False
            else:
                oldNameBase = highestNameBase
         
        self.simulator.uniqueNameBase = int( highestNameBase )
        
        return places, transitions, connectionsInSubnet
    #------------------------------------------------------------------------------------------------
           
      
    def createItemsAssignToEditor(self, editor, subnet, tmpSubnets, importSubnet=False):
        '''Assign places, transition and connections to subnet editors
        
        :param editor: `gui.DiagramEditor` subnet.
        :param subnet: Subnet string name.
        :param tmpSubnets: List of subnet names and corresponding items ["subnet",[items]].
        :param importSubnet: Flag determining, whethera new net is loaded or a subnet is imported.
        :return subnetConnections: List of connection in subnet for later inter subnet processing.
        '''
        self.mappingUniqueName = []
        subnetConnections = []             
        
        for subnetList in tmpSubnets:
            if editor is not None:
                editor.subnet = subnet    
                    
                subPlaces, subTransitions, connectionsInSubnet = self.initNetFromFile( editor, subnetList )
                for subPlace in subPlaces:
                    subPlace[1].subnet = subnet
                    if (subPlace[1].port is None and subPlace[1].portClone is None) \
                            or (subPlace[1].port is not None and subPlace[1].portClone is not None):
                        subPlace[1].place = Place( subPlace[1].uniqueName , subPlace[1].initMarking )
                        self.simulator.net.add_place( subPlace[1].place )                 
                        self.simulator.places.append(subPlace[1])
                        infoString = "Place added. Unique Name: %s - Display Name: %s - Port: %s - Tokens: %s"%(subPlace[1].uniqueName, subPlace[1].name, subPlace[1].portDirection, subPlace[1].initMarking)
                        item = QtGui.QListWidgetItem( str( infoString ) )
                        item.setTextColor(QtCore.Qt.green)
                        self.logWidget.addItem( item )
                        
                for subTransition in subTransitions:
                    if not subTransition[1].substitutionTransition:
                        try:
                            subTransition[1].transition = Transition( subTransition[1].uniqueName, Expression(subTransition[1].guardExpression) )
                            self.simulator.net.add_transition( subTransition[1].transition ) 
                            self.simulator.transitions.append( subTransition[1] )
                            infoString = "Transition added. Unique Name: %s - Display Name: %s - Guard Expression: %s"%(subTransition[1].uniqueName, subTransition[1].name, subTransition[1].guardExpression)
                            item = QtGui.QListWidgetItem( str( infoString ) )
                            item.setTextColor(QtCore.Qt.green)
                            self.logWidget.addItem( item )
                        except SyntaxError:
                            item = QtGui.QListWidgetItem( str( sys.exc_info()[1] ) )
                            item.setTextColor(QtCore.Qt.red)
                            self.logWidget.addItem( item ) 
#                 editor = None 
                            
            elif str( subnetList[0] ) == str("None") and subnet is None:
                self.setWindowTitle("pyPetriNets - %s"%( str(self.simulator.net) ) )
                subPlaces, subTransitions, connectionsInSubnet = self.initNetFromFile( self.editors[0], subnetList )
                for subPlace in subPlaces:
                    subPlace[1].subnet = subnetList[0]
                    if (subPlace[1].port is None and subPlace[1].portClone is None) \
                            or (subPlace[1].port is not None and subPlace[1].portClone is not None):
                        subPlace[1].place = Place( subPlace[1].uniqueName , subPlace[1].initMarking )
                        self.simulator.net.add_place( subPlace[1].place )                 
                        self.simulator.places.append(subPlace[1])
                        infoString = "Place added. Unique Name: %s - Display Name: %s - Port: %s - Tokens: %s"%(subPlace[1].uniqueName, subPlace[1].name, subPlace[1].portDirection, subPlace[1].initMarking)
                        item = QtGui.QListWidgetItem( str( infoString ) )
                        item.setTextColor(QtCore.Qt.green)
                        self.logWidget.addItem( item )
                        
                for subTransition in subTransitions:
                    if not subTransition[1].substitutionTransition:
                        try:
                            subTransition[1].transition = Transition( subTransition[1].uniqueName, Expression(subTransition[1].guardExpression) )
                            self.simulator.net.add_transition( subTransition[1].transition ) 
                            self.simulator.transitions.append( subTransition[1] )
                            infoString = "Transition added. Unique Name: %s - Display Name: %s - Guard Expression: %s"%(subTransition[1].uniqueName, subTransition[1].name, subTransition[1].guardExpression)
                            item = QtGui.QListWidgetItem( str( infoString ) )
                            item.setTextColor(QtCore.Qt.green)
                            self.logWidget.addItem( item )
                        except SyntaxError:
                            item = QtGui.QListWidgetItem( str( sys.exc_info()[1] ) )
                            item.setTextColor(QtCore.Qt.red)
                            self.logWidget.addItem( item ) 
            else:
                                
                self.addSubnetEditor( subnetList[0] )    
                subPlaces, subTransitions, connectionsInSubnet = self.initNetFromFile( self.editors[-1], subnetList )
                
                
                
                for subPlace in subPlaces:      
                    if (subPlace[1].port is None and not ( "i" in subPlace[1].portDirection and "o" in subPlace[1].portDirection ) ) \
                            or (subPlace[1].port is not None):
                        subPlace[1].place = Place( subPlace[1].uniqueName , subPlace[1].initMarking )
                        self.simulator.net.add_place( subPlace[1].place )                  
                        self.simulator.places.append( subPlace[1] )
                        infoString = "Place added. Unique Name: %s - Display Name: %s - Port: %s - Tokens: %s"%(subPlace[1].uniqueName, subPlace[1].name, subPlace[1].portDirection, subPlace[1].initMarking)
                        item = QtGui.QListWidgetItem( str( infoString ) )
                        item.setTextColor(QtCore.Qt.green)
                        self.logWidget.addItem( item )
                        
                for subTransition in subTransitions:
                    if not subTransition[1].substitutionTransition:
                        try:
                            subTransition[1].transition = Transition( subTransition[1].uniqueName, Expression(subTransition[1].guardExpression) )
                            self.simulator.net.add_transition( subTransition[1].transition ) 
                            self.simulator.transitions.append( subTransition[1] )
                            infoString = "Transition added. Unique Name: %s - Display Name: %s - Guard Expression: %s"%(subTransition[1].uniqueName, subTransition[1].name, subTransition[1].guardExpression)
                            item = QtGui.QListWidgetItem( str( infoString ) )
                            item.setTextColor(QtCore.Qt.green)
                            self.logWidget.addItem( item )
                        except SyntaxError:
                            item = QtGui.QListWidgetItem( str( sys.exc_info()[1] ) )
                            item.setTextColor(QtCore.Qt.red)
                            self.logWidget.addItem( item ) 
                            
                            
            subnetConnections.append( connectionsInSubnet )     
                          
        logging.debug( str(self.simulator.net.place()) )
        logging.debug( str(self.simulator.net.transition()) )
        
        return subnetConnections
    #------------------------------------------------------------------------------------------------
    

    def lookupSubstitutionConnectors(self, subnetConnections):
        '''Lookup and substitute connectors.
        
        :param subnetConnections: List of connection in subnet for inter subnet processing.
        '''
        lengthSubnetConnections = len( subnetConnections )
        lengthSubnetSimulator = len( self.simulator.subnets )
        for idx in range( lengthSubnetSimulator, lengthSubnetConnections + lengthSubnetSimulator ):            
            for subArc in subnetConnections[idx - lengthSubnetSimulator]:
                
                foundSrcConnector = False
                foundDstConnector = False
                for place in self.editors[idx].visualPlaces:   
                    if not foundSrcConnector: 
                        if str( place.uniqueName ) == str( subArc[0] ) and not isinstance( subArc[3], Connector ):
                            subArc[3] = place.connectorList[ int( subArc[3] ) ]    
                            foundSrcConnector = True                              
                        elif  isinstance( subArc[3], Connector ) and not isinstance( subArc[4], Connector ):  
                            foundSrcConnector = True             
                            
                    if not foundDstConnector:
                        if str( place.uniqueName ) == str( subArc[1] ) and not isinstance( subArc[4], Connector ):                                
                            subArc[4] = place.connectorList[  int( subArc[4] )  ] 
                            foundDstConnector = True                
                        elif  isinstance( subArc[4], Connector ) and not isinstance( subArc[3], Connector ):  
                            foundDstConnector = True                                       
                                     
                for transition in self.editors[idx].visualTransitions:   
                    if not foundSrcConnector:
                        if str( transition.uniqueName ) == str( subArc[0] ) and not isinstance( subArc[3], Connector ): 
                            subArc[3]  = transition.connectorList[  int( subArc[3] )  ]   
                            foundSrcConnector = True                
                        elif  isinstance( subArc[3], Connector ) and not isinstance( subArc[4], Connector ):  
                            foundSrcConnector = True  
                    if not foundDstConnector:
                        if str( transition.uniqueName ) == str( subArc[1] ) and not isinstance( subArc[4], Connector ):
                            subArc[4] = transition.connectorList[  int( subArc[4] )  ]   
                            foundDstConnector = True                     
                        elif  isinstance( subArc[4], Connector ) and not isinstance( subArc[3], Connector ):    
                            foundDstConnector = True   
                                
                if foundSrcConnector and foundDstConnector:
                    newArc = self.setArc(self.editors[idx], subArc[3], subArc[4], subArc[2])
#                     print("FOUND Arc", subArc[3].parent.uniqueName, newArc, subArc[4].parent.uniqueName, subArc[3].idx , subArc[4].idx )
                    logging.debug("Found Arc %s %s %s %d %d "%( subArc[3].parent.uniqueName, newArc, subArc[4].parent.uniqueName, subArc[3].idx , subArc[4].idx ) )
                    self.simulator.connectionList.append( [subArc[3].parent, newArc, subArc[4].parent, subArc[3].idx , subArc[4].idx] )
                    infoString = "Arc Connection added. Source Unique Name: %s - Source Name: %s - Destination Unique Name: %s - Destination Name: %s - Annotation: %s"%(subArc[3].parent.uniqueName, subArc[3].parent.name, subArc[4].parent.uniqueName, subArc[4].parent.name, newArc.name)
                    item = QtGui.QListWidgetItem( infoString )
                    item.setTextColor(QtCore.Qt.green)
                    self.logWidget.addItem( item )

    #------------------------------------------------------------------------------------------------
        
        
    def setArc(self, editor, srcConnector, dstConnector, itemName):   
        '''Create arcs based on new uniqueNames.
        
        :param editor: `gui.DiagramEditor` subnet.
        :param srcConnector: Source `model.AbstractItem.Connector`.
        :param dstConnector: Destination `model.AbstractItem.Connector`.
        :param itemName: Annotation text.
        :return newArc: Newly created `model.ArcItem`.
        '''
        newArc = ArcItem(editor, srcConnector, dstConnector)
        newArc.setEndPos(dstConnector.scenePos())  
        newArc.setDestination(dstConnector)      
        newArc.setName(itemName) 

        if isinstance(srcConnector.parent, PlaceItem):
            if srcConnector.parent.port is not None \
                        and str( srcConnector.parent.port ) != str("None") \
                        and srcConnector.parent.portClone is not None \
                        and str( srcConnector.parent.portClone ) != str("None"):
                pass  
            else:      
                newArc.setArcAnnotation( annotationText=itemName )
        elif isinstance(dstConnector.parent, PlaceItem): 
            if dstConnector.parent.port is not None \
                        and str( dstConnector.parent.port ) != str("None") \
                        and dstConnector.parent.portClone is not None \
                        and str( dstConnector.parent.portClone ) != str("None"):
                pass  
            else:      
                newArc.setArcAnnotation( annotationText=itemName )
                 
        if isinstance(srcConnector.parent, TransitionItem):
            if not srcConnector.parent.substitutionTransition:             
                if srcConnector.parent.subnet is not None \
                            and str( srcConnector.parent.subnet ) != str("None"):
                    newArc.setArcAnnotation( annotationText=itemName )
                else:   
                    pass  
            else:      
                newArc.setArcAnnotation( annotationText=itemName )                
        elif isinstance(dstConnector.parent, TransitionItem): 
            if not dstConnector.parent.substitutionTransition:
                if dstConnector.parent.subnet is not None \
                            and str( dstConnector.parent.subnet ) != str("None"):
                    newArc.setArcAnnotation( annotationText=itemName )
                else:   
                    pass                            
            else:      
                newArc.setArcAnnotation( annotationText=itemName )
                
        return newArc
    #------------------------------------------------------------------------------------------------
    
        
    def export_Step_as_SVG(self):
        '''Export Petrinet and subnets to seperate SVG files'''
        filename = QtGui.QFileDialog.getSaveFileName( self, "Export Step as SVG", "%s/output/svg/"%(self.workingDir) , "*.svg" )
        if filename is "":
            return
        
        iterString = ""        
        for editor in self.editors:
            
            if editor is self.editors[0]:
                iterString = "_%s" %self.simulator.net
            else:
                iterString = "_%s" %editor.subnet
                
            generator = QtSvg.QSvgGenerator()
            newFilename = filename
            if ".svg" in filename:
                newFilename = filename.split(".svg")[0]+iterString+".svg"
            else:
                newFilename = filename+iterString+".svg"
                        
            generator.setFileName(newFilename)            
            rect = editor.diagramScene.sceneRect()
            generator.setSize(QtCore.QSize(rect.width(), rect.height()))
            generator.setViewBox(QtCore.QRect(0, 0, rect.width(), rect.height()))
            generator.setTitle("%s Step %d"%(str(self.simulator.net), self.simulator.displayStep))
            painter = QtGui.QPainter()
            painter.begin(generator)
            editor.diagramScene.render( painter, source=rect , mode=QtCore.Qt.KeepAspectRatio)
            painter.end()
        
    #------------------------------------------------------------------------------------------------
        
    
    def closeEvent(self, event):
        '''Close window event.
        
        :param event: `QtGui.closeEvent`.
        '''
    #-------------------------------------------------------------------------------------------------------------------------
        
#==============================================================================================================================
