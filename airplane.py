from xxsubtype import bench

import pygame
import random
import Image
import math
import Figyrs
from dataclasses import dataclass, field, asdict
import time

PODEM_VISOT = 5  # футы за кадр (~30 мс), пока текущая высота не равна цели

@dataclass
# Самолёт: полёт, топливо, команды курса и скорости.
class airplane:
    x : float  # левый край спрайта
    y : float  # верхний край спрайта
    dx : int  # ширина спрайта
    dy : int  # высота спрайта
    name : str  # имя рейса, например Рейс1
    file : str  # путь к картинке спрайта
    speed :float  # текущая скорость, пиксели за кадр
    speed_min :float  # нижний предел скорости
    speed_max :float  # верхний предел скорости
    angle: float  # курс в градусах: 0 — вправо
    benzin: float  # остаток топлива
    visota_airplane: float  # текущая высота в футах
    visota_min: float  # нижний предел высоты
    visota_max: float  # верхний предел высоты

    # Создаёт самолёт и задаёт стартовые поля полёта.
    def __init__(self,x,y,dx,dy,display,file,name,speed,speed_min,speed_max,angle, benzin, visota_airplane, visota_min, visota_max):
        self.x=x  # левый край спрайта
        self.y=y  # верхний край спрайта
        self.dx=dx  # ширина спрайта
        self.dy=dy  # высота спрайта

        self.name=name  # имя рейса
        self.angle=angle  # курс в градусах
        self.speed=speed  # скорость, пиксели за кадр

        self.speed_min=speed_min  # минимальная скорость
        self.speed_max=speed_max  # максимальная скорость

        self.visota_min=visota_min  # минимальная высота в футах
        self.visota_max=visota_max  # максимальная высота в футах
        self.visota_airplane=visota_airplane  # текущая высота в футах
        if self.visota_airplane < self.visota_min:
            self.visota_airplane = self.visota_min
        if self.visota_airplane > self.visota_max:
            self.visota_airplane = self.visota_max
        self.zadana_visota=self.visota_airplane  # целевая высота в футах

        self.benzin=benzin  # остаток топлива
        self.izn_benzin=self.benzin  # стартовый бак (штраф в баллах)
        self.benzin_rashod=0  # расход топлива за текущий кадр
        self.display=display  # окно pygame
        self.camolet = Image.Image(self.x, self.y, self.dx, self.dy,self.display, file,self.angle)  # спрайт самолёта
        self.camolet.set_angle(self.angle)
        self.points=[]  # точки следа
        self.file=file  # путь к картинке
        self.count_points=0  # с какой точки рисовать след
        self.stolk = False  # столкнулся с другим самолётом
        self.finish = False  # сел в аэропорт
        self.poteryan=False  # потерян (экран, зона, пустой бак)
        self.Zapr_zon=False  # True, если самолёт в турбулентности
        self.scorOpt=2  # оптимальная скорость (минимальный расход)
        self.rashodbenz=0.01  # базовый расход топлива за кадр
        self.max=False  # подпись MAX на табличке (в коде не включается)
        self.min=False  # подпись MIN на табличке (в коде не включается)
        self.ball_benz=0  # уже сожжённое топливо для баллов
        self.__koef_ball=1  # множитель расхода: 1 обычный, 5 в турбулентности
        self.click_camolet=False  # выбран ли этот самолёт

        self.command_last_time=time.time()  # когда последний раз применили команду
        self.command=None  # текущая команда курса или скорости
        self.command_wait=0.5  # пауза между шагами команды, секунды
        self.command_speed=0.2  # шаг изменения скорости
        self.command_angle=15  # шаг поворота в градусах


    # Рисует спрайт, имя, высоту и след из последних 150 точек.
    def render(self):
        self.camolet.render()
        Figyrs.print_text(self.display,self.x+self.dx/2,self.y,25,(0,0,0),f"{self.name}")
        Figyrs.print_text(self.display,self.x+self.dx/2,self.y+22,20,(0,0,0),self.visota_text())
        #pygame.draw.circle(self.display,(255,0,0),(self.x+self.dx/2,self.y+self.dy/2),self.dx/2,2)

        if len(self.points) > 1:
            self.count_points = max(0, len(self.points) - 150)
            for i in range(self.count_points + 1, len(self.points)):
                n = self.points[i - 1]  # предыдущая точка следа
                m = self.points[i]  # текущая точка следа
                pygame.draw.line(self.display, (0, 0, 0), (n.x, n.y), (m.x, m.y))

    # Текст высоты: текущие футы и стрелка к цели, если ещё не дошли.
    def visota_text(self):
        current = int(self.visota_airplane)  # текущая высота
        target = int(self.zadana_visota)  # целевая высота
        if self.visota_airplane != self.zadana_visota:
            return f"{current} → {target} фт"
        return f"{current} фт"

    # Ставит целевую высоту и зажимает её в пределах самолёта.
    def set_zadana_visota(self, feet):
        if feet < self.visota_min:
            feet = self.visota_min
        if feet > self.visota_max:
            feet = self.visota_max
        self.zadana_visota = feet

    # Ставит команду поворота, если другой команды ещё нет.
    def add_angle(self,angle):
        if self.command is None:
            self.command_last_time=time.time()
            if angle>0:
                self.command=command_airplane_angle(angle, True)  # поворот влево
            else:
                self.command = command_airplane_angle(angle, False)  # поворот вправо


    # Ставит команду изменения скорости, если другой команды ещё нет.
    def add_speed(self,speed):
        if self.command is None:
            self.command_last_time = time.time()
            if speed > 0:
                self.command = command_airplane_speed(speed, True)  # ускорить
            else:
                self.command = command_airplane_speed(-speed, False)  # замедлить

    # Проверяет, попал ли клик в спрайт самолёта.
    def click(self,mouse_x,mouse_y)->bool:
        return self.camolet.click(mouse_x, mouse_y)

    # Задаёт множитель расхода топлива (1 обычный, 5 в турбулентности).
    def ymn_koef_ball(self,koef_ball):
        self.__koef_ball=koef_ball

    # Двигает самолёт за кадр: курс, скорость, высота, топливо.
    def move(self):
        if self.benzin<=0:
            self.benzin=0
            self.poteryan=True
            return
        if self.finish==True or self.stolk==True or self.poteryan==True:
            return
        if self.visota_airplane < self.zadana_visota:
            self.visota_airplane = min(self.visota_airplane + PODEM_VISOT, self.zadana_visota)
        elif self.visota_airplane > self.zadana_visota:
            self.visota_airplane = max(self.visota_airplane - PODEM_VISOT, self.zadana_visota)
        if self.visota_airplane < self.visota_min:
            self.visota_airplane = self.visota_min
        if self.visota_airplane > self.visota_max:
            self.visota_airplane = self.visota_max
        if time.time()-self.command_last_time>self.command_wait and self.command is not None:
            if isinstance(self.command, command_airplane_angle):
                angle_Min=self.command_angle  # шаг поворота за одно применение
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
                speed_Min = self.command_speed  # шаг скорости за одно применение
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


        angle_rad = math.radians(self.angle)  # курс в радианах для cos/sin

        # Рассчитываем смещение по осям
        dx = self.speed * math.cos(angle_rad)  # сдвиг по X за кадр
        dy = self.speed * math.sin(angle_rad)  # сдвиг по Y (на экране вниз со знаком минус)

        # Новые координаты
        self.x = self.x + dx
        self.y = self.y - dy
        self.camolet.set_x_y(self.x,self.y)
        n=point(self.x+self.dx/2,self.y+self.dy/2)  # центр самолёта для следа
        self.points.append(n)
        #print(f"a={self.angle}")

        self.benzin_rashod = (math.fabs(self.speed - self.scorOpt) + self.rashodbenz)*self.__koef_ball
        self.benzin=self.benzin-self.benzin_rashod
        self.ball_benz=self.ball_benz+self.benzin_rashod


# Точка следа самолёта (x, y).
class point:
    # Запоминает координаты точки.
    def __init__(self,x, y):
        self.x=x  # координата X
        self.y=y  # координата Y

# Команда поворота самолёта.
class command_airplane_angle:
    # Сколько ещё крутить и в какую сторону.
    def __init__(self,angle, left):
        self.angle=angle  # оставшийся угол команды
        self.left=left  # True — влево (+15), False — вправо

# Команда изменения скорости самолёта.
class command_airplane_speed:
    # На сколько менять скорость и ускорять ли.
    def __init__(self,speed, increase_speed):
        self.speed=speed  # сколько ещё шагов скорости
        self.increase_speed=increase_speed  # True — быстрее, False — медленнее
