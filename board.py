import pygame
import random
import Image
import math
import Figyrs

class board:
    def __init__(self,x,y,dx,dy,display,file,airplane):
        self.x=x
        self.y=y
        self.dx=dx
        self.dy=dy
        self.display=display
        self.airplane=airplane
        self.image = Image.Image(self.x, self.y, self.dx, self.dy,self.display, file)

    def render(self):
        self.image.render()
        Figyrs.print_text(self.display,self.x+self.dx/4,self.y+self.dy/2,28,(0,0,0),f"{self.airplane.name}")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 4, 23, (0, 0, 0),f"Расход={int(self.airplane.benzin_rashod * 10) / 10}")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 2, 23, (0, 0, 0),f"Бензин={int(self.airplane.benzin)}")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 2+self.dy / 3, 23, (0, 0, 0),f"Скорость={int(self.airplane.speed*10)/10}")
        if self.airplane.max==True:
            Figyrs.print_text(self.display, self.x + self.dx+self.dx / 7, self.y + self.dy/2, 27, (0, 0, 0),"MAX")
        if self.airplane.min==True:
            Figyrs.print_text(self.display, self.x + self.dx+self.dx / 7, self.y + self.dy/2, 27, (0, 0, 0),"MIN")


    def click(self,mouse_x,mouse_y)->bool:
        return self.image.click(mouse_x, mouse_y)
