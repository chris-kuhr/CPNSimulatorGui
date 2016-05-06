'''
Created on Mar 10, 2016

@author: christoph
'''

from PyQt4 import QtCore, QtGui, QtSvg
import sys, os, time
from time import gmtime, strftime

import logging

from gui.MainWindow import MainWindow 

if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    workingDir = os.path.dirname(os.path.realpath(__file__))
    
    logging.basicConfig(level=logging.DEBUG)#, filename='%s/output/log/%s.log'%(workingDir, str(strftime("%Y_%m_%d_%H_%M_%S", gmtime()))))
    ui = MainWindow( workingDir)    
    sys.exit(app.exec_())