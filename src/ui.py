from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog, \
    QTableWidget, QTableWidgetItem, QMessageBox
from src.ocr import extract_data_from_pdf
from src.db import read_database, delete_from_database, save_to_database


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.setWindowTitle("OrangeOCR")

        # Line Edit
        self.month_input = QLineEdit("04-2025")
        month_label = QLabel("Wpisz miesiąc w formacie MM-YYYY, np: 04-2025, 11-2026")

        # Main table
        self.table_widget = QTableWidget(self)

        # Buttons
        button_group = QHBoxLayout()

        button1 = QPushButton("1. Wczytaj plik pdf")
        button1.clicked.connect(self.load_pdf)
        button_group.addWidget(button1)

        save_to_db_button = QPushButton("2. Zapisz do bazy danych")
        save_to_db_button.clicked.connect(self.save_to_db)
        button_group.addWidget(save_to_db_button)

        view_button = QPushButton("3. Wyświetl dany miesiąc")
        view_button.clicked.connect(self.fetch_from_db)
        button_group.addWidget(view_button)

        export_to_file_button = QPushButton("4. Eksport do pliku")
        export_to_file_button.clicked.connect(self.save_to_file)
        button_group.addWidget(export_to_file_button)

        delete_from_db_button = QPushButton("Usuń z bazy danych")
        delete_from_db_button.clicked.connect(self.delete_from_db)
        button_group.addWidget(delete_from_db_button)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(month_label)
        main_layout.addWidget(self.month_input)
        main_layout.addLayout(button_group)
        main_layout.addWidget(self.table_widget)
        self.setLayout(main_layout)

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.df = extract_data_from_pdf(file_path)
            self.display_data()
            message_box("Dane wczytano pomyślnie")

    def save_to_db(self):
        month = self.month_input.text()
        if month:
            confirmation = confirmation_box(f"Czy chcesz zapisać dane z miesiąca {month}\nz bazy danych?")
            if confirmation:
                save_to_database(month, self.df)
                message_box("Dane zaimportowano pomyślnie")
        else:
            message_box("Proszę podać miesiąc")

    def delete_from_db(self):
        month = self.month_input.text()
        if month:
            confirmation = confirmation_box(f"Czy chcesz usunąć dane z miesiąca {month}\ndo bazy danych?")
            if confirmation:
                delete_from_database(month)
                message_box("Dane usunięto pomyślnie")
        else:
            message_box("Proszę podać miesiąc")

    def fetch_from_db(self):
        month = self.month_input.text()
        self.df = read_database(month)
        self.display_data()
        message_box("Dane wczytano pomyślnie")

    def save_to_file(self):
        save_file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz do pliku CSV", "", "CSV Files (*.csv)")
        if save_file_path:
            self.df.to_csv(save_file_path, index=False)

    def display_data(self):
        self.table_widget.setRowCount(len(self.df))
        self.table_widget.setColumnCount(len(self.df.columns))
        self.table_widget.setHorizontalHeaderLabels(self.df.columns)
        for row_idx, row in self.df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row_idx, col_idx, item)


def message_box(text, title="Uwaga"):
    messagebox = QMessageBox()
    messagebox.setWindowTitle(title)
    messagebox.setText(text)
    messagebox.exec()

def confirmation_box(text, title="Uwaga"):
    messagebox = QMessageBox()
    messagebox.setWindowTitle(title)
    messagebox.setText(text)
    messagebox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.StandardButton.Cancel)
    messagebox.setDefaultButton(QMessageBox.Save)

    if messagebox.exec() == 2048:
        return True
    else:
        return False
