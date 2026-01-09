import pygame
import math
from dataclasses import dataclass, field, asdict

@dataclass
class Tyrbylentnost:
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
        self.display.blit(self.image, (self.x, self.y))

    def select(self,x,y,dx,dy,xradius,yradius)->bool:
        x1 = x + dx / 2
        y1 = y + dy / 2
        x2 = self.x
        y2 = self.y
        # находим растояние между центром самолёта и турбулентности
        d = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        if dx + xradius / 4 >= d or dy + yradius / 4 >= d:
            return True
        else:
            return False