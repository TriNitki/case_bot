import sys
from PyQt5.QtCore    import QTimer, QDateTime
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, \
    QTextEdit, QPushButton

from datetime import datetime
import func as f


class MyGui(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = QLabel('time', self)
        self.textEdit = QTextEdit()
        self.button = QPushButton('Старт')
        self.button.clicked.connect(self.onButton)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.button)

        self.timer = QTimer(self)
        
        now = datetime.now()
        delay = 3600000 - int(now.minute * 60000 + now.second * 1000 + now.microsecond / 1000)
        self.timer.setInterval(delay) # интервал времени ожидания в миллисекундах
        self.timer.timeout.connect(self.displayTime)

    def displayTime(self):
        self.label.setText(QDateTime.currentDateTime().toString())
        now = datetime.now()
        delay = 3600000 - int(now.minute * 60000 + now.second * 1000 + now.microsecond / 1000)
        """db update"""
        f.update_currencies()
        f.update_items()
        f.update_assets()
        self.timer.setInterval(delay)
        self.textEdit.append('Success')

    def onButton(self):
        if self.button.text() == 'Старт':
            self.timer.start()                        # start
            self.button.setText('Стоп')
        else:
            self.timer.stop()                         # stop
            self.button.setText('Старт')           



app = QApplication(sys.argv)
gui = MyGui()
gui.show()
sys.exit(app.exec_())