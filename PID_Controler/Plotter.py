__author__      = "Jean-Luc CHARLES, aka JLC"
__copyright__   = "Copyright 2023"
__license__     = "GPL3"
__version__     = "1.0.1"
__date__        = "2023/07/23"
__maintainer__  = "JLC"
__email__       = "jean-luc.charles@mailo.com"


import numpy as np
import os

try:
    from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                                 QCheckBox, QPushButton, QLabel, QComboBox, QSizePolicy)
    from PyQt5.QtCore import Qt
except:
    from PyQt6.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                                 QCheckBox, QPushButton, QLabel, QComboBox, QSizePolicy)
    from PyQt6.QtCore import Qt
    
from matplotlib.backends.backend_qt5agg import  \
    FigureCanvasQTAgg as FigureCanvas,          \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class Plotter(QWidget):
    ''' 
    A widget to plot the curve for each field received through the serial link.
    '''

    colors = ['gray', 'olive', 'orange' , 'green', 'red', 'purple', 'brown', 'pink', 'blue', 'cyan' ]

    def __init__(self, parent):

        # call the base class constructor:
        QWidget.__init__(self, parent)

        # *** Good practices  ***
         # Define in the constructor the persisted data as attributes, 
         # and if we don't know their value at this time we can use 'None'.

        self.parent    = parent # Main applicaion window
        self.dict_var  = {}     # The dictionary of the fields to display and plot, with their checkboxes
        self.fig       = None   # The figure of the plot
        self.ax1       = None   # First Y axis (left side of the plot)
        self.ax2       = None   # Second Y axis (right side of the plot)
        self.canvas    = None   # The canvas for the plot
        self.toolbar   = None   # The matplotlib toolbar
        self.CSV_file  = ""     # The name of a CSV data file to plot
        self.xlim      = None   # xmin, xmax of the X axis
        self.ylim1     = None   # ymin, ymax for ax1 (left side of the plot)
        self.ylim2     = None   # ymin, ymax for ax2 (left side of the plot)

        self.__initUI()   # Initialize the users graphical interface

    def __initUI(self):

        print("Plotter.__initUI")
        hbox = QHBoxLayout(self)
        self.setLayout(hbox)

        # The grid to place the widgets:
        trace_box = QGridLayout()
        
        # The left axes:
        self.fig, self.ax1 = plt.subplots()
        self.ax1.set_title('PID Controler plot')
        
        # The right axes:
        self.ax2 = self.ax1.twinx()
        
        #self.fig.subplots_adjust(left=0.1,right=0.98,bottom=0.1,top=0.95)
        self.canvas  = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.fig.tight_layout()
        
        trace_box.addWidget(self.canvas, 0, 0)

        # The Matplotlib toolbar:
        bar = QHBoxLayout()
        
        # The Plot button:
        btn = QPushButton('Plot')
        btn.clicked.connect(self.Plot)
        btn.setFixedSize(50,25)
        bar.addWidget(btn)
        
        # The combo box to choose a CSV file:
        self.CSV_combo = QComboBox()
        self.CSV_combo.addItem('Choose CSV file')
        self.CSV_combo.setFixedSize(250,25)
        self.CSV_combo.textActivated[str].connect(self.LoadCSV_File)
        self.CSV_combo.enterEvent = self.FillCVS_Combo
        bar.addWidget(self.CSV_combo)
        bar.addStretch(1)
        
        trace_box.addLayout(bar, 1, 0)
        
        # The matplotlib navigation toolbar:
        self.toolbar = NavigationToolbar(self.canvas, self)
        trace_box.addWidget(self.toolbar, 2, 0)
        
        # The widget grid to organize the check boxes of the fields:
        ctrl_box = QGridLayout()
        ctrl_box.setContentsMargins(2, 2, 2, 2)
        
        for row, ((key, comment), color) in  enumerate(zip(self.parent.monitor_tab.field_prop, Plotter.colors)):
            
            # skip the "MS" <Elapsed time (ms)> field:
            if key == 'MS': continue

            label = QLabel(comment)
            
            check = QCheckBox()
            check.setStyleSheet("background-color: " + color)
            check.setFixedSize(25, 25)
            check.setStyleSheet("QCheckBox { width:30px; height:30px; border: 10px;}")  
            check.setStyleSheet("QCheckBox::indicator { width:30px; height:30px; border: 3px solid;}")            
            check.setStyleSheet(f"QCheckBox {{ color:{color};}}")
            check.setChecked(False)
            
            btn = QPushButton()
            btn.setCheckable(False)
            btn.setEnabled(False)
            btn.setText('L')
            btn.setStyleSheet("QPushButton { font:bold 16px; }")
            btn.setStyleSheet(f"QPushButton {{ color:{color};}}")
            btn.setFixedSize(30,25)
            btn.setToolTip('L: plot in the Left axis, R: plot in the Right axis')
            
            self.dict_var[key]=(check, btn)

            # set the Speed field checked and enable the L/R button:
            if key == 'SPE':
                check.setChecked(True)
                btn.setEnabled(True)
                
            ctrl_box.addWidget(label, row, 0)
            ctrl_box.addWidget(check, row, 1)
            ctrl_box.addWidget(btn, row, 2)
            
            check.stateChanged.connect(lambda state, k=key: self.select_var(k, state))
            btn.clicked.connect(lambda state, k=key: self.select_axis(k, state))            
            
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
        
        for field, (key, comment), color in zip(all_field, field_prop, Plotter.colors ):
            # skip the time field 'MS':
            if key == "MS": continue
            
            check, btn = self.dict_var[key]
            # plot only field with the check widget checked:
            if check.checkState() == Qt.CheckState.Unchecked: 
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
        
        if self.ax1.get_legend_handles_labels()[0]: self.ax1.legend(framealpha=1, loc='upper left')
        if self.ax2.get_legend_handles_labels()[0]: self.ax2.legend(framealpha=1, loc='upper right')
        
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
        """
        to load a CSV file and plot the fields.
        """
        
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
