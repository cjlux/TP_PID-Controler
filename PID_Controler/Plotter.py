#
# version 1.0 -- 2023/07/06 -- by JLC
#
#=========================================================================

import numpy as np
import os
from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                             QCheckBox, QPushButton, QLabel, QComboBox, QSizePolicy)
from matplotlib.backends.backend_qt5agg import  \
    FigureCanvasQTAgg as FigureCanvas,          \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class Plotter(QWidget):
    ''' Widget de tracé d'une courbe paramétrée'''

    colors = ['gray', 'orange' , 'green', 'red', 'purple', 'brown', 'pink', 'blue', 'olive', 'cyan' ]

    def __init__(self, parent):

        # appel du constructeur de la classe de base :
        QWidget.__init__(self, parent)

        # *** Bonnes pratiques  ***
        #   Définir dans le constructeur les données persistantes en tant 
        #   qu'attributs, et si on ne connaît pas leur valeur à ce moment 
        #   on peut utiliser None

        self.parent    = parent # fenêtre principale de l'application
        self.dict_var  = {}     # Le dictionnaire des varaiables à tracer avec leurs checkboxes
        self.fig       = None   # The figure of the plot
        self.ax1       = None   # First Y axis (left side of the plot)
        self.ax2       = None   # Second Y axis (rifht side of the plot)
        self.canvas    = None   # The canvas for the plot
        self.toolbar   = None   # The matplotlib toolbar
        self.CSV_file  = ""     # The name of a CSV data file to plot
        self.xlim      = None   # xmin, xmax du tracé
        self.ylim1     = None   # ymin, ymax for ax1 (left side of the plot)
        self.ylim2     = None   # ymin, ymax for ax2 (left side of the plot)

        self.__initUI()   # Initialisation de l'interface utilisateur

    def __initUI(self):

        hbox = QHBoxLayout(self)
        self.setLayout(hbox)

        # la zone de tracé:
        trace_box = QGridLayout()

        #self.axes    = self.figure.add_subplot(111)
        
        self.fig, self.ax1 = plt.subplots()   
        self.ax1.set_title('PID Controler plot')
        self.ax2 = self.ax1.twinx()
        #self.fig.subplots_adjust(left=0.1,right=0.98,bottom=0.1,top=0.95)
        self.canvas  = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fig.tight_layout()
        
        trace_box.addWidget(self.canvas, 0, 0)

        # La barre des boutons Matplotlib:
        bar = QHBoxLayout()
        
        btn = QPushButton('Plot')
        btn.clicked.connect(self.Plot)
        btn.setFixedSize(50,25)
        bar.addWidget(btn)
        #bar.addStretch(1)
        
        self.CSV_combo = QComboBox()
        self.CSV_combo.addItem('Choose CSV file')
        self.CSV_combo.setFixedSize(100,25)
        self.CSV_combo.activated[str].connect(self.LoadCSV_File)
        self.CSV_combo.enterEvent = self.FillCVS_Combo
        bar.addWidget(self.CSV_combo)
        bar.addStretch(1)
        
        trace_box.addLayout(bar, 1,0)
        #trace_box.addStretch(1)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        trace_box.addWidget(self.toolbar, 2, 0)
        #trace_box.addStretch(1)
        
        # La zone de controle:
        ctrl_box = QGridLayout()
        ctrl_box.setContentsMargins(2, 2, 2, 2)
        
        for row, ((key, comment), color) in  enumerate(zip(self.parent.monitor_tab.field_prop, Plotter.colors)):
            
            # skip the "MS" <Elapsed time (ms)> filrd:
            if key == 'MS': continue
            
            label = QLabel(comment)
            
            check = QCheckBox()
            check.setStyleSheet("background-color: "+color)
            check.setFixedSize(25, 25)
            check.setStyleSheet("QCheckBox { width:30px; height:30px; border: 10px;}")  
            check.setStyleSheet("QCheckBox::indicator { width:30px; height:30px; border: 3px solid;}")            
            check.setStyleSheet(f"QCheckBox {{ color:{color};}}")
            check.setChecked(False)
            check.stateChanged.connect(lambda state, k=key: self.select_var(k, state))
            
            btn = QPushButton()
            btn.setCheckable(False)
            btn.setEnabled(False)
            btn.setText('L')
            btn.setStyleSheet("QPushButton { font:bold 16px; }")
            btn.setStyleSheet(f"QPushButton {{ color:{color};}}")
            btn.setFixedSize(30,25)
            btn.setToolTip('L: plot in the Left axis, R: plot in the Right axis')
            btn.clicked.connect(lambda state, k=key: self.select_axis(k, state))
            self.dict_var[key]=(check, btn)

            if key == 'SPE':
                check.setChecked(True)
                btn.setEnabled(True)
                
            ctrl_box.addWidget(label, row, 0)
            ctrl_box.addWidget(check, row, 1)
            ctrl_box.addWidget(btn, row, 2)
            
        
        hbox.addLayout(trace_box)
        hbox.addLayout(ctrl_box)

    def select_axis(self, key, state):
        check, btn = self.dict_var[key]
        if btn.text() == 'L':
            btn.setText('R')
        else:
            btn.setText('L')
        self.Plot()

    def select_var(self, key, state):
        check, btn = self.dict_var[key]
        if state:
            btn.setEnabled(True)
        else:
            btn.setEnabled(False)
        self.Plot()
            
    def ClearAxes(self):
        self.ax1.clear()
        self.ax2.clear()
        self.canvas.draw()

    def Plot(self):

        self.ClearAxes()       
        
        if self.CSV_file:
            self.ax1.set_title(f'PID Controler plot - <{self.CSV_file}>')
        else:
            self.ax1.set_title(f'PID Controler plot')
          
        all_field  = np.array(self.parent.monitor_tab.all_field).T
        field_prop = self.parent.monitor_tab.field_prop
        
        X = all_field[0] # The x values (abscissa) for the plot
        
        for field, (key, comment), color in zip(all_field[1:], field_prop[1:], Plotter.colors ):
            #if key == "SPM": continue
            check, btn = self.dict_var[key]
            # plot only firled with the check widget checked:
            if not check.checkState(): 
                continue
            
            if btn.text() == 'L':
                self.ax1.plot(X, field, 
                               color=color, linewidth=0.5, linestyle='solid', 
                               marker='o', markersize=2.8                                                                                                                                                                                                              , markerfacecolor=color,
                               label=comment)
            else:
                self.ax2.plot(X, field, 
                               color=color, linewidth=0.5, linestyle='solid', 
                               marker='o', markersize=2.8                                                                                                                                                                                                              , markerfacecolor=color,
                               label=comment)
        
        self.ax1.legend(framealpha=1, loc='upper left')
        self.ax2.legend(framealpha=1, loc='upper right')
        
        self.ax1.set_xlabel('Time [ms]')

        self.ax1.grid()
        self.canvas.draw()

    def FillCVS_Combo(self, event):
        self.CSV_combo.clear()
        list_csv_file = [f for f in os.listdir() if f.lower().endswith('.csv')]
        self.CSV_combo.addItem('Choose CSV file')
        for f in list_csv_file:
            self.CSV_combo.addItem(f)
         
         
    def LoadCSV_File(self, CSV_file):

        self.CSV_file = CSV_file
        self.parent.monitor_tab.all_field.clear()
        with open(CSV_file) as F:
            lines = F.readlines()
        for line in lines:
            if line[0] == '#': 
                continue
            else:
                print(line.strip())
                values = [float(x) for x in line.split(';')]
                
                self.parent.monitor_tab.all_field.append(values)
                # update the grapher:                
        self.Plot()
                
            