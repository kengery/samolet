import pygame
from dataclasses import dataclass, field, asdict

@dataclass
# Запретный многоугольник: залетать нельзя.
class zona:
    points: list[tuple[float, float]]  # вершины многоугольника
    color: list[int,int,int]  # цвет заливки RGB
    # Запоминает экран, вершины и цвет зоны.
    def __init__(self,display,points,color):
        self.display=display  # окно pygame
        self.points=points  # список вершин [x, y]
        self.color=color  # цвет многоугольника

    # Рисует закрашенный многоугольник.
    def render(self):
        # Преобразуем точки в формат, понятный pygame (список кортежей (x, y))
        point_list = [(point[0], point[1]) for point in self.points]  # вершины для pygame
        # Рисуем закрашенный многоугольник
        pygame.draw.polygon(self.display, self.color, point_list)

    # True, если точка (x, y) внутри многоугольника (луч вправо).
    def select(self, x, y):
        inside = False  # чётность пересечений луча

        for i in range(len(self.points)):
            x1 = self.points[i][0]  # X первой вершины ребра
            y1 = self.points[i][1]  # Y первой вершины ребра
            x2 = self.points[(i + 1) % len(self.points)][0]  # X второй вершины ребра
            y2 = self.points[(i + 1) % len(self.points)][1]  # Y второй вершины ребра

            # Проверяем, пересекает ли горизонтальная линия ребро
            if (y1 <= y <= y2) or (y2 <= y <= y1):
                # Находим x координату пересечения
                x_intersect = x1 + (x2 - x1) * (y - y1) / (y2 - y1)  # X пересечения луча с ребром

                # Если пересечение справа от точки
                if x <= x_intersect:
                    inside = not inside  # ← ИНВЕРТИРУЕМ, а не устанавливаем в True

        return inside
