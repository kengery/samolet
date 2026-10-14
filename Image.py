import pygame

# Картинка на экране: загрузка, поворот, клик по прямоугольнику.
class Image:
    # Грузит файл, масштабирует до dx×dy и запоминает угол.
    def __init__(self,x,y,dx,dy,display,file, angle=0):
        self.x=x  # левый край
        self.y=y  # верхний край
        self.__dx=dx  # ширина картинки
        self.__dy=dy  # высота картинки
        self.__display=display  # окно pygame
        self.angle=angle  # угол поворота в градусах
        image_file=pygame.image.load(file)  # исходный файл картинки
        self.__image = pygame.transform.scale(image_file, (self.__dx, self.__dy))  # картинка нужного размера

    # Рисует картинку; если угол не 0 — крутит вокруг центра.
    def render(self):

        if (self.angle!=0):
            rotated_image = pygame.transform.rotate(self.__image, self.angle)  # повёрнутая копия
            rect = rotated_image.get_rect(center=(self.x + self.__dx / 2, self.y + self.__dy / 2))  # куда поставить центр
            self.__display.blit(rotated_image, rect)
        else:
            self.__display.blit(self.__image,(self.x,self.y))

    # Задаёт угол поворота спрайта.
    def set_angle(self, angle):
        self.angle=angle

    # True, если точка (mouse_x, mouse_y) внутри прямоугольника.
    def click(self,mouse_x,mouse_y)->bool:
        if self.x <mouse_x < self.x+self.__dx and self.y < mouse_y < self.y + self.__dy:
            return  True
        else:
            return False
    # Переносит левый верхний угол в новые координаты.
    def set_x_y(self,x,y):
        self.x=x
        self.y=y
