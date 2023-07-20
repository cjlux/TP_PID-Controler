#=========================================================================
# # version 1.0 -- 2023/07/06 -- by JLC
#=========================================================================
import numpy as np
import os, sys, platform

from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QAction, QStatusBar,
                             QLabel, QMessageBox)

from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtWidgets

from SerialPlotter import SerialPlotter
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

        if not os.path.isdir(PIDcontrol.image_dir) :
            msg = "Répertoire des images créés :\n\t'{}'"
            print(msg.format(PIDcontrol.image_dir))
            os.mkdir(PIDcontrol.image_dir)

        # *** Bonnes pratiques  ***
        #   Définir dans le constructeur les données persistantes en tant 
        #   qu'attributs, et si on ne connaît pas leur valeur à ce moment 
        #   on peut utiliser None

        ### Attributs (objets persistants)
        self.menubar = self.menuBar() # indispensable pour Mac

        ### Le gestionnaire d'onglets :
        self.tabs = QTabWidget()
        
        ### Les onglets de l'applications :        
        self.serialPlotter_tab = SerialPlotter(self)
        self.plotter_tab       = Plotter(self)
        
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
        self.resize(800, 600)
        self.center()
        self.setWindowTitle('PID controler')
        self.statusBar()  # Activate status bar
        
        self.tabs.addTab(self.serialPlotter_tab, "Serial controler")
        self.tabs.addTab(self.plotter_tab, "Data processing")
        
        self.setCentralWidget(self.tabs)

        ### Menus
        if platform.uname().system.startswith('Darw') :
            # programme exécuté sur une plateforme Apple :
            self.menubar.setNativeMenuBar(False)

        ##### The menu 'File'
        file_menu = self.menubar.addMenu('File')

        ### Load a CSV file :
        qa = QAction(QIcon(PIDcontrol.icone_dir+'/open.png'),
                           "Load CSV", self)
        qa.setShortcut('Ctrl+O')
        qa.setStatusTip('Loads a data file ...')
        # connexion with the 'open_config_file':
        qa.triggered.connect(self.LoadCSV_File)
        file_menu.addAction(qa)
        
        ### Quit :
        qa = QAction(QIcon(PIDcontrol.icone_dir+'/exit.png'),\
                          'Quit', self)
        qa.setShortcut('Ctrl+Q')
        qa.setStatusTip("Quit the application")
        qa.triggered.connect(self.Close)
        file_menu.addAction(qa)
          
        ##### The menu 'Config'
        conf_menu = self.menubar.addMenu('Config')

        ### Load a config file :
        qa = QAction(QIcon(PIDcontrol.icone_dir+'/open.png'),
                           "Load a config file", self)
        qa.setShortcut('Ctrl+C')
        qa.setStatusTip('Loads a configuration file ...')
        # connexion with the 'LoadConfigFile' method:
        qa.triggered.connect(self.LoadConfigFile)
        conf_menu.addAction(qa)
   
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
        desktop = QApplication.desktop()
        n = desktop.screenNumber(self.cursor().pos())
        screen_center = desktop.screenGeometry(n).center()
        geo_window = self.frameGeometry()
        geo_window.moveCenter(screen_center)
        self.move(geo_window.topLeft())
        
    def closeEvent(self, event):        
        '''
        redefinition of the closedEvent method, inherited from QWidget,
        connected to the QWidget event.QCloseEvent ("closed)
        the window")
        '''        
        rep = QMessageBox.question(self,        
            'Message',                          # bar title
            "Do you realy want to quit ?",      # text in the pop up window
            QMessageBox.Yes | QMessageBox.No,   # butons 'Yes' & 'No'
            QMessageBox.No)                     # 'No' is the default
        if rep == QMessageBox.Yes:
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
            QMessageBox.Yes | QMessageBox.No,   # butons 'Yes' & 'No'
            QMessageBox.No)                     # 'No' is the default
        if rep == QMessageBox.Yes:
            self.close()
        