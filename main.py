"""
Author: Jakub Kołodziej
"""

from PySide6.QtWidgets import QApplication
import sys

from src.ui import UI

app = QApplication(sys.argv)

window = UI()
window.show()

app.exec()

