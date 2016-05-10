from PyQt4 import QtGui, QtCore, QtSvg, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from collections import Counter, deque
import logging


import snakes.plugins
from snakes.nets import *

from gui.NameDialog import NameDialog
# 
from model.PlaceItem import PlaceItem
from model.TransitionItem import TransitionItem
from model.TokenItem import TokenItem
from model.PortItem import PortItem
from model.ArcItem import ArcItem


class CPNSimulator():
    '''CPN Simulator.
    
    :member mainWindow: `gui.MainWindow`. Main application window.
    :member net: SNAKES Colored Petrinet.  
    :member markingHistory: SNAKES Marking stored for every ` simulationStep`.
    :member simulationStep: Steps calculated for the Petrinet `net`
    :member displayStep: Step displayed in editors.
    :member simulatorSpeed: The speed with which the simulator progresses. 
    :member enabledTransitions: Number of enabled transitions.
    :member uniqueNameBase: Unique integer for the creation of new CPN elements. 
    :member initialMarking: SNAKES Marking at step 0. 
    :member colourSets: Set of defined string colors.  
    :member connectionList: List of all `model.ArcItem` s, except port substitution transition connections.   
    :member transitions: All `model.TransitionItem` except substitution transitions.  
    :member places: All `model.PlaceItem` except port places.  
    :member subnets: List of all subnets.  
    
    '''
    def __init__(self, mainWindow):
        '''Create CPN Simulator.
        
        :param mainWindow: `gui.MainWindow`. Main application window.
        '''
        self.mainWindow = mainWindow
        self.markingHistory = []
        self.simulationStep = 0
        self.displayStep = 0
        self.simulatorSpeed = 2000  
        self.enabledTransitions = 0    
        self.uniqueNameBase = 0   
                
        self.net = PetriNet("init")  
        self.initialMarking = None
        self.colourSets = set()
        self.connectionList = []
        self.transitions = []
        self.places = []        
        self.subnets = []
    #--------------------------------------------------------------------------
            
        
    def tokenAdded(self):    
        '''Called when a `model.TokenItem` was added to the `net`.'''
        self.markingHistory[self.displayStep] = self.net.get_marking() 
        self.getActualMarking( self.markingHistory[self.displayStep] ) 
    #------------------------------------------------------------------------------------------------
    
    
    def defineNewColour(self, colName):
        '''Define a new Color.
        
        :param colName: String color.
        '''
        if str( colName ) not in self.colourSets:
            self.colourSets.add( str( colName ) )
            for editor in self.mainWindow.editors:
                editor.colorListWidget.insertItem( editor.colorListWidget.count()-1, QtGui.QListWidgetItem( str( colName ) ) )
                editor.colorListItems.insert( len( editor.colorListItems), str( colName ) )
        else:
            errorString = str( "Colour Set already defined!" )
            item = QtGui.QListWidgetItem( errorString )
            item.setTextColor(QtCore.Qt.yellow)
            self.mainWindow.logWidget.addItem( item )
            
    #------------------------------------------------------------------------------------------------
    
    def setNetName(self):   
        '''Set the name of the `net`.'''
        for editor in self.mainWindow.editors:
            if editor != self.mainWindow.editors[0]:
                self.mainWindow.editors.remove(editor)
            else:                    
                editor.diagramScene.clear()
                
        self.net = PetriNet( self.mainWindow.diag.getName() )
        actualMarking = self.net.get_marking()
        self.markingHistory.append( actualMarking )
        self.mainWindow.setWindowTitle("pyPetriNets - %s"%( str(self.net) ) )
        del self.mainWindow.diag  
    #------------------------------------------------------------------------------------------------
    
    
    def resetSimulator(self, init=False):
        '''Reset simulator history to step 0.
        
        :param init: Initialization on startup/load
        '''
        self.simulationStep = 0
        self.displayStep = 0
        self.markingHistory = []
        
        self.net.set_marking( self.initialMarking )                
                
        actualMarking = self.net.get_marking()
        self.markingHistory.append( actualMarking )
        
        if not init:
            self.mainWindow.logWidget.clear()
        self.mainWindow.lineEdit.setText( "%d/%d"%( self.displayStep, self.simulationStep ) )
        self.back2beginning()
    #------------------------------------------------------------------------------------------------
    
    
    def startSim(self):
        '''Start simulator with the speed chosen with the radio edit.'''
        if self.mainWindow.pushButton_4.isDown():
            if self.mainWindow.pushButton_4.isChecked():
                self.mainWindow.pushButton_4.setChecked(False)
            else:  
                if self.mainWindow.radioButton.isChecked() == True:
                    self.simulatorSpeed = 5000         
                elif self.mainWindow.radioButton_2.isChecked() == True:
                    self.simulatorSpeed = 2000
                elif self.mainWindow.radioButton_3.isChecked() == True:
                    self.simulatorSpeed = 500       
                self.getActualMarking( self.markingHistory[ self.displayStep ] )  
                self.mainWindow.timer.start(self.simulatorSpeed)
    #-------------------------------------------------------------------
        
        
    def stopSim(self):
        '''Stop simulator.'''
        if self.mainWindow.pushButton_4.isChecked() and not self.mainWindow.pushButton_4.isDown():
            self.mainWindow.pushButton_4.setChecked(False)
        self.mainWindow.timer.stop()
    #-------------------------------------------------------------------
              
            
    def back2beginning(self):
        '''Return to step 0.'''
        self.displayStep = 0
        self.net.set_marking( self.markingHistory[self.displayStep] )
        self.getActualMarking( self.markingHistory[ self.displayStep ] )
        self.mainWindow.lineEdit.setText( "%d/%d"%( self.displayStep, self.simulationStep ) )
    #-------------------------------------------------------------------
    
    
    def backStep(self):
        '''Go one step back in history.'''
        if self.displayStep > 0:            
            self.displayStep -= 1
            self.net.set_marking( self.markingHistory[self.displayStep] )
            self.getActualMarking( self.markingHistory[ self.displayStep ] )
        self.mainWindow.lineEdit.setText( "%d/%d"%( self.displayStep, self.simulationStep ) )
    #-------------------------------------------------------------------
    
    
    def forward2lastStep(self):        
        '''Go forward to last step in history, given at ` simulationStep`.'''
        self.displayStep = self.simulationStep
        self.net.set_marking( self.markingHistory[self.displayStep] )
        self.getActualMarking( self.markingHistory[ self.displayStep ] )
        self.mainWindow.lineEdit.setText( "%d/%d"%( self.displayStep, self.simulationStep ) )
    #-------------------------------------------------------------------
    
    
    def forwardStep(self):
        '''Go step forward in history or claculate new step.'''
        if self.displayStep < self.simulationStep:
            self.displayStep += 1
            self.net.set_marking( self.markingHistory[self.displayStep] )
            self.getActualMarking( self.markingHistory[ self.displayStep ] )
        else:
            self.simulationStep += 1
            self.fireEnabledTransitions(self.simulationStep)
            
            if self.markingHistory[ self.simulationStep -1] == self.net.get_marking() and self.enabledTransitions == 0:
                self.net.set_marking( self.markingHistory[ self.simulationStep -1 ] )
                self.getActualMarking( self.markingHistory[ self.simulationStep -1 ] )  
                self.stopSim()
                self.simulationStep -= 1
                self.displayStep = self.simulationStep
            else:
                self.displayStep = self.simulationStep                
                self.markingHistory.append( self.net.get_marking() )  
                self.getActualMarking( self.markingHistory[ self.displayStep ] )

        self.mainWindow.lineEdit.setText( "%d/%d"%( self.displayStep, self.simulationStep ) )
    #-------------------------------------------------------------------
    
    
    def checkTranistionActivation(self, transition, mode, currentStep):
        '''Check whether a SNAKES transition is activated.
        
        :param transition: SNAKES transition to check.
        :param mode: SNAKES mode to check for activation. 
        :param currentStep: Step for which to calculate the activation
        :return activated: Activated True or False.
        '''
        activated = False
        transition.setBrush(QtGui.QBrush(QtCore.Qt.white))
        try:       
            activated = self.net.transition( transition.uniqueName ).activated( mode )
            transition.exceptionString = ""
            transition.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            transition.setBrush(QtGui.QBrush(QtCore.Qt.white))
        except NameError: 
            transition.exceptionString = "Step %d transition %s ACTIVATE Name Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
            item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
            item.setTextColor(QtCore.Qt.red)
            self.mainWindow.logWidget.addItem( item )
            transition.setBrush(QtGui.QBrush(QtCore.Qt.darkRed))
            pass
        except snakes.DomainError: 
            transition.exceptionString = "Step %d transition %s ACTIVATE Domain Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
            item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
            item.setTextColor(QtCore.Qt.red)
            self.mainWindow.logWidget.addItem( item )
            transition.setBrush(QtGui.QBrush(QtCore.Qt.darkRed))
            pass
        except TypeError: 
            transition.exceptionString = "Step %d transition %s ACTIVATE Type Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
            item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
            item.setTextColor(QtCore.Qt.red)
            self.mainWindow.logWidget.addItem( item )  
            transition.setBrush(QtGui.QBrush(QtCore.Qt.darkRed))              
            pass
        
        return activated
    #-------------------------------------------------------------------
        
        
    def checkTransitionEnabled(self, transition, mode, currentStep, activated, transitions2Fire):    
        '''Check whether a SNAKES transition is enabled.
        
        :param transition: SNAKES transition to check.
        :param mode: SNAKES mode to check for activation. 
        :param currentStep: Step for which to calculate the enabling.
        :param activated: Flag that determines, whether `transition` is activated.
        :param transitions2Fire: List of SNAKES transitions enabled to fire.
        :return enabled: Enabled True or False.
        '''
        enabled = False
        if activated:
            transition.exceptionString = ""
            try:
                enabled = self.net.transition( transition.uniqueName ).enabled( mode ) 
                transition.exceptionString = ""
                transition.setPen(QtGui.QPen(QtCore.Qt.green, 4))
            except NameError: 
                transition.exceptionString = "Step %d transition %s ENABLE Name Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transition.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass
            except snakes.DomainError: 
                transition.exceptionString = "Step %d transition %s ENABLE Domain Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transition.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass
            except TypeError: 
                transition.exceptionString = "Step %d transition %s ENABLE Type Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transition.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass
            
            if enabled:
                if not [transition.uniqueName, mode] in transitions2Fire: 
                    transitions2Fire.append( [transition, mode] )
        return enabled
    #-------------------------------------------------------------------
        
        
    def fireEnabledTransitions(self, currentStep):  
        '''Fire transitions in list `transitions2Fire`.
        
        :param currentStep: Step for which to calculate the firing.
        '''
        self.transitions2Fire = []         
                
        for transition in self.transitions:     
            enabled = False
            activated = False
            transition.exceptionString = ""
            transition.modeString = ""
            try:       
                for mode in self.net.transition( transition.uniqueName ).modes():
                    activated = self.checkTranistionActivation( transition, mode, currentStep )
                    enabled = self.checkTransitionEnabled( transition, mode, currentStep, activated, self.transitions2Fire) 
                
#                 if not enabled or not activated:
#                     for inputArc in self.net.transition( transition.uniqueName ).input():
#                         for place in inputArc:
#                             activated = self.checkTranistionActivation( transition, place.mode, currentStep )
#                             enabled = self.checkTransitionEnabled( transition, mode, currentStep, activated, self.transitions2Fire) 
                        
                        
            except NameError: 
                transition.exceptionString = "Step %d transition %s Mode Name Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transition.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass
            except snakes.DomainError: 
                transition.exceptionString = "Step %d transition %s Mode Domain Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transition.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass
            except TypeError: 
                transition.exceptionString = "Step %d transition %s Mode Type Error %s"%( currentStep,  transition.uniqueName, sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( transition.exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transition.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass                
                         
        for transFire in self.transitions2Fire:
            item = QtGui.QListWidgetItem( str( "FIRE transition %s for Substitution %s"%(transFire[0].uniqueName, transFire[1]) ) )
            item.setTextColor(QtCore.Qt.green)
            self.mainWindow.logWidget.addItem( item )
            exceptionString = ""
            try:
                self.net.transition( transFire[0].uniqueName ).fire( transFire[1] )
            except snakes.DomainError: 
                exceptionString = "Step %d FIRE %s Domain Error activated %s"%( currentStep, transFire[0].uniqueName,  sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transFire[0].exceptionString = exceptionString
                transFire[0].setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass        
            except TypeError: 
                exceptionString = "Step %d FIRE %s Type Error activated %s"%( currentStep, transFire[0].uniqueName,  sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transFire[0].exceptionString = exceptionString
                transFire[0].setPen(QtGui.QPen(QtCore.Qt.red, 4))
                pass
            except ValueError: 
                exceptionString = "Step %d FIRE %s Value Error not enabled for %s"%( currentStep, transFire[0].uniqueName,  sys.exc_info()[1])
                item = QtGui.QListWidgetItem( str( exceptionString ) )
                item.setTextColor(QtCore.Qt.red)
                self.mainWindow.logWidget.addItem( item )
                transFire[0].exceptionString = exceptionString
                transFire[0].setPen(QtGui.QPen(QtCore.Qt.red, 4))
             
        for place in self.places:
            for token in place.tokens:
                if "None" in str( token ):
                    place.tokens.remove(token)
                break
            
    #-----------------------------------------------------------------------------------------------
     
        
        
        
        
        
#     """
#                             IN PROGRESS CHECK FOR EMPTY PLACES IN EXPRESSION
#     """
#     def checkForEmptyness(self, connection): 
#         for connection2 in self.connectionList: 
#             if connection[0] == connection2[2]:                    
#                 evaluatedString = ""
#                 splitted = str( connection[1].name ).split()
#                 lengthSplitted = len( splitted )
# #                     if lengthSplitted < 5:
#                 for idx, word in enumerate( splitted ):
#                     if "if" in word:
#                         if str( splitted[idx+1].split("==")[0] ) == str( connection2[1].name ) or\
#                                     str( splitted[idx+1].split("!=")[0] ) == str( connection2[1].name ):    
#                             if "[]" in splitted[idx+1] and "==" in splitted[idx+1]:
#                                 print( connection[1].name )       
#                                 if connection2[0].place.is_empty():
#                                     print("place is empty1", connection2[0].uniqueName, splitted[idx-1] )
#                                     return connection2, splitted[idx-1]
#                                 else:
#                                     print("place is not empty1", connection2[0].uniqueName, splitted[idx+3] )
#                                     return connection2, splitted[idx+3]
#                                                             
#                             elif "[]" in splitted[idx+1] and "!=" in splitted[idx+1]:
#                                 print( connection[1].name )       
#                                 if not connection2[0].place.is_empty():
#                                     print("place is not empty2", connection2[0].uniqueName, splitted[idx-1] )
#                                     return connection2, splitted[idx-1] 
#                                 else:
#                                     print("place is empty2", connection2[0].uniqueName, splitted[idx+3] )
#                                     return connection2, splitted[idx+3] 
#         return None
#                                 
#                                 
#     #-------------------------------------------------------------------
    def getActualMarking(self, actualMarking):     
        '''Process status of visual net, depending on `actualMarking`.
        
        :param actualMarking: SNAKES Marking.
        '''
        infoString = str( "Step %d %s"%(self.displayStep, actualMarking) )
        item = QtGui.QListWidgetItem( infoString )
        item.setTextColor(QtCore.Qt.black)
        self.mainWindow.logWidget.addItem( item )
#         logging.warning( infoString )
        
        for subnetEditor in self.mainWindow.editors:
#             logging.debug( subnetEditor.visualConnectionList )
            subnetEditor.setTokens(actualMarking)                
            
            for place in subnetEditor.visualPlaces:
                place.stackTokens()
#                 place.findItemsInPlanes()
                
        self.enabledTransitions = 0
                       
        for connection in self.connectionList: 
#             logging.debug( "%s %s %s"%(connection[0], connection[1], connection[2] ) )
            if isinstance(connection[2], TransitionItem):
                connection[2].exceptionString = ""
                connection[2].modeString = ""
                for connectionPre in self.connectionList:
                    if connectionPre[0] == connection[2]:
                        enabled = False       
                        activated = False         
                        removedInput = None    
#                         connection[2].setBrush(QtGui.QBrush(QtCore.Qt.lightGray)) 
                        connection[2].setPen(QtGui.QPen(QtCore.Qt.black, 2))       
                        
                        connection[2].exceptionString = ""
                        
                                
                        try:
                            connection[2].modeString = ""
                            for mode in self.net.transition( connection[2].uniqueName ).modes():  
                                connection[2].modeString += "Mode: %s\n"%( str( mode ).replace( "{", "" ).replace( "}", "" ) )
                                if not activated:
                                    activated = self.net.transition( connection[2].uniqueName ).activated( mode )       
#                                     connection[2].setBrush(QtGui.QBrush(QtCore.Qt.white))                                
                                if not enabled: 
                                    enabled = self.net.transition( connection[2].uniqueName ).enabled( mode )
                                    connection[2].setPen(QtGui.QPen(QtCore.Qt.green, 4))
                        except KeyError:                                
                            connection[2].exceptionString = "Key Error: Node %s - Token %s"%( connection[2].name, sys.exc_info()[1])
                            item = QtGui.QListWidgetItem( str( connection[2].exceptionString ) )
                            item.setTextColor(QtCore.Qt.red)
                            self.mainWindow.logWidget.addItem( item )
#                             logging.warning( connection[2].exceptionString )
                            connection[2].setPen(QtGui.QPen(QtCore.Qt.red, 4))
                            pass      
                        except snakes.DomainError:
                            connection[2].exceptionString = "Domain Error: Node %s - Token %s"%( connection[2].name, sys.exc_info()[1])
                            item = QtGui.QListWidgetItem( str( connection[2].exceptionString ) )
                            item.setTextColor(QtCore.Qt.red)
                            self.mainWindow.logWidget.addItem( item )
#                             logging.warning( connection[2].exceptionString )
                            connection[2].setPen(QtGui.QPen(QtCore.Qt.red, 4))
                            pass      
                        except NameError: 
                            connection[2].exceptionString = "Name Error: Node %s - %s"%( connection[2].name, sys.exc_info()[1])
                            item = QtGui.QListWidgetItem( str( connection[2].exceptionString ) )
                            item.setTextColor(QtCore.Qt.red)
                            self.mainWindow.logWidget.addItem( item )
#                             logging.warning( connection[2].exceptionString )
                            connection[2].setPen(QtGui.QPen(QtCore.Qt.red, 4))
                            pass
                        
                        
                        if enabled:
                            self.enabledTransitions += 1
                        connection[2].enabled = enabled
                        break 
                    
        for subnetEditor in self.mainWindow.editors:
#             logging.debug( subnetEditor.visualConnectionList )
            subnetEditor.setTokens(actualMarking)                
            
            for place in subnetEditor.visualPlaces:
                place.stackTokens()
                place.findItemsInPlanes()
            
            for transition in subnetEditor.visualTransitions:
                transition.findItemsInPlanes()
                if transition.enabled:   
                    transition.setInfoString( transition.modeString )
                    transition.setPen(QtGui.QPen(QtCore.Qt.green, 4))
                elif transition.exceptionString != "":                  
                    transition.setInfoString( transition.exceptionString )
                    transition.setPen(QtGui.QPen(QtCore.Qt.red, 4))
                else:
                    transition.setInfoString( transition.modeString )
                    transition.setPen(QtGui.QPen(QtCore.Qt.black, 2))
                            

    #-----------------------------------------------------------------------------------------------
    
    
#===========================================================================================================