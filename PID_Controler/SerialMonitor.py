#
# version 1.0 -- 2023/07/06 -- by JLC
#
# Some code comes from https://ymt-lab.com/en/post/2021/pyqt5-serial-monitor/"
#
#=========================================================================
import os, sys, platform

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QCheckBox,
                             QFrame, QPushButton, QTextEdit, QGridLayout, QSizePolicy)
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtGui import QTextCursor, QFont

from time import sleep, time, strftime
import numpy as np
from collections import deque

from Grapher import Grapher

from SerialToolBar import SerialPortToolBar

#=========================================================================
class SerialMonitor(QWidget):
    '''
    To read data coming from the serial link and send commands to the microcontroler
    using the serial link
    '''

    # Class attributes:
    ino_file   = "testCodeurTeensy5.ino"
    start_char = 'c'
    stop_char  = 'b'


    def __init__(self, parent):

        # Call the base class constructor:
        QWidget.__init__(self, parent)
        
        # *** Bonnes pratiques  ***
        #   Définir dans le constructeur les données persistantes en tant 
        #   qu'attributs, et si on ne connaît pas leur valeur à ce moment 
        #   on peut utiliser None.

        self.mw    = parent     # fenêtre principale de l'application
        
        self.port  = None       # The serial port, see xxxxxx 
        self.data  = ""         # the data collected from the serial link 
                
        # The list of the labeled Field widgets to show data received from the serial link
        self.labeled_fields  = []
        
        # The list of the labeled buttons to send commands through the serial link
        self.labeled_buttons = []

        self.button_prop     = []  # the properties of the buttons
        self.field_prop      = []  # the properties of the fields 
        
        # Attributes for plotting:
        self.figure          = None  # figure pour le tracé
        self.axes            = None  # système d'axes du tracé
        self.canvas          = None  # pour le tracé matplot.lib
        self.toolbar         = None  # barre d'outils du tracé
        self.plot_xlim       = None  # xmin, xmax du tracé
        self.plot_ylim       = None  # ymin, ymax du tracé

        ### The serial tool bar ###
        self.serial_toolbar  = SerialPortToolBar(self)
        
        self.port = QSerialPort()
            
        self.serial_view  = SerialDataView(self)
        self.graph_widget = Grapher(self)

        #
    	# CSV ASCII output file
    	#
        self.fileName     = 'PID_control-'+strftime("%Y_%m_%d_%H_%M")+'.csv'
        self.data_format  = "{:8.2f}\t{:8.2f}\t{:4.2f}\t{:4.2f}\n"    
        
        L  = self.graph_widget.graph_length.value()
        self.nb_field     = self.ProcessInoFile()  # the number of fields received on the serial link
        self.all_field    = deque([[0]*self.nb_field for _ in range(L)], L)

        # create the tab graphical interface:
        self.__initUI()

        ### Connect widgets ###
        self.serial_toolbar.port_open_btn.clicked.connect(self.PortOpen)
        #self.serial_view.serialSendSignal.connect(self.sendFromPort)
        self.port.readyRead.connect(self.ReadFromSerialPort)
        
    def UpdateGraphLength(self, L):
        self.all_field    = deque([[0]*self.nb_field for _ in range(L)], L)
        # TODO: clear Graph
        
    def ProcessInoFile(self):
        '''Greps lines in the ino file that contain the word "case" to 
           set the labels of the command buttons.
           Expected line pattern is :
           - <case '+':// Accélere>             for a serial input
           - <mess += ",COM,";  // Command>     for a serila output
           
        '''
        
        try:    
            with open(SerialMonitor.ino_file, 'r') as f:
                
                for line in f.readlines():
                    print(line)
                    line = line.strip()
                    if 'case' in line:
                        print(line)
                        key = line.split("'")[1]
                        comment = line.split('//')[-1].strip()
                        self.button_prop.append((key, comment))
                    elif 'mess +=' in line and 'String' not in line:
                        print(line)
                        key = line.split('"')[1].replace(',','')
                        comment = line.split('//')[-1].strip()
                        self.field_prop.append((key, comment))
                
        except:
            print(f"Failed to process file {SerialMonitor.ino_file}")
        
        return len(self.field_prop)
        
    def PortOpen(self, flag):
        if flag:
            self.port.setBaudRate( self.serial_toolbar.baudRate() )
            self.port.setPortName( self.serial_toolbar.portName() )
            self.port.setDataBits( self.serial_toolbar.dataBit() )
            self.port.setParity( self.serial_toolbar.parity() )
            self.port.setStopBits( self.serial_toolbar.stopBit() )
            self.port.setFlowControl( self.serial_toolbar.flowControl() )
            r = self.port.open(QtCore.QIODevice.ReadWrite)
            if not r:
                self.mw.statusText.setText('Port open error')
                self.serial_toolbar.port_open_btn.setChecked(False)
                self.serial_toolbar.serialControlEnable(True)
            else:
                self.mw.statusText.setText('Port opened')
                self.serial_toolbar.serialControlEnable(False)
        else:
            self.port.close()
            self.mw.statusText.setText('Port closed')
            self.serial_toolbar.serialControlEnable(True)
        
    def ReadFromSerialPort(self):
        
        data = self.port.readAll()
        string = QtCore.QTextStream(data).readAll()
        #print(string, end="")
        
        if string[-1] == "\n":
            self.data += string.strip()
            values = []
            try:
                values = [float(x) for x in self.data.split(',')[1::2]]
            except:
                pass
            
            if values:
                for (_, field), value in zip(self.labeled_fields, values):
                    field.setNum(value)   # display the value in the Widget
                #print(values)
                self.all_field.append(values)
                # update the grapher:                
                self.graph_widget.setData(self.all_field)
                
            self.data = ""            
        else:
            self.data += string
        
        self.serial_view.AppendSerialText(string, QtGui.QColor(0, 0, 0))

    def sendFromPort(self, text):
        self.port.write(text.encode())
        #self.serial_view.AppendSerialText( text, QtGui.QColor(100, 100, 255) )
        
    def __initUI(self):
        
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.serial_toolbar, 0, 0, 1, 2)
        grid.addWidget(self.serial_view, 1, 0)
        grid.addWidget(self.graph_widget, 1, 1)
        grid.addWidget(FieldWidget(self), 2, 0, 1, 2)
        grid.addWidget(CommandWidget(self),3, 0, 1, 2)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)
        grid.setRowStretch(0,0)
        grid.setRowStretch(1,1)
        grid.setRowStretch(2,0)
        grid.setRowStretch(3,0)
        

class SerialDataView(QWidget):
    '''
    A Qt Widget to view data coming through a serial link (RS232, USB...).
    '''
    
    def __init__(self, parent):
        
        super(SerialDataView, self).__init__(parent)
        
        self.serialData = QTextEdit()
        self.serialData.setReadOnly(True)
        self.serialData.setMinimumSize(650,400)
        self.serialData.setFont(QFont('Courier New', 8))
        self.serialData.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.serialData.setFixedWidth(600)

        self.setLayout(QGridLayout())
        self.layout().addWidget(self.serialData, 0, 0)
        self.layout().setContentsMargins(2, 2, 2, 2)
        
    def AppendSerialText(self, appendText, color):
        self.serialData.moveCursor(QTextCursor.End)
        self.serialData.setFont(QFont('Courier New', 8))
        self.serialData.setTextColor(color)
        self.serialData.insertPlainText(appendText)
        self.serialData.moveCursor(QTextCursor.End)

class SerialSendView(QWidget):

    serialSendSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super(SerialSendView, self).__init__(parent)

        self.sendData = QTextEdit()
        self.sendData.setAcceptRichText(False)
        self.sendData.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.sendButton = QPushButton('Send')
        self.sendButton.clicked.connect(self.SendButtonClicked)
        self.sendButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        
        self.setLayout(QHBoxLayout() )
        self.layout().addWidget(self.sendData)
        self.layout().addWidget(self.sendButton)
        self.layout().setContentsMargins(3, 3, 3, 3)

    def SendButtonClicked(self):
        self.serialSendSignal.emit( self.sendData.toPlainText() )
        self.sendData.clear()        
        
class FieldWidget(QWidget):
    
    def __init__(self, parent):
        
        super(FieldWidget, self).__init__(parent)
        self.parent = parent
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        
        for (key, comment) in  parent.field_prop:            
            label = QLabel(f"{key}")
            label.setToolTip(comment)
            label.setFixedSize(125,25)

            h = QHBoxLayout()
            value = QLabel()
            value.setToolTip(comment)
            value.setFrameStyle(QFrame.StyledPanel)
            value.setFixedSize(100,25)
            
            check = QCheckBox()
            if key == 'SPE':
                check.setChecked(True)
            else:
                check.setChecked(False)
            check.setFixedSize(25, 25)
            check.stateChanged.connect(lambda state, k=key: self.SelectField(k, state))

            h.addWidget(value)
            h.addWidget(check)
            
            parent.labeled_fields.append((label, value))

            v = QVBoxLayout()
            v.addWidget(label)
            v.addLayout(h)
            
            hbox.addLayout(v)
            hbox.addStretch(1)
        
        hbox.setContentsMargins(2, 2, 2, 2)
        self.setLayout(hbox)          
    
    def SelectField(self, key, state):
        pass 
           
class CommandWidget(QWidget):
    
    def __init__(self, parent):
        
        super(CommandWidget, self).__init__(parent)
        self.parent = parent
        
        hbox = QHBoxLayout()        
        i = 0
        for key, comment in self.parent.button_prop:
            
            if key == SerialMonitor.start_char or key == SerialMonitor.stop_char:
                print(f'skipping <{key}, {comment}>')
                continue

            if i == 0 or i % 2 != 0: 
                v = QVBoxLayout()
            
            label = QLabel(comment)
            
            button = QPushButton()
            button.setText(key)
            button.setFixedSize(30,25)
            button.setToolTip(comment)
            button.clicked.connect(lambda x, k=key: self.parent.sendFromPort(k))
            
            self.parent.labeled_buttons.append((label, button))
            
            h = QHBoxLayout()    
            h.addWidget(button)
            h.addWidget(label)
            v.addLayout(h)
            v.addStretch(1)
            
            hbox.addLayout(v)
            hbox.addStretch(1)
            i += 1

        hbox.setContentsMargins(2, 2, 2, 2)
        self.setLayout(hbox)
            