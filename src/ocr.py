import PyPDF2
import re
import pandas as pd

def extract_data_from_pdf(file_path):
    """
    Scrapes and processes from PDF file chosen
    by users and saves the data into DataFrame.
    :param file_path:file path of file to process
    :return: DataFrame with processed Data
    """
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        page = reader.pages[1]
        page_text = page.extract_text()

    lines = page_text.split('\n')
    phone_pattern = r'^\d{9}'
    filtered_lines = [line for line in lines if re.match(phone_pattern, line)]

    data = [line.split() for line in filtered_lines]

    df = pd.DataFrame(data)

    df['nr'] = df[0]
    df['netto'] = df[1].str.replace(',', '.', regex=False)
    df['brutto'] = df[2].str.replace(',', '.', regex=False)

    df = df.drop(labels=[0, 1, 2], axis=1)

    return df