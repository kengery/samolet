import pygame
from dataclasses import dataclass, field, asdict

@dataclass
class zona:
    points: list[tuple[float, float]]
    color: list[int,int,int]
    def __init__(self,display,points,color):
        self.display=display
        self.points=points
        self.color=color

    def render(self):
        # Преобразуем точки в формат, понятный pygame (список кортежей (x, y))
        point_list = [(point[0], point[1]) for point in self.points]
        # Рисуем закрашенный многоугольник
        pygame.draw.polygon(self.display, self.color, point_list)

    def select(self, x, y):
        inside = False

        for i in range(len(self.points)):
            x1 = self.points[i][0]
            y1 = self.points[i][1]
            x2 = self.points[(i + 1) % len(self.points)][0]
            y2 = self.points[(i + 1) % len(self.points)][1]

            # Проверяем, пересекает ли горизонтальная линия ребро
            if ((y1 > y) != (y2 > y)):
                # Находим x координату пересечения
                x_intersect = x1 + (x2 - x1) * (y - y1) / (y2 - y1)

                # Если пересечение справа от точки
                if x <= x_intersect:
                    inside = not inside  # ← ИНВЕРТИРУЕМ, а не устанавливаем в True

        return inside