# version 1.0 -- 2023/07/06 -- by JLC
#
# Some code comes from https://ymt-lab.com/en/post/2021/pyqt5-serial-monitor/"
#
#=========================================================================

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QTextEdit, QGridLayout, QSizePolicy)
from QtGui import QTextCursor

class SerialDataView(QWidget):
    '''
    A Qt Widget to view data lines coming through a serial link (RS232, USB...).
    '''
    
    def __init__(self, parent):
        
        super(SerialDataView, self).__init__(parent)
        
        self.serialData = QTextEdit(self)
        self.serialData.setReadOnly(True)
        self.serialData.setFontFamily('Courier New')
        self.serialData.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(QGridLayout(self))
        self.layout().addWidget(self.serialData,    0, 0, 2, 1)
        self.layout().setContentsMargins(2, 2, 2, 2)
        
    def appendSerialText(self, appendText, color):
        self.serialData.moveCursor(QTextCursor.End)
        self.serialData.setFontFamily('Courier New')
        self.serialData.setTextColor(color)
        
        self.serialData.insertPlainText(appendText)
        
        lastData = self.serialDataHex.toPlainText().split('\n')[-1]
        lastLength = math.ceil( len(lastData) / 3 )
                
        self.serialData.moveCursor(QTextCursor.End)
        