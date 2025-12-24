import pygame
import random
import Image
import math
import Figyrs

class airplane:
    def __init__(self,game,x,y,dx,dy,display,file,name,speed,speed_min,speed_max,angle):
        self.x=x
        self.y=y
        self.dx=dx
        self.dy=dy

        self.angle_vis=0
        self.visota=800

        self.name=name
        self.angle=angle
        self.speed=speed
        self.speed_min=speed_min
        self.speed_max=speed_max
        self.benzin=5000
        self.benzin_rashod=0
        self.display=display
        self.camolet = Image.Image(self.x, self.y, self.dx, self.dy,self.display, file)
        self.camolet.set_angle(self.angle)
        self.points=[]
        self.count_points=0
        self.stolk = False
        self.finish = False
        self.scorOpt=3
        self.rashodbenz=0.01


    def render(self):
        self.camolet.render()
        Figyrs.print_text(self.display,self.x+self.dx/2,self.y,25,(0,0,0),f"{self.name}")

        if len(self.points) > 1:
            self.count_points = max(0, len(self.points) - 150)
            for i in range(self.count_points + 1, len(self.points)):
                n = self.points[i - 1]
                m = self.points[i]
                pygame.draw.line(self.display, (0, 0, 0), (n.x, n.y), (m.x, m.y))

    def add_angle(self,angle):
        self.angle=self.angle+angle
        self.camolet.set_angle(self.angle)

    def add_speed(self,speed):
        if self.speed_min < self.speed+speed < self.speed_max:
            self.speed=self.speed+speed

    def click(self,mouse_x,mouse_y)->bool:
        return self.camolet.click(mouse_x, mouse_y)

    def move(self):

        angle_rad = math.radians(self.angle)

        # Рассчитываем смещение по осям
        dx = self.speed * math.cos(angle_rad)
        dy = self.speed * math.sin(angle_rad)

        # Новые координаты
        self.x = self.x + dx
        self.y = self.y - dy
        self.camolet.set_x_y(self.x,self.y)
        n=point(self.x+self.dx/2,self.y+self.dy/2)
        self.points.append(n)
        #print(f"a={self.angle}")

        self.benzin_rashod = math.fabs(self.speed - self.scorOpt) + self.rashodbenz
        self.benzin=self.benzin-self.benzin_rashod



class point:
    def __init__(self,x, y):
        self.x=x
        self.y=y


"""
            n=speed
            self.sped.....+sped
            if n<self.speed and n!=self.speed:
                self.minysben=self.minysben-0.1
            else:
                self.minysben = self.minysben + 0.1
"""