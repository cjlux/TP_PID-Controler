__author__      = "Jean-Luc CHARLES, aka JLC"
__copyright__   = "Copyright 2023"
__license__     = "GPL3"
__version__     = "1.0.1"
__date__        = "2023/07/23"
__maintainer__  = "JLC"
__email__       = "jean-luc.charles@mailo.com"

#
# Try first to import PyQt5 and if it fails import PyQt6
#
import pyqtgraph as pg

try:
    from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QSpinBox, QGridLayout, QHBoxLayout,
                                 QSizePolicy, QLineEdit, QMessageBox)
except:
    from PyQt6.QtWidgets import (QWidget, QPushButton, QLabel, QSpinBox, QGridLayout, QHBoxLayout,
                                 QSizePolicy, QLineEdit, QMessageBox)    

import numpy as np
import time

class Grapher(QWidget):
        
    def __init__(self, parent, start_char, stop_char):
        
        super(Grapher, self).__init__(parent)

        # *** Good practices  ***
        # Define in the constructor the persisted data as attributes, 
        # and if we don't know their value at this time we can use 'None'.
        
        self.parent         = parent
        self.start_char     = start_char            # the char command for the START btn
        self.stop_char      = stop_char             # the char commad for the STOP btn
        self.graphWidget    = pg.PlotWidget(self)   # The plotter
        self.startstop_btn  = QPushButton()         # the START/STOP button
        self.save_btn       = QPushButton()         # the save button to write data in a CSV file
        self.file_prefix    = QLineEdit()           # A prefix for the generated fle name
        self.file_name      = QLineEdit()           # To edit the name of the file to save data
        self.graph_length   = QSpinBox()            # The length of the graph
        self.timestamp_name =''                     # proposed CSV save file name
        
        self.data_line      = None                  # the data to update the graph
        
        self.__initUI()
        
    def __initUI(self):
        
        print("Grapher.__initUI")
        grid =  QGridLayout()
        self.setLayout(grid)

        # The plotter of PyQtGraph:
        self.graphWidget.setBackground('w')
        styles = {'font-size':'20px'}
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setLabel('bottom', 'time [ms]')
        self.graphWidget.setMinimumWidth(600)
        self.graphWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        line = QHBoxLayout()
        
        self.startstop_btn.setText("START")
        self.startstop_btn.setEnabled(False)
        self.startstop_btn.setCheckable(True)
        self.startstop_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.startstop_btn.setFixedSize(70,25)
        self.startstop_btn.setToolTip(f"Send the start ('{self.start_char}') / stop('{self.stop_char}') command ")
        self.startstop_btn.clicked.connect(lambda state: self.StartStop(state))
        line.addWidget(self.startstop_btn)
        line.addStretch(1)
        
        label = QLabel('Optional prefix:')
        label.setToolTip('Optional prefix to the data file name')
        line.addWidget(label)
        
        self.file_prefix.setText('')
        self.file_prefix.setEnabled(False)
        self.file_prefix.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.file_prefix.setFixedSize(50, 25)
        self.file_prefix.setToolTip('Optional prefix to the data file name')
        line.addWidget(self.file_prefix)

        self.file_name.setText('name of the CSV data file')
        self.file_name.setEnabled(False)
        self.file_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.file_name.setFixedSize(200, 25)
        self.file_name.setToolTip('The name of the CSV data file to save')

        line.addWidget(self.file_name)
        
        self.save_btn.setText("Save CSV")
        self.save_btn.setFixedSize(70, 25)
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip('Save the graph data to the CSV file')
        self.save_btn.clicked.connect(self.SaveData)
        line.addWidget(self.save_btn)
        line.addStretch(1)
        
        label = QLabel('Length', parent=self)
        line.addWidget(label)
        
        self.graph_length.setRange(10, 10000)
        self.graph_length.setValue(100)
        self.graph_length.setSingleStep(10)
        self.graph_length.valueChanged.connect(lambda x: self.parent.UpdateGraphLength(x))
        
        line.addWidget(self.graph_length)
    
        pen = pg.mkPen(color=(0, 0, 255))
        self.data_line =  self.graphWidget.plot([], [], pen=pen)
        
        grid.addWidget(self.graphWidget, 0, 0)
        grid.addLayout(line, 1, 0)

    def Plot(self, x, y, color=(0, 0, 255)):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, pen=pen)
        
    def setData(self, all_field):
        all_field = np.array(all_field).T
        x = all_field[0]
        y = all_field[-2]
        self.data_line.setData(x, y)
        
    def StartStop(self, state):
        if state:
            self.startstop_btn.setText('STOP')
            self.parent.sendFromPort(self.parent.start_char)
            self.file_name.setText("")
            self.file_prefix.setEnabled(True)
            self.file_name.setEnabled(False)
            self.save_btn.setEnabled(False)
        else:
            self.startstop_btn.setText('START')
            self.parent.sendFromPort(self.parent.stop_char)
            self.timestamp_name = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
            self.file_name.setText(self.timestamp_name + ".csv")
            self.file_prefix.setEnabled(True)
            self.file_name.setEnabled(True)
            self.save_btn.setEnabled(True)
            #self.save_file.setText('Data saved in file <>')

    def SaveData(self):
        prefix = self.file_prefix.text()
        if prefix: prefix += '_'
        file_name = prefix + self.file_name.text()
        try:
            with open(file_name, "w") as F:
                # write header line:
                line1 = [f"#{key}" for key, comment in self.parent.field_prop]
                line2 = [f"#{comment}" for key, comment in self.parent.field_prop]
                F.write(";".join(line1) + "\n")
                F.write(";".join(line2) + "\n")
                # write the fields values:
                for field in self.parent.all_field:
                    line = [f"{data:.4f}" for data in field]
                    F.write(";".join(line) + "\n")
        except:
            QMessageBox.critical(self, 'Info', f"Error when saving File <{file_name}> ", QMessageBox.Ok) 
        else:
            QMessageBox.information(self, "Info", f"File <{file_name}> saved succesfully", QMessageBox.Ok) 
             
                