import os
import subprocess
import sys
import openpyxl

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QLabel, QLineEdit, QComboBox

PATH_TO_TXT_HASHES = "data/hashes.txt"
PATH_TO_TXT_RESULTS = "data/results.txt"


def get_path_to_hashcat():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    list_dir = os.listdir(current_dir)
    hash_dir = ""
    for i in list_dir:
        if i.startswith("hashcat"):
            hash_dir = i
            break
    new_hash_dir = os.path.join(current_dir, hash_dir)
    hash_exe_dir = os.path.join(new_hash_dir, "hashcat.exe")
    return hash_exe_dir, new_hash_dir


def get_data_from_excel(file_):
    file_write = open(PATH_TO_TXT_HASHES, mode="w")
    file = openpyxl.load_workbook(file_)
    worksheet = file.active
    for i in worksheet["A"][1:]:
        file_write.write(i.value + '\n')
    file_write.close()
    nums = []
    for i in worksheet["C"][1:]:
        val = i.value
        if val is not None:
            nums.append(int(val))
        else:
            break
    file.close()
    return nums


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hash_modes = {32: 0, 40: 100, 64: 1400, 128: 1700}
        self.start_file = None
        self.finish_file = None
        self.setWindowTitle("Дешифровка")
        self.setGeometry(100, 100, 600, 400)

        self.button = QPushButton("Выбрать файл расшифровки", self)
        self.button.clicked.connect(self.load_start_file)
        self.button.resize(230, 40)
        self.button.move(40, 50)

        self.button2 = QPushButton("Выбрать файл для сохранения", self)
        self.button2.clicked.connect(self.load_finish_file)
        self.button2.resize(230, 40)
        self.button2.move(40, 100)

        self.its_mask = QLabel(self)
        self.its_mask.setText("Введите маску:")
        self.its_mask.resize(230, 40)
        self.its_mask.move(40, 150)

        self.mask = QLineEdit(self)
        self.mask.resize(230, 40)
        self.mask.move(40, 200)
        self.mask.setText("?d?d?d?d?d?d?d?d?d?d?d")

        self.choose_salt = QComboBox(self)
        self.choose_salt.resize(230, 40)
        self.choose_salt.move(40, 250)
        self.choose_salt.addItem("Подобрать соль(сдвиг, только для чисел)")
        self.choose_salt.addItem("Прибавить соль")

        self.button_start = QPushButton("Начать дешифровку", self)
        self.button_start.clicked.connect(self.start_decryption)
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

    def start_decryption(self):
        text = ""
        nums = get_data_from_excel(self.start_file)
        text += f"Excel файл обработался, результат - {PATH_TO_TXT_HASHES}\n"
        self.text_edit.setText(text)
        hashcat_exe, hashcat_dir = get_path_to_hashcat()
        potfile_del = open(f"{hashcat_dir}/hashcat.potfile", "w")
        potfile_del.close()
        results_del = open(PATH_TO_TXT_RESULTS, "w")
        results_del.close()
        hashes_ = open(PATH_TO_TXT_HASHES)
        first_hash = hashes_.readlines()[0].strip()
        hashes_.close()
        hash_mode = str(self.hash_modes[len(first_hash)])

        hashcat_command = [hashcat_exe, "-m", hash_mode, "-a", "3", "--hwmon-temp-abort=110", "-o",
                           os.path.abspath(PATH_TO_TXT_RESULTS), os.path.abspath(PATH_TO_TXT_HASHES),
                           self.mask.text()]
        subprocess.run(hashcat_command, cwd=hashcat_dir)
        text += f"Расшифровали файл {self.start_file}, результат - {PATH_TO_TXT_RESULTS}\nПодбираем соль\n"
        self.text_edit.setText(text)
        if self.choose_salt.currentText() == "Подобрать соль(сдвиг, только для чисел)":
            file = open(PATH_TO_TXT_RESULTS)
            file_data = file.readlines()
            hashes = [i.split(":")[0] for i in file_data]
            hashes_nums = [int(i.split(":")[1].strip()) for i in file_data]
            salt = None
            for hash_ in hashes_nums:
                salt = hash_ - nums[0]
                flag = True
                for num in nums[1:]:
                    if (num + salt) not in hashes_nums:
                        flag = False
                        break
                if flag:
                    out_file = open(self.finish_file, mode="w")
                    for i in range(len(hashes_nums)):
                        res = hashes[i] + ":" + str(hashes_nums[i] - salt) + "\n"
                        out_file.write(res)
                    out_file.close()
                    text += f"Соль подобрана: {salt}, итоговый результат в файле: {self.finish_file}\n"
                    self.text_edit.setText(text)
                    break
            else:
                text += f"Не смогли подобрать соль\n"
                self.text_edit.setText(text)
            file.close()
        else:
            nums = list(map(str, nums))
            file = open(PATH_TO_TXT_RESULTS)
            file_data = file.readlines()
            hashes = [i.split(":")[0] for i in file_data]
            hashes_nums = [i.split(":")[1].strip() for i in file_data]
            salt = None
            for hash_ in hashes_nums:
                if hash_.startswith(nums[0]):
                    salt = hash_.lstrip(nums[0])
                flag = True
                for num in nums[1:]:
                    if (num + salt) not in hashes_nums:
                        flag = False
                        break
                if flag:
                    out_file = open(self.finish_file, mode="w")
                    for i in range(len(hashes_nums)):
                        res = hashes[i] + ":" + str(hashes_nums[i] - salt) + "\n"
                        out_file.write(res)
                    out_file.close()
                    text += f"Соль подобрана: {salt}, итоговый результат в файле: {self.finish_file}\n"
                    self.text_edit.setText(text)
                    break
            else:
                text += f"Не смогли подобрать соль\n"
                self.text_edit.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
