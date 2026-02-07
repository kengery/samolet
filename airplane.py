from xxsubtype import bench

import pygame
import random
import Image
import math
import Figyrs
from dataclasses import dataclass, field, asdict
import time

@dataclass
class airplane:
    x : float
    y : float
    dx : int
    dy : int
    name : str
    file : str
    speed :float
    speed_min :float
    speed_max :float
    angle: float
    benzin: float

    def __init__(self,x,y,dx,dy,display,file,name,speed,speed_min,speed_max,angle, benzin):
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

        self.benzin=benzin
        self.izn_benzin=self.benzin
        self.benzin_rashod=0
        self.display=display
        self.camolet = Image.Image(self.x, self.y, self.dx, self.dy,self.display, file,self.angle)
        self.camolet.set_angle(self.angle)
        self.points=[]
        self.file=file
        self.count_points=0
        self.stolk = False
        self.finish = False
        self.poteryan=False
        self.Zapr_zon=False
        self.scorOpt=3
        self.rashodbenz=0.01
        self.max=False
        self.min=False
        self.ball_benz=0
        self.__koef_ball=1
        self.click_camolet=False

        self.command_last_time=time.time()
        self.command=None
        self.command_wait=0.5
        self.command_speed=0.2
        self.command_angle=10


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
        if self.command is None:
            self.command_last_time=time.time()
            if angle>0:
                self.command=command_airplane_angle(angle, True)
            else:
                self.command = command_airplane_angle(angle, False)


    def add_speed(self,speed):
        if self.command is None:
            self.command_last_time = time.time()
            if speed > 0:
                self.command = command_airplane_speed(speed, True)
            else:
                self.command = command_airplane_speed(-speed, False)

    def click(self,mouse_x,mouse_y)->bool:
        return self.camolet.click(mouse_x, mouse_y)

    def ymn_koef_ball(self,koef_ball):
        self.__koef_ball=koef_ball

    def move(self):
        if self.benzin<=0:
            self.benzin=0
            self.poteryan=True
            return
        if self.finish==True or self.stolk==True or self.poteryan==True:
            return
        if time.time()-self.command_last_time>self.command_wait and self.command is not None:
            if isinstance(self.command, command_airplane_angle):
                angle_Min=self.command_angle
                if self.command.left==True:
                    self.command.angle = self.command.angle - angle_Min
                    angle_Min=angle_Min*-1
                    if self.command.angle <= 0:
                        self.command = None
                else:
                    self.command.angle = self.command.angle + angle_Min
                    if self.command.angle >= 0:
                        self.command = None
                self.angle=self.angle-angle_Min
                self.command_last_time=time.time()
                self.camolet.set_angle(self.angle)

            if isinstance(self.command, command_airplane_speed):
                speed_Min = self.command_speed
                if self.command.increase_speed == True:
                    if self.command.speed - speed_Min <= 0:
                        self.command = None
                        return
                    else:
                        self.command.speed = self.command.speed - speed_Min
                    self.speed = self.speed + speed_Min
                    if self.speed >=self.speed_max:
                        self.speed=self.speed_max
                        self.command=None
                else:
                    if self.command.speed - speed_Min <= 0:
                        self.command = None
                        return
                    else:
                        self.command.speed = self.command.speed - speed_Min

                    self.speed = self.speed - speed_Min
                    if self.speed <= self.speed_min:
                        self.speed = self.speed_min
                        self.command = None
                self.command_last_time = time.time()


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

        self.benzin_rashod = (math.fabs(self.speed - self.scorOpt) + self.rashodbenz)*self.__koef_ball
        self.benzin=self.benzin-self.benzin_rashod
        self.ball_benz=self.ball_benz+self.benzin_rashod


class point:
    def __init__(self,x, y):
        self.x=x
        self.y=y

class command_airplane_angle:
    def __init__(self,angle, left):
        self.angle=angle
        self.left=left

class command_airplane_speed:
    def __init__(self,speed, increase_speed):
        self.speed=speed
        self.increase_speed=increase_speed