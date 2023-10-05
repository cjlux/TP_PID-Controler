__author__      = "Jean-Luc CHARLES, aka JLC"
__copyright__   = "Copyright 2023"
__license__     = "GPL3"
__version__     = "1.0.1"
__date__        = "2023/07/23"
__maintainer__  = "JLC"
__email__       = "jean-luc.charles@mailo.com"

import sys

#
# Try first to import PyQt5 and if it fails import PyQt6
#
try:
    from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    from PyQt5 import QtWidgets
except:
    from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    from PyQt6 import QtWidgets
    
from PIDcontrol import PIDcontrol

print(f"Python version {sys.version} - QtAppli (qt v{QT_VERSION_STR}, pyqt_v{PYQT_VERSION_STR})")

# Check whether there is already a running QApplication (e.g., if running from an IDE):
qapp = QtWidgets.QApplication.instance()
if not qapp:
    qapp = QtWidgets.QApplication(sys.argv)

my_app = PIDcontrol()
qapp.exec() 
