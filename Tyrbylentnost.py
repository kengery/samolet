import pygame
import math
import random
from dataclasses import dataclass, field, asdict

@dataclass
# Зона турбулентности: сносит самолёт, после выравнивания топливо жжётся вдвое.
class Tyrbylentnost:
    x: float  # центр зоны по X
    y: float  # центр зоны по Y
    dx: int  # сторона квадрата по X
    dy: int  # сторона квадрата по Y
    file: str  # путь из JSON, на экран не выводится

    # Запоминает размер, центр и окно. Картинку не грузит.
    def __init__(self, display, x, y, dx, dy, file):
        self.x=x  # центр по X
        self.y=y  # центр по Y
        self.dx=dx  # ширина квадрата
        self.dy=dy  # высота квадрата
        self.file=file  # файл из JSON
        self.napravlenie=random.uniform(0, 360)  # градусы сноса на этот заход карты
        self.display=display  # окно pygame
        # Цвет (красный, зелёный, синий, прозрачность): 0 — невидно, 255 — как сплошная краска.
        self.zalivka = (230, 190, 90, 80)  # янтарная заливка, слабо прозрачная
        self.ramka = (230, 190, 90, 200)  # та же зона, рамка почти непрозрачная

    # Рисует полупрозрачный квадрат вокруг центра.
    def render(self):
        # Отдельный холст размером с зону: на нём рисуем, потом кладём на карту.
        # SRCALPHA — режим «можно задавать прозрачность пикселей», иначе заливка перекроет радар.
        kvadrat = pygame.Surface((int(self.dx), int(self.dy)), pygame.SRCALPHA)
        kvadrat.fill(self.zalivka)  # залитый квадрат: сквозь него виден фон
        pygame.draw.rect(kvadrat, self.ramka, kvadrat.get_rect(), 2)  # обводка по краю, 2 пикселя
        levo = self.x - (self.dx / 2)  # левый край квадрата на экране
        verh = self.y - (self.dy / 2)  # верхний край квадрата на экране
        self.display.blit(kvadrat, (levo, verh))  # перенос холста на окно игры

    # True, если центр самолёта попал в зону ветра.
    def select(self,x,y,dx,dy)->bool:
        x1 = x + dx / 2  # центр самолёта X
        y1 = y + dy / 2  # центр самолёта Y
        x2 = self.x  # центр зоны X
        y2 = self.y  # центр зоны Y
        # находим растояние между центром самолёта и плохой погодой
        d = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))  # расстояние до центра зоны
        if dx + self.dx/3 >= d or dy + self.dy/3 >= d:
            return True
        else:
            return False
