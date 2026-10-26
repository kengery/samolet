import pygame
import random
import Image
import math
import Figyrs

# Табличка слева: имя, высота, расход, бензин, скорость самолёта.
class board:
    # Создаёт табличку для одного самолёта.
    def __init__(self,x,y,dx,dy,display,file,airplane):
        self.x=x  # левый край таблички
        self.y=y  # верхний край таблички
        self.dx=dx  # ширина таблички
        self.dy=dy  # высота таблички
        self.display=display  # окно pygame
        self.airplane=airplane  # самолёт, данные которого показывают
        self.image = Image.Image(self.x, self.y, self.dx, self.dy,self.display, file)  # фон таблички

    # Рисует табличку и строки с данными самолёта.
    def render(self):
        self.image.render()
        Figyrs.print_text(self.display,self.x+self.dx/4,self.y+self.dy/3,24,(0,0,0),f"{self.airplane.name}")
        Figyrs.print_text(self.display, self.x + self.dx / 4, self.y + self.dy * 0.72, 16, (0, 0, 0), f"Высота={int(round(self.airplane.visota_airplane))} м")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 4, 23, (0, 0, 0),f"Расход={int(self.airplane.benzin_rashod * 10) / 10}")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 2, 23, (0, 0, 0),f"Бензин={int((100*self.airplane.benzin)/self.airplane.izn_benzin)}%")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 2+self.dy / 4, 23, (0, 0, 0),f"Скорость={self.airplane.skorost_kmch()} км/ч")
        if self.airplane.max==True:
            Figyrs.print_text(self.display, self.x + self.dx+self.dx / 7, self.y + self.dy/2, 27, (0, 0, 0),"MAX")
        if self.airplane.min==True:
            Figyrs.print_text(self.display, self.x + self.dx+self.dx / 7, self.y + self.dy/2, 27, (0, 0, 0),"MIN")


    # Проверяет, попал ли клик в табличку.
    def click(self,mouse_x,mouse_y)->bool:
        return self.image.click(mouse_x, mouse_y)
