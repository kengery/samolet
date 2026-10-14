import pygame
import math
from dataclasses import dataclass, field, asdict

@dataclass
# Зона турбулентности: самолёт не теряется, топливо жжётся быстрее.
class Tyrbylentnost:
    x: float  # центр зоны по X
    y: float  # центр зоны по Y
    dx: int  # ширина картинки
    dy: int  # высота картинки
    file: str  # путь к картинке зоны

    # Грузит картинку ветра и запоминает размер и центр.
    def __init__(self, display, x, y, dx, dy, file):
        self.x=x  # центр по X
        self.y=y  # центр по Y
        self.dx=dx  # ширина
        self.dy=dy  # высота
        self.file=file  # файл картинки
        self.display=display  # окно pygame
        image_file=pygame.image.load(file)  # исходный файл
        self.image = pygame.transform.scale(image_file, (self.dx, self.dy))  # картинка нужного размера

    # Рисует зону вокруг её центра.
    def render(self):
        self.display.blit(self.image, (self.x-(self.dx/2), self.y-(self.dy/2)))

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
