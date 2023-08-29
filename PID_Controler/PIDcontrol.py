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

        # Style simple pour l'appel du constructeur de la classe de base :
        super().__init__()

        # Gestion des répertoires statiques
        if not os.path.isdir(PIDcontrol.icone_dir) :
            print("Répertoire des icônes non trouvé.")
            
        # *** Good practices  ***
        # Define in the constructor the persisted data as attributes, 
        # and if we don't know their value at this time we can use 'None'.

        ### Attributs (objets persistants)
        self.menubar = self.menuBar() # indispensable pour Mac

        ### Le gestionnaire d'onglets :
        self.tabs = QTabWidget()
        
        ### Les onglets de l'applications :        
        self.monitor_tab = Monitor(self)
        self.plotter_tab = Plotter(self)
        
        ### Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusText = QLabel(self)
        self.statusBar().addWidget(self.statusText)

        self.__initUI()   # Initialisation de l'interface utilisateur
        self.show()       # Affichage (hérité de la classe de base)

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
           
    def LoadCSV_File(self):
        '''
        Load data previously saved in a CSV file
        '''
    
    def LoadConfigFile(self):
        pass
    
    def clearPlots(self):
        pass
        #self.onePlotTab.ClearAxes()
        #self.twoPlotsTab.ClearAxes()

    def center(self):
        '''Pour centrer la fenêtre dans l'écran'''
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

        
    def closeEvent(self, event):        
        '''
        redefinition of the closedEvent method, inherited from QWidget,
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
        