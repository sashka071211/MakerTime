import sys                          # Для роботи з системними аргументами та виходом із програми
import random                       # Для генерації випадкових чисел (для кольорів планети)
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt

# Основний клас гри, успадковуємо від QWidget — базового вікна
class PlanetClicker(QWidget):
    def __init__(self):
        super().__init__()  # Ініціалізація QWidget

        # Налаштування вікна: заголовок, повноекранний режим, фон
        self.setWindowTitle("🌍 Planet Clicker")
        self.showMaximized()
        self.setStyleSheet("background-color: #1e1e2f;")  # Темний фон

        # Початкові змінні для гри
        self.score = 0                  # Кількість набраних балів
        self.click_power = 1            # Сила кліку (множник)
        self.upgrade_cost = 50          # Вартість прокачки кліку

        # Налаштування планети: сітка з квадратів
        self.grid_size = 31             # Кількість квадратів по ширині та висоті планети
        self.square_size = 20           # Розмір квадратика в пікселях
        self.planet_radius = self.grid_size // 2  # Радіус планети — наполовину від розміру сітки

        # Лейбл для відображення балів
        self.score_label = QLabel(f"Бали: {self.score}")
        self.score_label.setFont(QFont("Arial", 28))    # Встановлюємо шрифт і розмір
        self.score_label.setStyleSheet("color: white;") # Білий колір тексту

        # Лейбл для відображення потужності кліку
        self.multiplier_label = QLabel(f"Множник: x{self.click_power}")
        self.multiplier_label.setFont(QFont("Arial", 24))
        self.multiplier_label.setStyleSheet("color: #7fffd4;")  # Світло-бірюзовий колір

        # Кнопка для прокачки кліку
        self.upgrade_button = QPushButton(f"Прокачати (+1) за {self.upgrade_cost}")
        # Стиль кнопки — фіолетовий фон, білий текст, округлені кути
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
        # Підключаємо натискання кнопки до функції апгрейду
        self.upgrade_button.clicked.connect(self.upgrade_click)

        # Вертикальний лейаут для розташування елементів
        layout = QVBoxLayout()
        layout.addWidget(self.score_label)       # Додаємо лейбл балів зверху
        layout.addWidget(self.multiplier_label)  # Додаємо лейбл множника під ним
        layout.addStretch()                       # Порожній простір (щоб кнопка була внизу)
        layout.addWidget(self.upgrade_button)    # Кнопка внизу
        self.setLayout(layout)                    # Застосовуємо лейаут до вікна

    # Метод для малювання планети на екрані
    def paintEvent(self, event):
        painter = QPainter(self)                       # Створюємо об’єкт для малювання
        painter.setRenderHint(QPainter.Antialiasing)  # Увімкнення згладжування

        # Центруємо планету по ширині вікна
        screen_width = self.width()
        start_x = screen_width // 2 - (self.grid_size * self.square_size) // 2
        start_y = 120    # Відступ зверху для планети
        center = self.grid_size // 2

        # Проходимо по кожному квадрату сітки
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Обчислюємо відстань від центру планети
                dist = ((i - center) ** 2 + (j - center) ** 2) ** 0.5
                # Малюємо квадрат, якщо він у межах радіуса планети
                if dist <= self.planet_radius:
                    color = self.get_color_by_phase()   # Отримуємо колір залежно від фази
                    painter.setBrush(color)             # Встановлюємо колір заливки
                    painter.setPen(Qt.NoPen)            # Без контуру квадратика
                    # Малюємо квадрат у відповідній позиції
                    painter.drawRect(start_x + i * self.square_size,
                                     start_y + j * self.square_size,
                                     self.square_size, self.square_size)

    # Функція визначення кольору квадратів планети в залежності від фази
    def get_color_by_phase(self):
        phase = self.get_planet_phase()  # Визначаємо фазу планети

        # П’ять різних фаз із різними кольорами (вода, земля, пустеля, лід, неон)
        if phase == 1:
            # Переважно вода (синій), 25% земля (зелений)
            return QColor(100, 200, 255) if random.random() < 0.75 else QColor(60, 179, 113)
        elif phase == 2:
            # Більше зелені (рослинність)
            return QColor(60, 179, 113) if random.random() < 0.7 else QColor(100, 200, 255)
        elif phase == 3:
            # Пустельні кольори (пісок і світло-зелений)
            return QColor(237, 201, 175) if random.random() < 0.7 else QColor(189, 183, 107)
        elif phase == 4:
            # Льодовики (білий та блакитний)
            return QColor(240, 248, 255) if random.random() < 0.8 else QColor(173, 216, 230)
        else:
            # Неонові яскраві кольори для кінцевої фази
            colors = [QColor(255, 20, 147), QColor(0, 255, 255), QColor(255, 69, 0)]
            return random.choice(colors)

    # Визначаємо фазу планети залежно від потужності кліку
    def get_planet_phase(self):
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

    # Обробка кліку миші
    def mousePressEvent(self, event):
        x, y = event.x(), event.y()  # Координати кліку

        screen_width = self.width()
        start_x = screen_width // 2 - (self.grid_size * self.square_size) // 2
        start_y = 120
        end_x = start_x + self.grid_size * self.square_size
        end_y = start_y + self.grid_size * self.square_size
        center = self.grid_size // 2

        # Перевіряємо чи клік був в межах планети
        if start_x <= x <= end_x and start_y <= y <= end_y:
            i = (x - start_x) // self.square_size
            j = (y - start_y) // self.square_size
            dist = ((i - center) ** 2 + (j - center) ** 2) ** 0.5
            if dist <= self.planet_radius:
                # Подвоюємо бали, якщо клік по планеті
                self.score += self.click_power * 2
            else:
                # Якщо клік поза планетою, але в межах сітки — звичайний бонус
                self.score += self.click_power
        else:
            # Клік поза планетою дає звичайний бонус
            self.score += self.click_power

        self.update_ui()  # Оновлюємо відображення

    # Функція для апгрейду кліку
    def upgrade_click(self):
        if self.score >= self.upgrade_cost:   # Якщо достатньо балів
            self.score -= self.upgrade_cost   # Віднімаємо вартість прокачки
            self.click_power += 1              # Збільшуємо потужність кліку
            self.upgrade_cost += 50            # Збільшуємо вартість наступного апгрейду
            self.planet_radius += 0.5          # Збільшуємо радіус планети (прокачка планети)
            # Обмежуємо максимальний розмір планети радіусом сітки
            if self.planet_radius > self.grid_size // 2:
                self.planet_radius = self.grid_size // 2

            self.update_ui()  # Оновлюємо всі написи та перемальовуємо

    # Оновлення текстів на кнопках і лейблах, а також перемальовування
    def update_ui(self):
        self.score_label.setText(f"Бали: {self.score}")
        self.multiplier_label.setText(f"Множник: x{self.click_power}")
        self.upgrade_button.setText(f"Прокачати (+1) за {self.upgrade_cost}")
        self.repaint()  # Перемальовуємо планету для оновлення кольорів та розміру

# Запуск програми
if __name__ == "__main__":
    app = QApplication(sys.argv)      # Створюємо застосунок Qt
    window = PlanetClicker()          # Створюємо головне вікно гри
    window.show()                    # Показуємо вікно
    sys.exit(app.exec_())             # Запускаємо цикл обробки подій Qt
