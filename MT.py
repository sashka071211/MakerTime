import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt


class PlanetClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Planet Clicker")
        self.showMaximized()
        self.setStyleSheet("background-color: #1e1e2f;")

        self.score = 0
        self.click_power = 1
        self.upgrade_cost = 50

        self.grid_size = 31
        self.square_size = 20
        self.planet_radius = self.grid_size // 2

        self.score_label = QLabel(f"Бали: {self.score}")
        self.score_label.setFont(QFont("Arial", 28))
        self.score_label.setStyleSheet("color: white;")

        self.multiplier_label = QLabel(f"Множник: x{self.click_power}")
        self.multiplier_label.setFont(QFont("Arial", 24))
        self.multiplier_label.setStyleSheet("color: #7fffd4;")

        self.upgrade_button = QPushButton(f"Прокачати (+1) за {self.upgrade_cost}")
        self.upgrade_button.setStyleSheet("""
            QPushButton {
                background-color: #6a5acd;
                color: white;
                font-size: 22px;
                padding: 12px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #7b68ee;
            }
        """)
        self.upgrade_button.clicked.connect(self.upgrade_click)

        layout = QVBoxLayout()
        layout.addWidget(self.score_label)
        layout.addWidget(self.multiplier_label)
        layout.addStretch()
        layout.addWidget(self.upgrade_button)
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        screen_width = self.width()
        start_x = screen_width // 2 - (self.grid_size * self.square_size) // 2
        start_y = 120
        center = self.grid_size // 2

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                dist = ((i - center) ** 2 + (j - center) ** 2) ** 0.5
                if dist <= self.planet_radius:
                    color = self.get_color_by_phase()
                    painter.setBrush(color)
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(start_x + i * self.square_size,
                                     start_y + j * self.square_size,
                                     self.square_size, self.square_size)

    def get_color_by_phase(self):
        """ Вибір кольору в залежності від фази планети """
        phase = self.get_planet_phase()

        if phase == 1:
            return QColor(100, 200, 255) if random.random() < 0.75 else QColor(60, 179, 113)
        elif phase == 2:
            return QColor(34, 139, 34) if random.random() < 0.7 else QColor(0, 191, 255)
        elif phase == 3:
            rand = random.random()
            if rand < 0.5:
                return QColor(210, 180, 140)  # пустеля
            elif rand < 0.8:
                return QColor(70, 130, 180)  # вода
            else:
                return QColor(34, 139, 34)   # зелень
        elif phase == 4:
            rand = random.random()
            if rand < 0.4:
                return QColor(240, 248, 255)  # льодовик
            elif rand < 0.7:
                return QColor(70, 130, 180)  # вода
            else:
                return QColor(34, 139, 34)   # зелень
        else:
            rand = random.random()
            if rand < 0.4:
                return QColor(255, 20, 147)  # фантастичні рожеві
            elif rand < 0.7:
                return QColor(0, 255, 255)   # неоново-блакитні
            else:
                return QColor(147, 112, 219) # пурпурові

    def get_planet_phase(self):
        """ Повертає фазу планети за множником """
        if self.click_power < 5:
            return 1
        elif self.click_power < 10:
            return 2
        elif self.click_power < 15:
            return 3
        elif self.click_power < 20:
            return 4
        else:
            return 5

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        screen_width = self.width()
        start_x = screen_width // 2 - (self.grid_size * self.square_size) // 2
        start_y = 120
        end_x = start_x + self.grid_size * self.square_size
        end_y = start_y + self.grid_size * self.square_size
        center = self.grid_size // 2

        if start_x <= x <= end_x and start_y <= y <= end_y:
            i = (x - start_x) // self.square_size
            j = (y - start_y) // self.square_size
            dist = ((i - center) ** 2 + (j - center) ** 2) ** 0.5
            if dist <= self.planet_radius:
                self.score += self.click_power * 2
            else:
                self.score += self.click_power
        else:
            self.score += self.click_power

        self.update_ui()

    def upgrade_click(self):
        if self.score >= self.upgrade_cost:
            self.score -= self.upgrade_cost
            self.click_power += 1
            self.upgrade_cost += 50
            self.planet_radius += 0.5
            if self.planet_radius > self.grid_size // 2:
                self.planet_radius = self.grid_size // 2
            self.update_ui()

    def update_ui(self):
        self.score_label.setText(f"Бали: {self.score}")
        self.multiplier_label.setText(f"Множник: x{self.click_power}")
        self.upgrade_button.setText(f"Прокачати (+1) за {self.upgrade_cost}")
        self.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlanetClicker()
    window.show()
    sys.exit(app.exec_())
