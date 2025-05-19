from PySide6.QtWidgets import QApplication
import sys

from src.ui import UI

# Aplikacja OCR do odczytu faktur z numerami telefonów z orange
# Stworzył Jakub Kołodziej
# 19.05.2025

app = QApplication(sys.argv)

window = UI()
window.show()

app.exec()

