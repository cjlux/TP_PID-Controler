# version 1.0 -- 2023/07/06 -- by JLC
#=========================================================================
import sys
from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5 import QtWidgets
from PIDcontrol import PIDcontrol

print(f"Python version {sys.version} - QtAppli (qt v{QT_VERSION_STR}, pyqt_v{PYQT_VERSION_STR})")

#=========================================================================
# Check whether there is already a running QApplication (e.g., if running
# from an IDE).
qapp = QtWidgets.QApplication.instance()
if not qapp:
    qapp = QtWidgets.QApplication(sys.argv)

my_app = PIDcontrol()
qapp.exec_() 
#=========================================================================

