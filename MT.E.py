import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class PlanetClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Planet Clicker")
        self.showFullScreen()  # Запускаємо на повний екран
        self.setStyleSheet("background:#1e1e2f; color: white;")

        # Ініціалізація змінних гри
        self.score, self.click_power, self.income = 0, 1, 0
        self.click_cost, self.income_cost = 50, 100
        self.grid_size, self.square, self.radius = 19, 24, 9

        # Створення інтерфейсу
        self.make_ui()

        # Таймер для пасивного доходу, спрацьовує щосекунди
        self.timer = QTimer(self, timeout=self.add_income)
        self.timer.start(1000)

    def make_ui(self):
        # Функція для створення підписів
        def label(t, s):
            l = QLabel(t)
            l.setFont(QFont("Arial", s))
            l.setStyleSheet("color: white")
            return l

        # Функція для створення кнопок
        def btn(t, fn):
            b = QPushButton(t)
            b.setStyleSheet(
                "QPushButton {background:#6a5acd; color:white; font-size:20px; padding:10px; border-radius:10px}"
                "QPushButton:hover {background:#7b68ee;}"
            )
            b.clicked.connect(fn)
            return b

        # Створення основних віджетів
        self.score_lbl = label("", 24)
        self.mult_lbl = label("", 18)
        self.inc_lbl = label("", 18)
        self.click_btn = btn("", self.up_click)
        self.income_btn = btn("", self.up_income)

        # Вертикальний лейаут для розташування віджетів
        v = QVBoxLayout()
        for w in [self.score_lbl, self.mult_lbl, self.inc_lbl, self.click_btn, self.income_btn]:
            v.addWidget(w)
        v.addStretch()
        self.setLayout(v)

        # Початкове оновлення UI
        self.update_ui()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2 + 100

        # Малюємо планету у вигляді сітки квадратів
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if ((i - self.radius) ** 2 + (j - self.radius) ** 2) ** 0.5 <= self.radius:
                    p.setBrush(self.phase_color())
                    p.setPen(Qt.NoPen)
                    p.drawRect(cx + (i - self.radius) * self.square,
                               cy + (j - self.radius) * self.square,
                               self.square, self.square)

    def phase_color(self):
        # Обираємо кольори залежно від фази (в залежності від click_power)
        phase = min(self.click_power // 5 + 1, 5)
        colors = [
            [QColor(100, 200, 255), QColor(60, 179, 113)],
            [QColor(34, 139, 34), QColor(0, 191, 255)],
            [QColor(210, 180, 140), QColor(70, 130, 180)],
            [QColor(240, 248, 255), QColor(70, 130, 180)],
            [QColor(255, 20, 147), QColor(0, 255, 255)]
        ][phase - 1]
        return colors[0] if random.random() < 0.7 else colors[1]

    def mousePressEvent(self, e):
        cy = self.height() // 2 + 100
        pt = cy - self.radius * self.square
        pb = cy + self.radius * self.square

        # Якщо клік по планеті, даємо подвоєний бал, інакше — звичайний
        self.score += self.click_power * 2 if pt <= e.y() <= pb else self.click_power
        self.update_ui()

    def up_click(self):
        # Прокачка кліку (натискаємо кнопку)
        if self.score >= self.click_cost:
            self.score -= self.click_cost
            self.click_power += 1
            self.click_cost += 50
            self.update_ui()
        else:
            self.show_insufficient_funds()

    def up_income(self):
        # Прокачка пасивного доходу (натискаємо кнопку)
        if self.score >= self.income_cost:
            self.score -= self.income_cost
            self.income += 1
            self.income_cost += 100
            self.update_ui()
        else:
            self.show_insufficient_funds()

    def add_income(self):
        # Додаємо пасивний дохід щосекунди
        if self.income > 0:
            self.score += self.income
            self.update_ui()

    def update_ui(self):
        # Оновлюємо текст у всіх підписах і кнопках
        self.score_lbl.setText(f"Бали: {self.score}")
        self.mult_lbl.setText(f"Множник: x{self.click_power}")
        self.inc_lbl.setText(f"Пасивний дохід: +{self.income}/сек")
        self.click_btn.setText(f"Прокачати клік (+1) за {self.click_cost}")
        self.income_btn.setText(f"Прокачати автоклік (+1/сек) за {self.income_cost}")
        self.repaint()

    def show_insufficient_funds(self):
        # Вікно-попередження про недостатню кількість грошей
        msg = QMessageBox(self)
        msg.setWindowTitle("Недостатньо грошей")
        msg.setText("У вас недостатньо грошей для покупки!")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2e2e4d;
                color: #e0e0e0;
                font-size: 16px;
                font-family: Arial;
            }
            QPushButton {
                background-color: #6a5acd;
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7b68ee;
            }
        """)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PlanetClicker()
    w.show()
    sys.exit(app.exec_())
