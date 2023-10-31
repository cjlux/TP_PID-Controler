__author__      = "Jean-Luc CHARLES, aka JLC"
__copyright__   = "Copyright 2023"
__license__     = "GPL3"
__version__     = "1.0.1"
__date__        = "2023/07/23"
__maintainer__  = "JLC"
__email__       = "jean-luc.charles@mailo.com"
__credits__     = "https://ymt-lab.com/en/post/2021/pyqt5-serial-monitor/"

#
# Try first to import PyQt5 and if it fails import PyQt6
#
try:
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QCheckBox,
                                 QFrame, QPushButton, QTextEdit, QGridLayout, QSizePolicy, QToolBar,
                                 QComboBox)
    from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
    from PyQt5.QtGui import QTextCursor, QFont
except:
    from PyQt6 import QtCore, QtGui
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QCheckBox,
                                 QFrame, QPushButton, QTextEdit, QGridLayout, QSizePolicy, QToolBar,
                                 QComboBox)
    from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
    from PyQt6.QtGui import QTextCursor, QFont
    
from time import strftime
from collections import deque
from Grapher import Grapher

class Monitor(QWidget):
    '''
    To read data coming from the serial link and send commands to the microcontroler
    using the serial link
    '''

    # Class attributes:
    ino_file   = "./testCodeurTeensy5/testCodeurTeensy5.ino"
    start_char = 'c'
    stop_char  = 'b'

    def __init__(self, parent):

        # Call the base class constructor:
        QWidget.__init__(self, parent)
        
        # *** Good practices  ***
         # Define in the constructor the persisted data as attributes, 
         # and if we don't know their value at this time we can use 'None'.

        self.mw    = parent     # main window of the application
        
        self.port  = None       # The serial port, see xxxxxx 
        self.data  = ""         # the data collected from the serial link 
        self.dict_var  = {}     # The dictionary of the firld to display and plot, with their checkboxes
                
        # The list of the labeled Field widgets to show data received from the serial link
        self.labeled_fields  = []
        
        # The list of the labeled buttons to send commands through the serial link
        self.labeled_buttons = []

        self.button_prop     = []  # the properties of the buttons
        self.field_prop      = []  # the properties of the fields 
        
        # Attributes for plotting:
        self.figure          = None  # figure for plotting
        self.axes            = None  # plot axis
        self.canvas          = None  # matplot.lib canvas
        self.toolbar         = None  # plot toolbar
        self.plot_xlim       = None  # plot xmin, xmax
        self.plot_ylim       = None  # plot ymin, ymax

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
        '''To Grep lines in the .ino file that contain the word "case" to 
           set the labels of the command buttons.
           Expected line pattern is :
           - <case '+':// Accélere>             for a serial input
           - <mess += ",COM,";  // Command>     for a serila output
        '''
        try:    
            with open(Monitor.ino_file, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if 'case' in line:
                        key = line.split("'")[1]
                        comment = line.split('//')[-1].strip()
                        self.button_prop.append((key, comment))
                        print(f'Found key <{key}> and comment <{comment}> in line "{line}"')
                    elif 'mess +=' in line and 'String' not in line:
                        key = line.split('"')[1].replace(',','')
                        comment = line.split('//')[-1].strip()
                        self.field_prop.append((key, comment))
                        print(f'Found key <{key}> and comment <{comment}> in line <{line}>')
                
        except:
            print(f"Failed to process file {Monitor.ino_file}")
        
        return len(self.field_prop)
        
    def PortOpen(self, flag):
        if flag:
            self.port.setBaudRate( self.serial_toolbar.baudRate() )
            self.port.setPortName( self.serial_toolbar.portName() )
            #print(self.serial_toolbar.dataBit())
            self.port.setDataBits( self.serial_toolbar.dataBit() )
            self.port.setParity( self.serial_toolbar.parity() )
            self.port.setStopBits( self.serial_toolbar.stopBit() )
            self.port.setFlowControl( self.serial_toolbar.flowControl() )
            r = self.port.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
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
        '''
        To read data received on the serial link.
        '''
        
        data = self.port.readAll()
        string = QtCore.QTextStream(data).readAll()
        
        if len(string) <= 0: return

        # Display the data in the 'serial_view':        
        self.serial_view.AppendSerialText(string, QtGui.QColor(0, 0, 0))

        # Extract informations from data
        index = string.find('\n')
        while index != -1:
            self.data += string[:index]
            string = string[index+1:]
            
            values = []
            try:
                # print(f"<{repr(self.data)}>")
                values = [float(x) for x in self.data.split(',')[1::2]]
                for (_, field), value in zip(self.labeled_fields, values):
                    field.setNum(value)   # display the value in the Widget
                # print(values)
                self.all_field.append(values)
                # update the grapher:                
                self.graph_widget.setData(self.all_field)
            except:
                print(f"err:<{self.data}>")
            
            index = string.find('\n')
            self.data = ""
        self.data += string
        
    def sendFromPort(self, text):
        self.port.write(text.encode())
        #self.serial_view.AppendSerialText( text, QtGui.QColor(100, 100, 255) )
        
    def __initUI(self):
        
        print("Monitor.__initUI")
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
        
        print("SerialDataView.__init__")
        super(SerialDataView, self).__init__(parent)
        
        self.serialData = QTextEdit()
        self.serialData.setReadOnly(True)
        self.serialData.setMinimumSize(650,400)
        self.serialData.setFont(QFont('Courier New', 8))
        self.serialData.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.serialData.setFixedWidth(600)

        self.setLayout(QGridLayout())
        self.layout().addWidget(self.serialData, 0, 0)
        self.layout().setContentsMargins(2, 2, 2, 2)
        
    def AppendSerialText(self, appendText, color):
        self.serialData.moveCursor(QTextCursor.MoveOperation.End)
        self.serialData.setFont(QFont('Courier New', 8))
        self.serialData.setTextColor(color)
        self.serialData.insertPlainText(appendText)
        self.serialData.moveCursor(QTextCursor.MoveOperation.End)

class SerialSendView(QWidget):

    serialSendSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        
        print("SerialSendView.__init__")
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
        self.serialSendSignal.emit(self.sendData.toPlainText())
        self.sendData.clear()        
        
class FieldWidget(QWidget):
    
    def __init__(self, parent):
        
        print("FieldWidget.__init__")
        super(FieldWidget, self).__init__(parent)
        self.parent = parent
        
        hbox = QHBoxLayout()
        self.setLayout(hbox)  
        
        for (key, comment) in  parent.field_prop:            
            label = QLabel(f"{key}")
            label.setToolTip(comment)
            label.setFixedSize(125,25)

            value = QLabel()
            value.setToolTip(comment)
            value.setFrameStyle(QFrame.Shape.StyledPanel)
            value.setFixedSize(100,25)
            
            """
            check = QCheckBox()
            if key == 'SPE':
                check.setChecked(True)
            else:
                check.setChecked(False)
            check.setFixedSize(25, 25)
            check.stateChanged.connect(lambda state, k=key: self.SelectField(k, state))
            """
            parent.labeled_fields.append((label, value))

            """h = QHBoxLayout()
            h.addWidget(value)
            h.addWidget(check)"""

            v = QVBoxLayout()
            v.addWidget(label)
            v.addWidget(value)
            #v.addLayout(h)
            
            hbox.addLayout(v)
            hbox.addStretch(1)
        
        hbox.setContentsMargins(2, 2, 2, 2)        
    
    def SelectField(self, key, state):
        pass 
           
class CommandWidget(QWidget):
    """
    To build a widget containing one push button for each of the commands that can be sent through
    the serial link to drive the PID controler.
    The list of the command labels comes from the attribute 'parent.button_prop'.
    """
    def __init__(self, parent):
        
        print("CommandWidget.__init__")
        super(CommandWidget, self).__init__(parent)
        self.parent = parent
        
        hbox = QHBoxLayout()  
        self.setLayout(hbox)
        
        for i, (key, comment) in enumerate(self.parent.button_prop):
            
            if key == Monitor.start_char or key == Monitor.stop_char:
                print(f'skipping <{key}, {comment}>')
                continue
            
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
            
            if i == 0 or i % 2 != 0: 
                v = QVBoxLayout()
            
            v.addLayout(h)
            v.addStretch(1)
            
            if i == 0 or i % 2 != 0: 
                hbox.addLayout(v)
                hbox.addStretch(1)

        hbox.setContentsMargins(2, 2, 2, 2)
        
            
class SerialPortToolBar(QToolBar):
    '''
    The bar with all the buttons ans combo to configure/open/colse the serial link.
    '''
    def __init__(self, parent):
        
        print("SerialPortToolBar.__init__")
        super(SerialPortToolBar, self).__init__(parent)
        
        self.parent = parent
        
        self.port_open_btn = QPushButton('Open')
        self.port_open_btn.setCheckable(True)
        self.port_open_btn.setMinimumHeight(32)

        self.port_names = QComboBox(self)
        self.port_names.addItems([ port.portName() for port in QSerialPortInfo().availablePorts() ])
        self.port_names.setMinimumHeight(30)

        self.baud_rates = QComboBox(self)
        self.baud_rates.addItems([
            '110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '28800', 
            '31250', '38400', '51200', '56000', '57600', '76800', '115200', '128000', '230400', '256000', '921600'
        ])
        self.baud_rates.setCurrentText('115200')
        self.baud_rates.setMinimumHeight(30)

        self.data_bits = QComboBox(self)
        self.data_bits.addItems(['5 bit', '6 bit', '7 bit', '8 bit'])
        self.data_bits.setCurrentIndex(3)
        self.data_bits.setMinimumHeight(30)

        self._parity = QComboBox(self)
        self._parity.addItems(['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'])
        self._parity.setCurrentIndex(0)
        self._parity.setMinimumHeight(30)

        self.stop_bits = QComboBox(self)
        self.stop_bits.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])
        self.stop_bits.setCurrentIndex(0)
        self.stop_bits.setMinimumHeight(30)

        self._flowControl = QComboBox(self)
        self._flowControl.addItems(['No Flow Control', 'Hardware Control', 'Software Control'])
        self._flowControl.setCurrentIndex(0)
        self._flowControl.setMinimumHeight(30)

        self.addWidget(self.port_open_btn)
        self.addWidget(self.port_names)
        self.addWidget(self.baud_rates)
        self.addWidget(self.data_bits)
        self.addWidget(self._parity)
        self.addWidget(self.stop_bits)
        self.addWidget(self._flowControl)

    def serialControlEnable(self, flag):
        self.port_names.setEnabled(flag)
        self.baud_rates.setEnabled(flag)
        self.data_bits.setEnabled(flag)
        self._parity.setEnabled(flag)
        self.stop_bits.setEnabled(flag)
        self._flowControl.setEnabled(flag)
        
        self.parent.graph_widget.startstop_btn.setEnabled(not flag)
        
    def baudRate(self):
        return int(self.baud_rates.currentText())

    def portName(self):
        return self.port_names.currentText()

    def dataBit(self):
        return QSerialPort.DataBits(self.data_bits.currentIndex() + 5)

    def parity(self):
        return QSerialPort.Parity(self._parity.currentIndex())

    def stopBit(self):
        return QSerialPort.StopBits(self.stop_bits.currentIndex())

    def flowControl(self):
        return QSerialPort.FlowControl(self._flowControl.currentIndex())
                