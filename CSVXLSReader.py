import sys
import pandas as pd
import subprocess
import os
import uuid
import json
import time
import shutil
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog

class FileLoaderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV / XLSX File Loader")
        self.setGeometry(300, 300, 600, 400)

        self.setAcceptDrops(True)  # Włączamy akceptowanie upuszczanych plików

        self.label = QLabel("Wybierz plik CSV lub XLSX lub przeciągnij go tutaj", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Wybierz plik CSV/XLSX", self)
        self.button.clicked.connect(self.select_file)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik CSV/XLSX", "", "CSV Files (*.csv);;XLSX Files (*.xlsx)")
        if file_path:
            self.load_file(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        if file_path.endswith(".csv") or file_path.endswith(".xlsx"):
            self.load_file(file_path)
        else:
            self.label.setText("Proszę przeciągnąć plik CSV lub XLSX!")

    def load_file(self, file_path):
        print("Rozpoczęcie przetwarzania...")
        start_time = time.time()

        if os.path.exists(file_path):
            try:
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif file_path.endswith(".xlsx"):
                    df = pd.read_excel(file_path)

                print("Podgląd pliku:")
                print(df.head())
                self.open_vscode_with_file(file_path)
            except Exception as e:
                print(f"Błąd podczas wczytywania pliku: {e}")
        else:
            print("Plik nie istnieje lub nie jest dostępny:", file_path)

        print(f"Czas wykonania: {time.time() - start_time:.2f} sekund")

    def open_vscode_with_file(self, file_path):
        vscode_command = shutil.which('code') or \
                         os.path.expanduser(r'~\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd')

        if not os.path.exists(vscode_command):
            print("Nie znaleziono VS Code! Zainstaluj lub dodaj do ścieżki systemowej.")
            return

        # Zmieniamy nazwę notebooka na nazwę pliku CSV/XLSX z rozszerzeniem .ipynb
        base_name = os.path.basename(file_path)  # Pobieramy nazwę pliku (np. 'dane.csv' lub 'dane.xlsx')
        notebook_name = f"{os.path.splitext(base_name)[0]}.ipynb"  # Zmieniamy rozszerzenie na .ipynb
        notebook_path = os.path.join(os.path.expanduser("~"), "Desktop", notebook_name)  # Ścieżka na pulpicie

        file_path = file_path.replace("\\", "/")  # Zamiana na forward slash
        file_path = file_path.replace("'", "\\'") if "'" in file_path else file_path

        try:
            with open(notebook_path, 'w', encoding='utf-8') as notebook:
                notebook_content = {
                    "nbformat": 4,
                    "nbformat_minor": 5,
                    "metadata": {
                        "kernelspec": {
                            "display_name": "Python 3",
                            "language": "python",
                            "name": "python3"
                        }
                    },
                    "cells": [
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "outputs": [],
                            "source": [
                                "import pandas as pd\n",
                                f"df = pd.read_csv(r'{file_path}')\n" if file_path.endswith('.csv') else f"df = pd.read_excel(r'{file_path}')\n",
                                "print('Wczytano plik:')\n",
                                "df.head()\n",
                                "# Jeśli dane się nie wczytują, sprawdź ścieżkę powyżej"
                            ]
                        }
                    ]
                }
                json.dump(notebook_content, notebook, indent=2)
            print(f"Notebook utworzony: {notebook_path}")
        except Exception as e:
            print(f"Błąd podczas tworzenia notebooka: {e}")
            return

        try:
            subprocess.Popen([vscode_command, notebook_path], shell=True)
            print("VS Code uruchomiony pomyślnie!")
        except Exception as e:
            print(f"Błąd podczas uruchamiania VS Code: {e}")
            print("Spróbuj otworzyć notebook ręcznie z lokalizacji:", notebook_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileLoaderApp()
    window.show()
    sys.exit(app.exec_())
