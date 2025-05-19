## OrangeOCR

Simple tool that scrapes data from invoices from Polish telecom Orange.

I created this tool to automate and simplify some of the work of internal accounting department.

### Installation
I compile this using pyinstaller package and redistribute it as single "exe" file

To do this please run command below in main project directory
```bash
pyinstaller --onefile --name OrangeOCR main.py
```

### Tools:
* Qt with `pyside6`
* `sqlite3` database
* `pypdf2` as PDF OCR tool
* `pandas`
