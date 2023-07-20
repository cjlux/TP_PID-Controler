# version 1.0 -- 2023/07/06 -- by JLC
#
# Adapted from https://ymt-lab.com/en/post/2021/pyqt5-serial-monitor/"
#
#=========================================================================
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtSerialPort import QSerialPortInfo

import numpy as np
import sys

from time import sleep, time, strftime

#=========================================================================

class SerialPortToolBar(QToolBar):
    '''
    The bar with all the buttons ans combo to configure/open/colse the serial link.
    '''
    def __init__(self, parent):
        super(SerialPortToolBar, self).__init__(parent)
        
        self.parent = parent
        
        self.port_open_btn = QtWidgets.QPushButton('Open')
        self.port_open_btn.setCheckable(True)
        self.port_open_btn.setMinimumHeight(32)

        self.port_names = QtWidgets.QComboBox(self)
        self.port_names.addItems([ port.portName() for port in QSerialPortInfo().availablePorts() ])
        self.port_names.setMinimumHeight(30)

        self.baud_rates = QtWidgets.QComboBox(self)
        self.baud_rates.addItems([
            '110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '28800', 
            '31250', '38400', '51200', '56000', '57600', '76800', '115200', '128000', '230400', '256000', '921600'
        ])
        self.baud_rates.setCurrentText('115200')
        self.baud_rates.setMinimumHeight(30)

        self.data_bits = QtWidgets.QComboBox(self)
        self.data_bits.addItems(['5 bit', '6 bit', '7 bit', '8 bit'])
        self.data_bits.setCurrentIndex(3)
        self.data_bits.setMinimumHeight(30)

        self._parity = QtWidgets.QComboBox(self)
        self._parity.addItems(['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'])
        self._parity.setCurrentIndex(0)
        self._parity.setMinimumHeight(30)

        self.stop_bits = QtWidgets.QComboBox(self)
        self.stop_bits.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])
        self.stop_bits.setCurrentIndex(0)
        self.stop_bits.setMinimumHeight(30)

        self._flowControl = QtWidgets.QComboBox(self)
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
        return int(self.data_bits.currentIndex() + 5)

    def parity(self):
        return self._parity.currentIndex()

    def stopBit(self):
        return self.stop_bits.currentIndex()

    def flowControl(self):
        return self._flowControl.currentIndex()
    