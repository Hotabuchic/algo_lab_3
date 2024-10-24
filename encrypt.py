import hashlib
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QComboBox, QTextEdit, QLineEdit
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hash_modes = {"MD5": 0, "SHA-1": 100, "SHA-256": 1400, "SHA-512": 1700}
        self.start_file = None
        self.finish_file = None
        self.setWindowTitle("Зашифрофка")
        self.setGeometry(100, 100, 600, 400)

        self.button = QPushButton("Выбрать файл зашифровки", self)
        self.button.clicked.connect(self.load_start_file)
        self.button.resize(230, 40)
        self.button.move(40, 50)

        self.button2 = QPushButton("Выбрать файл для сохранения", self)
        self.button2.clicked.connect(self.load_finish_file)
        self.button2.resize(230, 40)
        self.button2.move(40, 100)

        self.choose_hash = QComboBox(self)
        self.choose_hash.resize(230, 40)
        self.choose_hash.move(40, 150)
        self.choose_hash.addItem("md5")
        self.choose_hash.addItem("sha1")
        self.choose_hash.addItem("sha256")
        self.choose_hash.addItem("sha512")

        self.choose_salt = QComboBox(self)
        self.choose_salt.resize(230, 40)
        self.choose_salt.move(40, 200)
        self.choose_salt.addItem("Добавить соль")
        self.choose_salt.addItem("Прибавить соль(сдвиг, только для чисел)")

        self.salt = QLineEdit(self)
        self.salt.resize(230, 40)
        self.salt.move(40, 250)

        self.button_start = QPushButton("Зашифровать", self)
        self.button_start.clicked.connect(self.start_encryption)
        self.button_start.resize(230, 40)
        self.button_start.move(40, 300)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(300, 50, 250, 300)

    def load_start_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "",
                                              options=options)
        self.start_file = file
        self.button.setText(file.split("/")[-1])

    def load_finish_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "",
                                              options=options)
        self.finish_file = file
        self.button2.setText(file.split("/")[-1])

    def start_encryption(self):
        hash_func = hashlib.new(self.choose_hash.currentText())
        file = open(self.start_file)
        data = file.readlines()
        file.close()
        salt = self.salt.text()
        choose_salt = self.choose_salt.currentText()
        out_file = open(self.finish_file, mode="w")
        if choose_salt == "Прибавить соль(сдвиг, только для чисел)":
            if salt:
                for i in data:
                    num = str(int(i.strip()) + int(salt))
                    hash_func.update(num.encode())
                    out_file.write(hash_func.hexdigest() + "\n")
                    hash_func = hashlib.new(self.choose_hash.currentText())
        else:
            for i in data:
                num = i.strip() + salt
                hash_func.update(num.encode())
                out_file.write(hash_func.hexdigest() + "\n")
                hash_func = hashlib.new(self.choose_hash.currentText())
        out_file.close()
        self.text_edit.setText(f"{self.start_file} успешно зашифрован {self.choose_hash.currentText()}\n"
                               f"Результат находится в {self.finish_file}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
