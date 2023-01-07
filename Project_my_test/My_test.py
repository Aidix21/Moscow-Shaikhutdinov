import sys
import sqlite3

from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QTableView
from PyQt5.QtWidgets import QLineEdit, QComboBox, QPushButton, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QPixmap

path = 'data/tests/'
con = sqlite3.connect('data/mytest.db')
font_name = 'Arial'
font_size = 10
W, H = 900, 600


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(W, H))
        self.setWindowTitle("МуTest")
        font = QFont(font_name, font_size)
        row_height = font_size * 4
        # input dialog
        dx = font_size * 2
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Registration")
        dlg.setInputMode(QInputDialog.TextInput)
        dlg.setLabelText("What is your name?")
        dlg.resize(500, 100)
        ok_pressed = dlg.exec_()
        name = dlg.textValue()
        while not name or not ok_pressed:
            ok_pressed = dlg.exec_()
            name = dlg.textValue()
        self.user_name = name
        # настройки теста по умолчанию
        self.theme = 'Health'
        self.title_test = 'Grammar and vocabulary'
        self.file_name_test = path + '1/2812health-reading.txt'
        # строка приветствия
        font = QFont(font_name, 16)
        self.lbs = QLabel(self)
        self.lbs.setFont(font)
        self.lbs.setStyleSheet("color: #A52A2A")
        s = name.capitalize() + ", to start testing, select a topic and a task!"
        self.lbs.setText(s)
        self.lbs.resize(W - 2 * dx, row_height)
        self.lbs.move(dx, dx)
        self.lbs.setFont(font)
        self.lbs_score = QLabel(self)
        self.lbs_score.setFont(font)
        font = QFont(font_name, font_size)
        self.combo = QComboBox(self)
        self.combo.resize(300, row_height)
        self.combo.move(dx, row_height + dx * 2)
        self.combo.setCurrentText('')
        self.combo.setFont(font)
        self.combo.currentTextChanged.connect(self.combo_changed)
        self.combo2 = QComboBox(self)
        self.combo2.resize(300, row_height)
        self.combo2.move(300 + 2 * dx, row_height + dx * 2)
        self.combo2.setCurrentText('')
        self.combo2.setFont(font)
        # begin test
        self.btn = QPushButton(self)
        self.btn.setText('Begin test')
        self.btn.setStyleSheet("background-color: #3FFF00")
        self.btn.clicked.connect(self.load_test)
        self.btn.resize(200, row_height)
        self.btn.move(600 + 3 * dx, row_height + dx * 2)
        self.btn.setFont(font)
        # объекты теста (группы для разных типов тестов)
        self.group = [QLabel(self)] * 5
        self.group2 = [QLabel(self)] * 5
        self.cms = []
        self.edits = []

        # объекты теста (setVisible(False))
        self.task = QLabel(self)
        self.task.setVisible(False)
        self.text = QLabel(self)
        self.text.setVisible(False)
        self.lbs_score.resize(400, row_height)
        self.lbs_score.move(dx, row_height + dx * 2)
        self.lbs_score.setVisible(False)
        # проверка теста
        self.score = 0
        self.check_button = QPushButton(self)
        self.check_button.setText('End test')
        self.check_button.resize(200, row_height)
        self.check_button.move(W // 2 - 100, H - row_height * 3)
        self.check_button.setFont(font)
        self.check_button.clicked.connect(self.view_score)
        self.check_button.setStyleSheet("background-color: #3FFF00")
        self.check_button.setVisible(False)
        # новый тест
        self.new = QPushButton(self)
        self.new.setText('New test')
        self.new.setStyleSheet("background-color: #3FFF00")
        self.new.clicked.connect(self.new_test)
        self.new.resize(200, row_height)
        self.new.move(600 + 3 * dx, row_height + dx * 2)
        self.new.setFont(font)
        self.new.setVisible(False)
        #
        for i in range(5):
            s = 'lbs ' + str(i)
            self.group[i] = QLabel(self)
            self.group[i].setText(s)
            self.group[i].setFont(font)
            self.group[i].setVisible(False)
        for i in range(5):
            s = 'lbs2' + str(i)
            self.group2[i] = QLabel(self)
            self.group2[i].setText(s)
            self.group2[i].setFont(font)
            self.group2[i].setVisible(False)
        for i in range(5):
            edit = QLineEdit(self)
            edit.setFont(font)
            edit.setVisible(False)
            self.edits.append(edit)
        for i in range(5):
            cm = QComboBox(self)
            cm.setFont(font)
            cm.setVisible(False)
            cm.currentTextChanged.connect(self.check_test_type2)
            self.cms.append(cm)
        self.add_themes()
        self.add_tests()

        self.pixmap = QPixmap('data/presents.jpg')
        self.image = QLabel(self)
        self.image.move(190, 160)
        self.image.resize(500, 279)
        self.image.setPixmap(self.pixmap)
        self.image.setVisible(False)
        self.button_Thank = QPushButton(self)
        self.button_Thank.resize(501, 40)
        self.button_Thank.move(189, 439)
        self.button_Thank.setText("Continue")
        self.button_Thank.setVisible(False)
        self.button_Thank.clicked.connect(self.remove_promotion)

        self.button_results = QPushButton(self)
        self.button_results.resize(200, 50)
        self.button_results.move(660, 17)
        self.button_results.setText("Results")
        self.button_results.clicked.connect(self.check_results)

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('data/mytest.db')
        db.open()
        # QTableView - виджет для отображения данных из базы
        self.result = QTableView(self)
        # Создадим объект QSqlTableModel,
        # зададим таблицу, с которой он будет работать,
        #  и выберем все данные
        model = QSqlTableModel(self, db)
        model.setTable('results')
        model.select()
        # Для отображения данных на виджете
        # свяжем его и нашу модель данных
        self.result.setModel(model)
        self.result.move(10, 240)
        self.result.resize(541, 350)
        self.result.setVisible(False)
        self.button_hide_results = QPushButton(self)
        self.button_hide_results.resize(100, 30)
        self.button_hide_results.move(555, 560)
        self.button_hide_results.setText("Ok")
        self.button_hide_results.clicked.connect(self.close_results)
        self.button_hide_results.setVisible(False)

    def add_themes(self):
        cur = con.cursor()
        request = f"""select title DISTING from themes"""
        result = cur.execute(request).fetchall()
        if len(result) != 0:
            for item in result:
                self.combo.addItem(item[0])
        else:
            self.combo.addItems(['Health', 'Sport'])

    def combo_changed(self):
        self.add_tests()

    def add_tests(self):
        cur = con.cursor()
        theme = self.combo.currentText()
        self.combo2.clear()
        request = f"""select title  from tests
        where theme in (select id from themes where title ='{theme}')"""
        result = cur.execute(request).fetchall()
        if len(result) != 0:
            for item in result:
                self.combo2.addItem(item[0])
                self.btn.setEnabled(True)
        else:
            self.combo2.addItem('No test in DB')
            self.btn.setEnabled(False)
        print(result)

    def load_test(self):
        self.button_results.setVisible(False)
        self.result.setVisible(False)
        self.button_hide_results.setVisible(False)

        cur = con.cursor()
        theme = self.combo.currentText()
        test = self.combo2.currentText()
        request = f"""select theme, fname, type from tests
                where title = '{test}' and
                theme in (select id from themes where title ='{theme}')"""
        result = cur.execute(request).fetchall()
        print(result[0])
        if len(result) != 0:
            self.file_name_test = (path + str(result[0][0]) +
                                   '/' + result[0][1])
            self.theme = theme
            self.title_test = test
        print(self.file_name_test)
        type = result[0][2]
        if type == 2:
            self.test_type_2()

    def test_type_2(self):
        font = QFont(font_name, 16)
        self.lbs.setFont(font)
        try:
            f = open(self.file_name_test)
            text = f.read().split('#')
            task, words, questions, ans = [i.strip() for i in text]
            self.words = words.split()
            self.questions = questions.split('\n')
            self.ans = [int(i) for i in ans.split()]
            self.task_text = task
            n = len(self.questions)
        except:
            self.lbs.setText("file not found or corrupted")
        if f:
            self.btn.setVisible(False)
            self.lbs.setText(f'{self.theme}. {self.title_test}')
            self.lbs.setStyleSheet("color: #A52A2A")
            m = max([len(x) for x in self.words]) + 5  # длина комбобокса
            row_height = font_size * 4
            dx = font_size * 2
            # вывод теста
            self.combo.setVisible(False)
            self.combo2.setVisible(False)
            self.task.setText(task)
            self.task.setFont(font)
            self.task.resize(W - 2 * dx, row_height)
            self.task.setWordWrap(True)
            self.task.move(dx, 150)
            self.task.setVisible(True)
            for i in range(n):
                s = self.questions[i].split('*')
                x, y = row_height, 200 + i * (row_height + 10)
                self.group[i].resize(len(s[0]) * font_size, row_height)
                self.group[i].setText(s[0])
                self.group[i].move(x, y)
                self.group[i].setVisible(True)
                x = x + len(s[0]) * font_size
                self.cms[i].move(x, y)
                self.cms[i].addItems([''] + self.words)
                self.cms[i].resize(m * font_size, row_height)
                self.cms[i].setVisible(True)
                x += m * font_size
                self.group2[i].resize(len(s[-1]) * font_size, row_height)
                self.group2[i].setText(s[-1])
                self.group2[i].move(x, y)
                self.group2[i].setVisible(True)

    def check_test_type2(self):
        y = H - 80
        row_height = font_size * 4
        x = font_size * 2
        count_change = 0
        n = len(self.questions)
        for i in range(n):
            s = self.cms[i].currentText()
            if s != '':
                count_change += 1

        if count_change == n:
            self.check_button.setVisible(True)

    def view_score(self):
        self.check_button.setVisible(False)
        n = len(self.questions)
        name = self.user_name
        theme = self.combo.currentText()
        titl = self.combo2.currentText()

        count_true = 0
        for i in range(n):
            s = self.cms[i].currentText()
            if s == self.words[self.ans[i]]:
                count_true += 1
            else:
                self.cms[i].setStyleSheet("background-color: #A52A2A; color: white;")
            self.cms[i].setEnabled(False)
        self.lbs_score.setText("Score: " + str(round(count_true / n * 100)))
        self.lbs_score.setVisible(True)
        self.new.setVisible(True)
        if round(count_true / n * 100) == 100:
            self.button_Thank.setVisible(True)
            self.image.setVisible(True)

        cur = con.cursor()
        cur.execute(f"""INSERT INTO results(names, themes, title, score) VALUES('{name}', '{theme}', '{titl}',
        {round(count_true / n * 100)})""")
        con.commit()

    def remove_promotion(self):
        self.button_Thank.setVisible(False)
        self.image.setVisible(False)

    def check_results(self):
        con.commit()
        self.result.setVisible(True)
        self.button_hide_results.setVisible(True)

    def close_results(self):
        self.result.setVisible(False)
        self.button_hide_results.setVisible(False)

    def new_test(self):
        self.button_results.setVisible(True)
        self.task.setVisible(False)
        self.text.setVisible(False)
        self.lbs_score.setVisible(False)
        self.new.setVisible(False)
        for i in range(5):
            self.group[i].setVisible(False)
        for i in range(5):
            self.group2[i].setVisible(False)
        for i in range(5):
            self.edits[i].setVisible(False)
            self.edits[i].setEnabled(True)
        for i in range(5):
            self.cms[i].setVisible(False)
            self.cms[i].setEnabled(True)
        self.combo.setVisible(True)
        self.combo2.setVisible(True)
        self.btn.setVisible(True)
        s = self.user_name.capitalize() + ", to start testing, select a topic and a task!"
        self.lbs.setText(s)


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())