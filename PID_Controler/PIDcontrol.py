__author__      = "Jean-Luc CHARLES, aka JLC"
__copyright__   = "Copyright 2023"
__license__     = "GPL3"
__version__     = "1.0.1"
__date__        = "2023/07/23"
__maintainer__  = "JLC"
__email__       = "jean-luc.charles@mailo.com"

import numpy as np
import os, platform

try:
    from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QStatusBar,
                                 QLabel, QMessageBox)
    from PyQt5.QtGui import QIcon, QGuiApplication
except:
    from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar,
                                 QLabel, QMessageBox)
    from PyQt6.QtGui import QIcon, QGuiApplication, QAction

from Monitor import Monitor
from Plotter import Plotter

class PIDcontrol(QMainWindow):

    icone_dir   = "icones"
    cur_dir     = os.getcwd()+"/"        # Répertoire de travail
    image_dir   = os.getcwd()+"/images/" # Dossier des images
    image_fmt     = "image{:04d}.png"    # Nom automatique des images
                                         # (rectifié dans la version 1.4)
    
    def __init__(self):

        # call the base class constructor:
        super().__init__()

        # Managing static directories:
        if not os.path.isdir(PIDcontrol.icone_dir) :
            print("Icon directory not found.")
            
        # *** Good practices  ***
        # Define in the constructor the persisted data as attributes, 
        # and if we don't know their value at this time we can use 'None'.

        ### Attributs (persistant data)
        self.menubar = self.menuBar() # indispensable pour Mac

        ### the tab manager: :
        self.tabs = QTabWidget()
        
        ### The tabs of the application :        
        self.monitor_tab = Monitor(self)
        self.plotter_tab = Plotter(self)
        
        ### Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusText = QLabel(self)
        self.statusBar().addWidget(self.statusText)

        self.__initUI()   # initialize the GUI
        self.show()       # Display the screnn

    def __initUI(self):
        '''
        Mettre en place les éléments de l'interface graphique
        '''
        
        print("PIDcontrol.__initUI")
        self.resize(800, 600)
        self.center()
        self.setWindowTitle('PID controler')
        self.statusBar()  # Activate status bar
        
        self.tabs.addTab(self.monitor_tab, "Monitor")
        self.tabs.addTab(self.plotter_tab, "Plotter")
        
        self.setCentralWidget(self.tabs)

        ### Menus
        if platform.uname().system.startswith('Darw') :
            # programme exécuté sur une plateforme Apple :
            self.menubar.setNativeMenuBar(False)

        ##### The menu 'File'
        file_menu = self.menubar.addMenu('File')
        
        ### Quit :
        qa = QAction(QIcon(PIDcontrol.icone_dir+'/exit.png'),\
                          'Quit', self)
        qa.setShortcut('Ctrl+Q')
        qa.setStatusTip("Quit the application")
        qa.triggered.connect(self.Close)
        file_menu.addAction(qa)
        
        ##### The menu 'Flags'
        flag_menu = self.menubar.addMenu('Flags')
        
        ### Display serial data :
        qa = QAction('Display serial data', self)
        qa.setShortcut('Ctrl+D')
        qa.setStatusTip("Display the serial data in the monitor tab")
        qa.triggered.connect(self.DisplaySerialData)
        qa.setCheckable(True)
        qa.setChecked(True) 
        flag_menu.addAction(qa)
           
    def LoadCSV_File(self):
        '''
        Load data previously saved in a CSV file
        '''
        pass
    
    def LoadConfigFile(self):
        pass
    
    def clearPlots(self):
        pass
        #self.onePlotTab.ClearAxes()
        #self.twoPlotsTab.ClearAxes()

    def center(self):
        '''To center the xindow on the screen'''
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

        
    def closeEvent(self, event):        
        '''
        Redefinition of the closedEvent method, inherited from QWidget,
        connected to the QWidget event.QCloseEvent ("closed)
        the window")
        '''        
        rep = QMessageBox.question(self,        
            'Message',                          # bar title
            "Do you realy want to quit ?",      # text in the pop up window
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,   # butons 'Yes' & 'No'
            QMessageBox.StandardButton.No)                     # 'No' is the default
        if rep == QMessageBox.StandardButton.Yes:
            event.accept() 
        else:
            event.ignore() 
    
    def Close(self):        
        '''
        Send a message Box to confirm the click on the Quit button
        '''        
        rep = QMessageBox.question(self,        
            'Message',                          # bar title
            "Do you realy want to quit ?",      # text in the pop up window
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,   # butons 'Yes' & 'No'
            QMessageBox.StandardButton.No)                     # 'No' is the default
        if rep == QMessageBox.StandardButton.Yes:
            self.close()
        
    def DisplaySerialData(self, status):
        
        monitor = self.monitor_tab
        grid = monitor.layout()
            
        if status == False:
            item = grid.itemAtPosition(1,0)
            widget = item.widget()
            grid.removeWidget(widget)
            widget.setVisible(False)
            
            item = grid.itemAtPosition(1,1)
            widget = item.widget()
            grid.removeWidget(widget)
            
            grid.addWidget(monitor.graph_widget, 1, 0, 1, 2)
            
        else:            
            item = grid.itemAtPosition(1,0)
            widget = item.widget()
            grid.removeWidget(widget)
                        
            grid.addWidget(monitor.serial_view, 1, 0)
            grid.addWidget(monitor.graph_widget, 1, 1)
            monitor.serial_view.setVisible(True)
            monitor.graph_widget.setVisible(True)