from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog, \
    QTableWidget, QTableWidgetItem, QMessageBox
from src.ocr import extract_data_from_pdf
from src.db import execute


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.setWindowTitle("OrangeOCR")

        # Line Edit
        self.input = QLineEdit("03-2025")
        month_label = QLabel("Wpisz miesiąc w formacie MM-YYYY, np: 04-2025, 11-2026")

        # Main table
        self.table_widget = QTableWidget(self)

        # Buttons
        data_button_group = QHBoxLayout()

        view_button = QPushButton("Raport miesięczny")
        view_button.clicked.connect(self.fetch_data_from_db)
        data_button_group.addWidget(view_button)

        search_button = QPushButton("Wyszukaj")
        search_button.clicked.connect(self.search_data_in_db)
        data_button_group.addWidget(search_button)

        export_to_file_button = QPushButton("Eksport do pliku")
        export_to_file_button.clicked.connect(self.save_to_file)
        data_button_group.addWidget(export_to_file_button)

        load_pdf_button = QPushButton("1. Wczytaj plik pdf")
        load_pdf_button.clicked.connect(self.load_pdf)
        data_button_group.addWidget(load_pdf_button)

        save_to_db_button = QPushButton("2. Zapisz do bazy danych")
        save_to_db_button.clicked.connect(self.save_to_db)
        data_button_group.addWidget(save_to_db_button)

        delete_from_db_button = QPushButton("Usuń z bazy danych")
        delete_from_db_button.clicked.connect(self.delete_data_from_db)
        data_button_group.addWidget(delete_from_db_button)

        users_button_group = QHBoxLayout()

        view_users_button = QPushButton("1. Wyświetl użytkowników")
        view_users_button.clicked.connect(self.fetch_users_from_dataabse)
        users_button_group.addWidget(view_users_button)


        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(month_label)
        main_layout.addWidget(self.input)
        main_layout.addLayout(data_button_group)
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(users_button_group)
        self.setLayout(main_layout)

    def load_pdf(self):
        """
        Loads chosen PDF file into main program
        DataFrame.
        :return:
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.df = extract_data_from_pdf(file_path)
            self.display_data()
            message_box("Dane wczytano pomyślnie")

    def save_to_db(self):
        """
        Saves current DataFrame into database with
        chosen input as month.
        :return:
        """
        month = self.input.text()

        statement = """
                    INSERT INTO data (nr, miesiac, netto, brutto)
                    VALUES (?, ?, ?, ?)
                    """

        confirmation = confirmation_box(f"Czy miesiąc {month} się zgadza dla tej faktury")
        if not confirmation:
            return

        if month:
            confirmation = confirmation_box(f"Czy chcesz zaimportować dane z miesiąca {month}\ndo bazy danych?")
            if confirmation:
                for _, row in self.df.iterrows():
                    execute(statement, params=(row['nr'], month, row['netto'], row['brutto']))

                message_box("Dane zaimportowano pomyślnie")
        else:
            message_box("Proszę podać miesiąc")

    def delete_data_from_db(self):
        """
        Deletes data from database
        based on month from user input.
        :return:
        """
        month = self.input.text()
        statement = """
                    DELETE FROM data
                    WHERE miesiac = ?
                    """

        if month:
            confirmation = confirmation_box(f"Czy chcesz usunąć dane z miesiąca {month}\nz bazy danych?")
            if confirmation:
                execute(statement, params=(month, ))
                message_box("Dane usunięto pomyślnie")
        else:
            message_box("Proszę podać miesiąc")

    def fetch_data_from_db(self):
        """
        Fetches and displays report
        data from database.
        :return:
        """
        month = self.input.text()
        statement = """
                    SELECT u.nr, u.name, u.department, u.account, SUM(d.netto), SUM(d.brutto)
                    FROM users u
                    LEFT JOIN data d ON u.nr = d.nr
                    GROUP BY u.nr, u.name, u.department, u.account
                    UNION
                    SELECT NULL, NULL, 'Konto: ', u.account AS konto, ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                    FROM users u
                    LEFT JOIN data d ON u.nr = d.nr
                    GROUP BY u.account
                    UNION
                    SELECT NULL, NULL, NULL, 'Razem:', ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                    FROM users u
                    LEFT JOIN data d ON u.nr = d.nr
                    """
        if month:
            statement = """
                        SELECT u.nr, u.name, u.department, u.account, SUM(d.netto), SUM(d.brutto)
                        FROM users u
                        LEFT JOIN data d ON u.nr = d.nr
                        WHERE d.miesiac = ?
                        GROUP BY u.nr, u.name, u.department, u.account
                        UNION
                        SELECT NULL, NULL, 'Konto: ', u.account AS konto, ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                        FROM users u
                        LEFT JOIN data d ON u.nr = d.nr
                        WHERE d.miesiac = ?
                        GROUP BY u.account
                        UNION
                        SELECT NULL, NULL, NULL, 'Razem:', ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                        FROM users u
                        WHERE d.miesiac = ?
                        LEFT JOIN data d ON u.nr = d.nr
                        """

            self.df = execute(statement, params=(month, ))
        else:
            self.df = execute(statement)

        self.display_data()

    def save_to_file(self):
        """
        Saves current DataFrame content as
        chosen CSV file.
        """
        save_file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz do pliku CSV", "", "CSV Files (*.csv)")
        if save_file_path:
            self.df.to_csv(save_file_path, index=False)

    def search_data_in_db(self):
        """
        Searches for data in database based
        on user input under conditions like
        month, name or phone number.
        :return:
        """
        _input = self.input.text()
        __input = f"%{_input}%"
        statement = """
                    SELECT u.nr, u.name, u.department, u.account, d.netto, d.brutto
                    FROM users u
                    LEFT JOIN data d ON u.nr = d.nr
                    WHERE d.miesiac = ?
                    OR u.nr LIKE ?
                    OR u.name LIKE ?
                    """
        self.df = execute(statement, params=(_input, __input, __input))
        self.display_data()

    def display_data(self):
        """
        Displays current main DataFrame values
        contained in self.df variable in main
        QTableWidget.
        :return:
        """
        self.table_widget.setRowCount(len(self.df))
        self.table_widget.setColumnCount(len(self.df.columns))
        self.table_widget.setHorizontalHeaderLabels(self.df.columns)
        for row_idx, row in self.df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row_idx, col_idx, item)

    def fetch_users_from_dataabse(self):
        """
        Fetches all user data into main DataFrame
        then displays it in main QTableWidget.
        :return:
        """
        statement = """
                    SELECT * FROM users
                    """

        self.df = execute(statement)
        self.display_data()
        message_box("Dane wczytano pomyślnie")


def message_box(text, title="Uwaga"):
    """
    Initializes and displays QMessageBox
    window with defined text and title.

    :param text: sets QMessageBox text
    :param title: sets QMessageBox title
    :return:
    """
    messagebox = QMessageBox()
    messagebox.setWindowTitle(title)
    messagebox.setText(text)
    messagebox.exec()

def confirmation_box(text, title="Uwaga"):
    """
    Initializes and displays QMessageBox
    window with defined text, title and
    additional confirmation buttons.

    :param text: sets QMessageBox text
    :param title: sets QMessageBox title
    :return: True if Save button was clicked, else returns false
    """
    messagebox = QMessageBox()
    messagebox.setWindowTitle(title)
    messagebox.setText(text)
    messagebox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.StandardButton.Cancel)
    messagebox.setDefaultButton(QMessageBox.Save)

    if messagebox.exec() == 2048:
        return True
    else:
        return False
