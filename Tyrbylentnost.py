import pygame
import math
import random
import Figyrs
from dataclasses import dataclass, field, asdict

SKOROST_ZONY = 0.04  # пиксели за кадр, сдвиг центра по ветру зоны
SKOROST_VISOTY = 0.08  # метры за кадр, сдвиг слоя высоты
VISOTA_SLOIA = 305  # зона берёт самолёт, если разница высот меньше этого
VISOTA_START_MIN = 305  # нижняя высота слоя на старте карты
VISOTA_START_MAX = 3048  # верхняя высота слоя на старте карты

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
        self.napravlenie=random.uniform(0, 360)  # градусы сноса и хода зоны на этот заход карты
        self.visota=random.uniform(VISOTA_START_MIN, VISOTA_START_MAX)  # высота слоя, метры
        self.izvestna = False  # True, если зону уже доложили и её рисуем
        self.doklad_x = self.x  # X отметки доклада
        self.doklad_y = self.y  # Y отметки доклада
        self.doklad_visota = self.visota  # высота слоя в докладе, метры
        if random.random() < 0.5:
            self.hod_visota = SKOROST_VISOTY  # слой каждый кадр поднимается
        else:
            self.hod_visota = -SKOROST_VISOTY  # слой каждый кадр опускается
        self.display=display  # окно pygame
        # Цвет (красный, зелёный, синий, прозрачность): 0 — невидно, 255 — как сплошная краска.
        self.zalivka = (230, 190, 90, 80)  # янтарная заливка, слабо прозрачная
        self.ramka = (230, 190, 90, 200)  # та же зона, рамка почти непрозрачная

    # Ставит отметку доклада на текущие место и высоту зоны.
    def doklad(self):
        self.izvestna = True
        self.doklad_x = self.x
        self.doklad_y = self.y
        self.doklad_visota = self.visota

    # Рисует полупрозрачный квадрат отметки доклада.
    def render(self):
        if self.izvestna == False:
            return
        # Отдельный холст размером с зону: на нём рисуем, потом кладём на карту.
        # SRCALPHA — режим «можно задавать прозрачность пикселей», иначе заливка перекроет радар.
        kvadrat = pygame.Surface((int(self.dx), int(self.dy)), pygame.SRCALPHA)
        kvadrat.fill(self.zalivka)  # залитый квадрат: сквозь него виден фон
        pygame.draw.rect(kvadrat, self.ramka, kvadrat.get_rect(), 2)  # обводка по краю, 2 пикселя
        levo = self.doklad_x - (self.dx / 2)  # левый край отметки на экране
        verh = self.doklad_y - (self.dy / 2)  # верхний край отметки на экране
        self.display.blit(kvadrat, (levo, verh))  # перенос холста на окно игры
        Figyrs.print_text(self.display, self.doklad_x, self.doklad_y, 18, (70, 220, 230), f"{int(round(self.doklad_visota))} м")

    # Сдвигает центр по ветру зоны и высоту слоя. Края экрана не разворачивают.
    def move(self):
        rad = math.radians(self.napravlenie)  # направление ветра в радианах
        self.x = self.x + math.cos(rad) * SKOROST_ZONY
        self.y = self.y - math.sin(rad) * SKOROST_ZONY
        self.visota = self.visota + self.hod_visota

    # True, если центр самолёта попал в квадрат и в слой высоты зоны.
    def select(self,x,y,dx,dy,visota)->bool:
        x1 = x + dx / 2  # центр самолёта X
        y1 = y + dy / 2  # центр самолёта Y
        x2 = self.x  # центр зоны X
        y2 = self.y  # центр зоны Y
        # находим растояние между центром самолёта и плохой погодой
        d = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))  # расстояние до центра зоны
        na_karte = dx + self.dx/3 >= d or dy + self.dy/3 >= d  # близко на карте
        na_visote = math.fabs(visota - self.visota) < VISOTA_SLOIA  # самолёт в слое зоны
        if na_karte and na_visote:
            return True
        else:
            return False
