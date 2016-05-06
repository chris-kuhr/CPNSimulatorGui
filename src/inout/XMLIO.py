from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import re
import sys

from lxml import etree as et
from collections import Counter, deque
import logging


# from model.PlaceItem import PlaceItem
# from model.TransitionItem import TransitionItem
# from model.TokenItem import TokenItem
# from model.ArcItem import ArcItem
# from model.PortItem import PortItem
# from model.VisualNodes import *


class XMLIO(object):
    '''XML Input and Output'''
    def __init__(self, simulator, rootElementName=""):
        '''Init XML parser.
        
        :param simulator: Simulator to import to or export from.
        :param rootElementName: XML root element.
        '''
        self.simulator = simulator
        if str( rootElementName ) != "":
            self.cpn = et.Element(rootElementName)
            self.cpn.text = str(simulator.net)
    #------------------------------------------------------------------------------------------------
        
    def loadNet(self, filename):
        '''Parse XML file and prepare data for object creation.
        
        :param filename: Filepath to XML file which shall be loaded.
        :return [ netName, subnets, serConnections, serPlaces, serTransitions ]: A list containing lists for object creation.
        '''
        
        parser = et.XMLParser(dtd_validation=False)
        serPlaces = []
        serTransitions = []        
        serConnections = []
        subnets = []
        lastConnection = None
        netName = ""
        
        try:
            foundPlace = False
            foundTransition = False
            foundConnection = False
            foundPos = False
            foundInitMark = False
            foundLog = False
            initMark = []  
            
            cpnTree = et.parse(filename, parser)    
            
            place = None
            
            actualSubnet = ""

            for idx, element in enumerate( cpnTree.getroot().iter("*") ) :                
#                 print(element, element.tag, element.text)
                if lastConnection is not None:
                    serConnections.append( [actualSubnet, lastConnection] )                     
                    lastConnection = None
                
                if idx is 0:
                    netName = element.text 
                                    
                if str( element.tag ) == str("SubnetName"):
                    actualSubnet = element.text
                        
                    subnets.append( actualSubnet )
                
                if str( element.tag ) == str("Place"):
                    if not foundPlace:  
                        foundPlace = True
                        place = []         
                    else:                  
                        foundInitMark = False
                        place.append(initMark)
                        serPlaces.append( [actualSubnet, place] )
                        place = []         
                        
                if str( element.tag ) == str("Transition"):
                    if not foundPlace:  
                        if not foundTransition:  
                            foundTransition = True
                            transition = []                          
                        else:   
                            serTransitions.append( [actualSubnet, transition] )
                            transition = []      
                    else:       
                        foundPlace = False
                        foundInitMark = False
                        place.append(initMark)
                        serPlaces.append( [actualSubnet, place] )
                        foundTransition = True
                        transition = [] 
                        
                if str( element.tag ) == str("Connection"):
                    if not foundTransition:  
                        if not foundConnection:  
                            foundConnection = True
                            connection = []                          
                        else:   
                            serConnections.append( [actualSubnet, connection] )  
                            connection = []                      
                    else:   
                        foundTransition = False
                        serTransitions.append( [actualSubnet, transition] )
                        foundConnection = True
                        connection = []         
                    
                if "uniqueName" in element.tag:
                    if foundConnection and not foundTransition and not foundPlace:
                        if "SRC" in element.tag:
                            connection.append( element.text )
                        elif "DST" in element.tag:
                            connection.append( element.text )
                    else:
                        if foundPlace and not foundTransition and not foundConnection:
                            place.append( element.text )
                        if foundTransition and not foundPlace and not foundConnection:
                            transition.append( element.text )
                        
                if str( element.tag ) == str("name"):
                    if foundPlace and not foundTransition and not foundConnection:
                        place.append( element.text )
                    if foundTransition and not foundPlace and not foundConnection:
                        transition.append( element.text )
                    if foundConnection and not foundPlace and not foundTransition:
                        connection.append( element.text )
                        
                if str( element.tag ) == str("sourceConnector") and foundConnection:
                    connection.append( element.text )
                        
                if str( element.tag ) == str("destinationConnector") and foundConnection:
                    connection.append( element.text )
                    lastConnection = connection
                    foundConnection = False
                                        
                if str( element.tag ) == str("portClone") and foundPlace:
                    place.append( element.text )
                    
                if str( element.tag ) == str("port") and foundPlace:
                    place.append( element.text )
                    
                if str( element.tag ) == str("pos"):
                    pos = []
                    foundPos = True
                if str( element.tag ) == str("x") and foundPos:
                    if foundPlace or foundTransition:
                        pos.append( element.text )
                if str( element.tag ) == str("y") and foundPos:
                    if foundPlace or foundTransition:
                        pos.append( element.text )
                        if foundPlace:
                            place.append(pos)
                        if foundTransition:
                            transition.append(pos)
                        foundPos = False
                    
                if str( element.tag ) == str("initMarking") and foundPlace:
                    foundInitMark = True
                    initMark = []                    
                if "token" in element.tag and foundInitMark and foundPlace:
                    initMark.append( element.text )   
                       
                if str( element.tag ) == str("guardExpression") and foundTransition:
                    transition.append( element.text )
                    
                if str( element.tag ) == str("subnet") and foundTransition:
                    transition.append( element.text )
                    
                if str( element.tag ) == str("Log"):
                    foundLog = True
                    
            if not foundLog:            
                serConnections.append( [actualSubnet, lastConnection] )
            return [ netName, subnets, serConnections, serPlaces, serTransitions ]
            
        except et.XMLSyntaxError:
            logging.debug( "XML Parse Error %s" %( str( sys.exc_info()[1] ) ) )
            return [ netName, subnets, serConnections, serPlaces, serTransitions ]
                
    #------------------------------------------------------------------------------------------------
    
    
    
    
    
    
    
    
    
    def netToXML(self, subnet, placesS, transitionsS, connectionsS):
        '''Save Colored Petrinet **Subnet** to XML tree. 
        
        :param subnet: Subnet name.
        :param placesS: Place contained in `subnet`.
        :param transitionsS: Transitions contained in `subnet`.
        :param connectionsS: Connections contained in `subnet`.
        '''
        
        subnetName = et.SubElement(self.cpn, "SubnetName")
        subnetName.text = str( subnet )
        
        serPlaces = []  
            
        for place in placesS: 
            
            if place.portClone is None and str(place.portDirection) != str("None") and ("i" in place.portDirection or "o" in place.portDirection):
                place.portClone = place.uniqueName
                marking = None
            else:
                if isinstance( place.initMarking, deque ):
                    marking = list( place.initMarking )
                else:                          
                    marking = place.initMarking 
                place.portClone = None
                                 
                
            serPlaces.append( 
                                 [
                                 place.name, 
                                 [place.scenePos().x(), place.scenePos().y()], 
                                 marking,
                                 place.uniqueName,
                                 place.portDirection,
                                 place.portClone
                                 ]
                             )
      
        serTransitions = []   
        for transition in transitionsS:
            serTransitions.append( 
                                    [
                                     transition.name, 
                                     [transition.scenePos().x(), transition.scenePos().y()], 
                                     transition.guardExpression if not transition.substitutionTransition else "None",
                                     transition.uniqueName,
                                     transition.subnet if transition.substitutionTransition else "None"
                                     ]
                                  )
            
        serConnections = []        
        for connection in connectionsS:
            serConnections.append(
                                    [
                                     connection[0].parent.uniqueName,
                                     connection[2].parent.uniqueName,
                                     connection[1].name,
                                     connection[3],
                                     connection[4]               
                                     ]
                                  )
            
        for p in serPlaces:
            place = et.SubElement(subnetName, "Place")
            uN = et.SubElement(place, "uniqueName")
            uN.text = p[3]
            na = et.SubElement(place, "name")
            na.text = p[0]
            nc = et.SubElement(place, "portClone")
            nc.text = str( p[5] )
            nc = et.SubElement(place, "port")
            nc.text = str( p[4] )
            pos = et.SubElement(place, "pos")
            posx = et.SubElement(pos, "x")
            posx.text = str(p[1][0])
            posy = et.SubElement(pos, "y")
            posy.text = str(p[1][1])
            inMark = et.SubElement(place, "initMarking")
            if isinstance(p[2], list):
                for idx, iM in enumerate(p[2]):
                    if str( iM ) != str("None") and iM is not None:
                        _iM = et.SubElement(inMark, "token%d"%idx)
                        _iM.text = str(iM)
            else:
                if p[2] is not None:
                    _iM = et.SubElement(inMark, "token0")
                    _iM.text = str(p[2])                
            
        for t in serTransitions:
            transition = et.SubElement(subnetName, "Transition")
            uN = et.SubElement(transition, "uniqueName")
            uN.text = t[3]
            na = et.SubElement(transition, "name")
            na.text = t[0]
            pos = et.SubElement(transition, "pos")
            posx = et.SubElement(pos, "x")
            posx.text = str(t[1][0])
            posy = et.SubElement(pos, "y")
            posy.text = str(t[1][1])
            guEx = et.SubElement(transition, "guardExpression")
            guEx.text = t[2]            
            guEx = et.SubElement(transition, "subnet")
            guEx.text = str( t[4] )
                        
        for c in serConnections:
            connection = et.SubElement(subnetName, "Connection")
            src = et.SubElement(connection, "uniqueNameSRC")
            src.text = c[0]
            dst = et.SubElement(connection, "uniqueNameDST")
            dst.text = c[1]
            na = et.SubElement(connection, "name")
            na.text = c[2]
            na = et.SubElement(connection, "sourceConnector")
            na.text = "%d"%c[3]
            na = et.SubElement(connection, "destinationConnector")
            na.text = "%d"%c[4]            
    #------------------------------------------------------------------------------------------------
    
    def saveLog(self, logList):
        '''Save Log Entries to XML tree.
        
        :param logList: List of log entries from the log widget.
        '''
        
        subnetName = et.SubElement(self.cpn, "Log")
        for logItem in logList:
            na = et.SubElement(subnetName, "Line")
            na.text = logItem
    #------------------------------------------------------------------------------------------------
        
    
    def saveNet(self, filename):        
        '''Save XML tree to file.
        
        :param filename: Filepath where the XML tree is saved. 
        '''
        doctype = """<!DOCTYPE ColouredPetriNet SYSTEM "ColouredPetriNet.dtd">"""        
        with et.xmlfile(filename, encoding='utf-8') as xf:
            xf.write_declaration(standalone=False)
            xf.write_doctype(doctype)
            tree = et.ElementTree(self.cpn)
            xf.write(tree.getroot())
        
        pass
    #------------------------------------------------------------------------------------------------