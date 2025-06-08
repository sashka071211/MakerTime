import sys, random, json, os
from datetime import datetime, timedelta
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

        # Кожен світ має свої унікальні прокачки
        self.worlds = {
            1: {
                "name": "Земля",
                "click_bonus": 1,
                "color1": QColor(100, 200, 255),
                "color2": QColor(60, 179, 113),
                "click_power": 1,
                "income": 0,
            },
            2: {
                "name": "Марс",
                "click_bonus": 2,
                "color1": QColor(255, 100, 100),
                "color2": QColor(200, 50, 50),
                "click_power": 2,
                "income": 1,
            },
            3: {
                "name": "Венера",
                "click_bonus": 3,
                "color1": QColor(255, 215, 0),
                "color2": QColor(255, 140, 0),
                "click_power": 3,
                "income": 2,
            },
        }
        self.current_world = 1

        self.bonus_speed = 1
        self.double_chance = 0.0

        # Магазин (універсальний)
        self.shop_items = {
            "click_power": {"level": 0, "base_cost": 50, "cost": 50, "power": 1, "desc": "Підвищення множника кліку"},
            "income": {"level": 0, "base_cost": 100, "cost": 100, "power": 1, "desc": "Покращення пасивного доходу"},
            "bonus_speed": {"level": 0, "base_cost": 500, "cost": 500, "power": 1, "desc": "Прискорення щоденного бонусу"},
            "double_chance": {"level": 0, "base_cost": 1000, "cost": 1000, "power": 0.05, "desc": "Шанс подвоїти бали"},
        }

        self.daily_bonus_available = True
        self.bonus_time = None

        self.grid_size, self.square, self.radius = 19, 24, 9

        self.make_ui()
        self.load_game()

        self.timer = QTimer(self, timeout=self.add_income)
        self.timer.start(1000)

    def make_ui(self):
        def label(t, s):
            l = QLabel(t)
            l.setFont(QFont("Arial", s))
            l.setStyleSheet("color: white")
            return l

        self.score_lbl = label("", 36)
        self.mult_lbl = label("", 20)
        self.inc_lbl = label("", 20)

        # Верхня панель з кнопками
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        self.gift_btn = QPushButton("Щоденний бонус")
        self.gift_btn.setFixedSize(160, 45)
        self.gift_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffcc00;
                color: #333333;
                font-weight: bold;
                font-size: 16px;
                border-radius: 12px;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: #ffd633;
            }
        """)
        self.gift_btn.clicked.connect(self.open_bonus_case)
        top_layout.addWidget(self.gift_btn)

        self.shop_btn = QPushButton("🛒 Магазин")
        self.shop_btn.setFixedSize(200, 55)
        self.shop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
        """)
        self.shop_btn.clicked.connect(self.open_shop)
        top_layout.addWidget(self.shop_btn)

        # Кнопка виходу
        self.exit_btn = QPushButton("Вийти")
        self.exit_btn.setFixedSize(100, 45)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a5acd;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #7b68ee;
            }
        """)
        self.exit_btn.clicked.connect(self.exit_app)
        top_layout.addWidget(self.exit_btn)

        # Випадаючий список для вибору світу
        self.world_combo = QComboBox()
        self.world_combo.setFixedSize(180, 45)
        for wid, wdata in self.worlds.items():
            self.world_combo.addItem(wdata['name'], userData=wid)
        self.world_combo.setCurrentIndex(self.current_world - 1)
        self.world_combo.currentIndexChanged.connect(self.change_world)
        top_layout.addWidget(self.world_combo)

        v = QVBoxLayout()
        v.addLayout(top_layout)

        # Головний заголовок
        self.title_lbl = QLabel("🌍 Вітаємо в Planet Clicker!")
        self.title_lbl.setFont(QFont("Arial", 40, QFont.Bold))
        self.title_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_lbl.setStyleSheet(
            "color: #ffd700; margin-top: 40px; margin-bottom: 10px; text-shadow: 1px 1px 2px black;"
        )

        # Опис гри
        self.game_desc_lbl = QLabel(
            "Клікай по планеті, збирай бали і прокачуй свої здібності в Магазині!\n"
            "Отримуй щоденний бонус і розвивай свій множник та пасивний дохід.\n"
            "Насолоджуйся красивим інтерфейсом і веселою грою!"
        )
        self.game_desc_lbl.setFont(QFont("Arial", 18))
        self.game_desc_lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.game_desc_lbl.setWordWrap(True)
        self.game_desc_lbl.setStyleSheet("color: #aaaaaa; margin: 0 30px 0 30px;")

        # Опис світу — окремий блок праворуч
        self.desc_lbl = QLabel()
        self.desc_lbl.setFont(QFont("Arial", 18))
        self.desc_lbl.setAlignment(Qt.AlignCenter)
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("color: #aaaaaa; margin: 0 50px 0 50px;")
        self.update_world_text()

        # Горизонтальний layout для опису і світу
        hlayout = QHBoxLayout()
        left_v = QVBoxLayout()
        left_v.addWidget(self.title_lbl)
        left_v.addWidget(self.game_desc_lbl)
        hlayout.addLayout(left_v, 3)
        hlayout.addWidget(self.desc_lbl, 2)  # опис світу праворуч

        hr = QFrame()
        hr.setFixedHeight(4)
        hr.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #4caf50, stop:1 #81c784);
            border-radius: 2px;
            margin-top: 30px;
            margin-bottom: 40px;
            margin-left: 100px;
            margin-right: 100px;
        """)

        v.addLayout(hlayout)
        v.addWidget(hr)

        v.addWidget(self.score_lbl, alignment=Qt.AlignCenter)
        v.addWidget(self.mult_lbl, alignment=Qt.AlignCenter)
        v.addWidget(self.inc_lbl, alignment=Qt.AlignCenter)

        v.addStretch()
        self.setLayout(v)
        self.update_ui()

    def exit_app(self):
        reply = QMessageBox.question(
            self, 'Вихід', "Ви дійсно хочете вийти?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QApplication.quit()

    def change_world(self, index):
        wid = self.world_combo.itemData(index)
        if wid in self.worlds:
            self.current_world = wid
            self.update_world_text()
            self.update_ui()

    def update_world_text(self):
        self.desc_lbl.setText(
            f"Поточний світ: {self.worlds[self.current_world]['name']}\n"
            f"(Кліки ×{self.worlds[self.current_world]['click_bonus']})"
        )

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2 + 100
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if ((i - self.radius) ** 2 + (j - self.radius) ** 2) ** 0.5 <= self.radius:
                    color1 = self.worlds[self.current_world]['color1']
                    color2 = self.worlds[self.current_world]['color2']
                    p.setBrush(color1 if random.random() < 0.7 else color2)
                    p.setPen(Qt.NoPen)
                    p.drawRect(cx + (i - self.radius) * self.square, cy + (j - self.radius) * self.square, self.square, self.square)

    def mousePressEvent(self, e):
        cy = self.height() // 2 + 100
        pt = cy - self.radius * self.square
        pb = cy + self.radius * self.square
        if pt <= e.y() <= pb:
            base_click = self.shop_items['click_power']['power'] * self.worlds[self.current_world]['click_bonus'] + self.worlds[self.current_world]['click_power'] - 1
            # Враховуємо покупки
            base_click += (self.click_power - 1)
            if random.random() < self.double_chance:
                base_click *= 2
            self.score += int(base_click)
            self.update_ui()

    def add_income(self):
        if self.income > 0:
            self.score += self.income + self.worlds[self.current_world]['income'] + self.shop_items['income']['power'] * self.shop_items['income']['level']
            self.update_ui()

    def update_ui(self):
        self.score_lbl.setText(f"Бали: {self.score}")
        self.mult_lbl.setText(
            f"Множник: x{self.click_power} (Світовий бонус ×{self.worlds[self.current_world]['click_bonus']})"
        )
        self.inc_lbl.setText(f"Пасивний дохід: +{self.income + self.worlds[self.current_world]['income']}/сек")
        self.repaint()
        self.save_game()

    def open_bonus_case(self):
        if not self.daily_bonus_available:
            QMessageBox.information(self, "Щоденний бонус", "Ви вже отримали бонус сьогодні. Чекайте наступного дня!")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("🎁 Щоденний бонус")
        dlg.setFixedSize(400, 300)
        dlg.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d8bfd8, stop:1 #dda0dd); color: black;")

        vbox = QVBoxLayout()
        label = QLabel("Обирайте свій бонус:")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(label)

        def choose_bonus(bonus):
            if bonus == "score":
                self.score += 5000 * self.bonus_speed
            elif bonus == "click":
                self.click_power += 5
            elif bonus == "income":
                self.income += 10
            self.daily_bonus_available = False
            self.bonus_time = datetime.now()
            self.update_ui()
            QMessageBox.information(dlg, "Вітаємо!", f"Ви отримали бонус: {bonus}!")
            dlg.accept()

        btn_score = QPushButton("5000 балів")
        btn_score.clicked.connect(lambda: choose_bonus("score"))
        btn_click = QPushButton("+5 множника кліку")
        btn_click.clicked.connect(lambda: choose_bonus("click"))
        btn_income = QPushButton("+10 пасивного доходу")
        btn_income.clicked.connect(lambda: choose_bonus("income"))

        for btn in [btn_score, btn_click, btn_income]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("background: #7b68ee; color: white; font-weight: bold; font-size: 18px; border-radius: 10px; margin: 10px;")
            vbox.addWidget(btn)

        dlg.setLayout(vbox)
        dlg.exec_()

    def open_shop(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("🛒 Магазин")
        dlg.setFixedSize(400, 450)
        dlg.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4169e1, stop:1 #00bfff); color: white;")

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Покращуйте свої здібності:"))
        vbox.addSpacing(10)

        for key, item in self.shop_items.items():
            hbox = QHBoxLayout()
            lbl = QLabel(f"{item['desc']}: Рівень {item['level']}, Ціна: {item['cost']} балів")
            lbl.setFont(QFont("Arial", 14))
            hbox.addWidget(lbl)

            btn = QPushButton("Купити")
            btn.setFixedWidth(80)
            btn.setStyleSheet("background: #32cd32; color: black; font-weight: bold; border-radius: 8px;")
            btn.clicked.connect(lambda checked, k=key: self.buy_upgrade(k))
            hbox.addWidget(btn)
            vbox.addLayout(hbox)

        dlg.setLayout(vbox)
        dlg.exec_()

    def buy_upgrade(self, key):
        item = self.shop_items[key]
        if self.score >= item["cost"]:
            self.score -= item["cost"]
            item["level"] += 1
            item["cost"] = int(item["base_cost"] * (1.5 ** item["level"]))
            if key == "click_power":
                self.click_power += item["power"]
            elif key == "income":
                self.income += item["power"]
            elif key == "bonus_speed":
                self.bonus_speed += item["power"]
            elif key == "double_chance":
                self.double_chance = min(self.double_chance + item["power"], 1.0)
            self.update_ui()
        else:
            QMessageBox.warning(self, "Недостатньо балів", "У вас недостатньо балів для покупки.")

    def save_game(self):
        data = {
            "score": self.score,
            "click_power": self.click_power,
            "income": self.income,
            "bonus_speed": self.bonus_speed,
            "double_chance": self.double_chance,
            "daily_bonus_available": self.daily_bonus_available,
            "bonus_time": self.bonus_time.isoformat() if self.bonus_time else None,
            "shop_items": self.shop_items,
            "current_world": self.current_world,
        }
        with open("savegame.json", "w") as f:
            json.dump(data, f)

    def load_game(self):
        if os.path.exists("savegame.json"):
            with open("savegame.json", "r") as f:
                data = json.load(f)
                self.score = data.get("score", 0)
                self.click_power = data.get("click_power", 1)
                self.income = data.get("income", 0)
                self.bonus_speed = data.get("bonus_speed", 1)
                self.double_chance = data.get("double_chance", 0.0)
                self.daily_bonus_available = data.get("daily_bonus_available", True)
                bonus_time = data.get("bonus_time")
                self.bonus_time = datetime.fromisoformat(bonus_time) if bonus_time else None
                self.shop_items = data.get("shop_items", self.shop_items)
                self.current_world = data.get("current_world", 1)
                self.world_combo.setCurrentIndex(self.current_world - 1)
                self.update_ui()
                # Перевірка часу бонусу
                if self.bonus_time:
                    if datetime.now() - self.bonus_time > timedelta(days=1):
                        self.daily_bonus_available = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlanetClicker()
    window.show()
    sys.exit(app.exec_())
