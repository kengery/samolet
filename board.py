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
        Figyrs.print_text(self.display,self.x+self.dx/3,self.y+self.dy/2,25,(0,0,0),f"{self.airplane.name}")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 2, 25, (0, 0, 0),f"Fuel={int(self.airplane.benzin)}")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 4, 25, (0, 0, 0),f"RasxFuel={self.airplane.benzin_rashod}")
        Figyrs.print_text(self.display, self.x + self.dx / 1.5, self.y + self.dy / 2+self.dy / 3, 25, (0, 0, 0),f"Speed={self.airplane.speed}")


    def click(self,mouse_x,mouse_y)->bool:
        return self.image.click(mouse_x, mouse_y)
