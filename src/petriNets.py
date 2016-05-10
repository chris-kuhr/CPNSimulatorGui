'''
Created on Mar 10, 2016

@author: christoph
'''

from PyQt4 import QtCore, QtGui, QtSvg
import sys, os, time
from time import gmtime, strftime

import argparse
import logging

from gui.MainWindow import MainWindow 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", help="set log level to: DEBUG, INFO, WARNING. default: off")
    
    app = QtGui.QApplication(sys.argv)
    workingDir = os.path.dirname(os.path.realpath(__file__))
    
    args = parser.parse_args()
    if args.log is not None:
        numeric_level = getattr(logging, args.log.upper()) 
    else:
        numeric_level = 0
        
    logging.basicConfig(level=numeric_level, filename='%s/output/log/%s.log'%(workingDir, str(strftime("%Y_%m_%d_%H_%M_%S", gmtime()))))
    
    ui = MainWindow( workingDir)    
    sys.exit(app.exec_())