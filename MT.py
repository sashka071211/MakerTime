import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class PlanetClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Planet Clicker")
        self.showFullScreen()
        self.setStyleSheet("background:#1e1e2f; color: white;")
        self.score, self.click_power, self.income = 0, 1, 0
        self.click_cost, self.income_cost = 50, 100
        self.grid_size, self.square, self.radius = 19, 24, 9
        self.daily_bonus_available = True
        self.make_ui()
        self.timer = QTimer(self, timeout=self.add_income)
        self.timer.start(1000)

    def make_ui(self):
        def label(t, s):
            l = QLabel(t)
            l.setFont(QFont("Arial", s))
            l.setStyleSheet("color: white")
            return l
        def btn(t, fn):
            b = QPushButton(t)
            b.setStyleSheet(
                "QPushButton {background:#6a5acd; color:white; font-size:20px; padding:10px; border-radius:10px}"
                "QPushButton:hover {background:#7b68ee;}"
            )
            b.clicked.connect(fn)
            return b

        self.score_lbl = label("", 24)
        self.mult_lbl = label("", 18)
        self.inc_lbl = label("", 18)
        self.click_btn = btn("", self.up_click)
        self.income_btn = btn("", self.up_income)

        # Кнопка "Подарунок" з картинкою коробки
        self.gift_btn = QPushButton()
        self.gift_btn.setToolTip("Отримати щоденний бонус!")
        self.gift_btn.setFixedSize(80, 80)
        gift_pix = QPixmap("gift.png")
        if gift_pix.isNull():
            print("Помилка: не знайдено файл gift.png")
        self.gift_btn.setIcon(QIcon(gift_pix))
        self.gift_btn.setIconSize(gift_pix.rect().size())
        self.gift_btn.setStyleSheet("background: transparent; border: none;")
        self.gift_btn.clicked.connect(self.open_bonus_case)

        v = QVBoxLayout()
        for w in [self.score_lbl, self.mult_lbl, self.inc_lbl, self.click_btn, self.income_btn, self.gift_btn]:
            v.addWidget(w)
        v.addStretch()
        self.setLayout(v)
        self.update_ui()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2 + 100
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if ((i - self.radius) ** 2 + (j - self.radius) ** 2) ** 0.5 <= self.radius:
                    p.setBrush(self.phase_color())
                    p.setPen(Qt.NoPen)
                    p.drawRect(cx + (i - self.radius) * self.square, cy + (j - self.radius) * self.square, self.square, self.square)

    def phase_color(self):
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
        self.score += self.click_power * 1 if pt <= e.y() <= pb else self.click_power
        self.update_ui()

    def up_click(self):
        if self.score >= self.click_cost:
            self.score -= self.click_cost
            self.click_power += 1
            self.click_cost += 50
            self.update_ui()
        else:
            self.show_insufficient_funds()

    def up_income(self):
        if self.score >= self.income_cost:
            self.score -= self.income_cost
            self.income += 1
            self.income_cost += 100
            self.update_ui()
        else:
            self.show_insufficient_funds()

    def add_income(self):
        if self.income > 0:
            self.score += self.income
            self.update_ui()

    def update_ui(self):
        self.score_lbl.setText(f"Бали: {self.score}")
        self.mult_lbl.setText(f"Множник: x{self.click_power}")
        self.inc_lbl.setText(f"Пасивний дохід: +{self.income}/сек")
        self.click_btn.setText(f"Прокачати клік (+1) за {self.click_cost}")
        self.income_btn.setText(f"Прокачати автоклік (+1/сек) за {self.income_cost}")
        self.repaint()

    def show_insufficient_funds(self):
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

    def open_bonus_case(self):
        if not self.daily_bonus_available:
            QMessageBox.information(self, "Щоденний бонус", "Ви вже отримали бонус сьогодні. Спробуйте завтра!")
            return

        self.prizes = [
            ("+100 балів", lambda: self.add_points(100)),
            ("+1 множник кліку", lambda: self.add_click_power(1)),
            ("+1 пасивний дохід", lambda: self.add_income_power(1)),
            ("+200 балів", lambda: self.add_points(200)),
            ("+2 множник кліку", lambda: self.add_click_power(2)),
            ("+3 пасивний дохід", lambda: self.add_income_power(3)),
        ]

        dialog = QDialog(self)
        dialog.setWindowTitle("Щоденний бонус - Колесо Фортуни")
        dialog.setStyleSheet("background:#1e1e2f; color: white;")
        dialog.showFullScreen()

        layout = QVBoxLayout(dialog)

        # Фон сундука (картинка)
        chest_pix = QPixmap("chest.png")
        if chest_pix.isNull():
            print("Помилка: не знайдено файл chest.png")
            # Якщо картинки немає, зробимо фон градієнтом
            palette = dialog.palette()
            gradient = QLinearGradient(0, 0, 0, dialog.height())
            gradient.setColorAt(0, QColor("#3a2a0f"))
            gradient.setColorAt(1, QColor("#1e1e2f"))
            brush = QBrush(gradient)
            palette.setBrush(QPalette.Window, brush)
            dialog.setPalette(palette)
        else:
            # Відображаємо картинку як лейбл на фон
            bg_label = QLabel(dialog)
            bg_label.setPixmap(chest_pix.scaled(dialog.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            bg_label.setGeometry(0, 0, dialog.width(), dialog.height())
            bg_label.lower()

        # Надпис для анімації
        self.animated_label = QLabel("")
        self.animated_label.setAlignment(Qt.AlignCenter)
        self.animated_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.animated_label.setStyleSheet("background: rgba(0,0,0,0.5); padding: 20px; border-radius: 15px;")
        layout.addWidget(self.animated_label, alignment=Qt.AlignCenter)

        # Кнопка закриття після анімації
        self.close_btn = QPushButton("Закрити")
        self.close_btn.setFont(QFont("Arial", 20))
        self.close_btn.setStyleSheet(
            "QPushButton {background:#6a5acd; color:white; padding:10px; border-radius:10px;}"
            "QPushButton:hover {background:#7b68ee;}"
        )
        self.close_btn.clicked.connect(dialog.accept)
        self.close_btn.setVisible(False)
        layout.addWidget(self.close_btn, alignment=Qt.AlignCenter)

        self.prize_index = 0
        self.cycles = 0
        self.max_cycles = 30

        self.timer_anim = QTimer()
        self.timer_anim.timeout.connect(self.animate_prizes)
        self.timer_anim.start(100)

        self.dialog = dialog
        dialog.exec_()

    def animate_prizes(self):
        prize_name, _ = self.prizes[self.prize_index]
        self.animated_label.setText(prize_name)
        self.prize_index = (self.prize_index + 1) % len(self.prizes)
        self.cycles += 1
        if self.cycles >= self.max_cycles:
            self.timer_anim.stop()
            final_prize_index = random.randint(0, len(self.prizes) - 1)
            prize_name, prize_func = self.prizes[final_prize_index]
            self.animated_label.setText(f"🎉 Вітаємо! Ви отримали: {prize_name} 🎉")
            prize_func()
            self.daily_bonus_available = False
            self.close_btn.setVisible(True)

    def add_points(self, amount):
        self.score += amount
        self.update_ui()

    def add_click_power(self, amount):
        self.click_power += amount
        self.update_ui()

    def add_income_power(self, amount):
        self.income += amount
        self.update_ui()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PlanetClicker()
    w.show()
    sys.exit(app.exec_())
