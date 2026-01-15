import pygame
import math
from dataclasses import dataclass, field, asdict

@dataclass
class Pogoda:
    x: float
    y: float
    dx: int
    dy: int
    file: str

    def __init__(self, display, x, y, dx, dy, file):
        self.x=x
        self.y=y
        self.dx=dx
        self.dy=dy
        self.file=file
        self.display=display
        image_file=pygame.image.load(file)
        self.image = pygame.transform.scale(image_file, (self.dx, self.dy))

    def render(self):
        self.display.blit(self.image, (self.x-(self.dx/2), self.y-(self.dy/2)))

    def select(self,x,y,dx,dy)->bool:
        x1 = x + dx / 2
        y1 = y + dy / 2
        x2 = self.x
        y2 = self.y
        # находим растояние между центром самолёта и плохой погодой
        d = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        if dx + self.dx/3 >= d or dy + self.dy/3 >= d:
            return True
        else:
            return False