from xxsubtype import bench

import pygame
import Image
import math
import Figyrs
from dataclasses import dataclass, field, asdict
import time

PODEM_VISOT = 1  # метры за кадр (~30 мс), пока текущая высота не равна цели
TURB_PADENIE = 9  # метры в секунду, пока турбулентность сносит
SKOROST_KMCH = 200  # км/ч на 1 пиксель за кадр; speed 2 → 400 км/ч
VEKTOR_KADROV = 100  # длина линии курса, кадры (~3 с)
AVTOPILOT_GRAD = 0.5  # максимальный доворот к аэропорту, градусы за кадр
TURB_NACHALO = 1.5  # секунды сноса в сторону зоны
TURB_OBRATNO = TURB_NACHALO / 2  # секунды сноса в обратную сторону

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
    visota_airplane: float  # текущая высота в метрах
    visota_min: float  # нижний предел высоты в метрах
    visota_max: float  # верхний предел высоты в метрах

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

        self.visota_min=visota_min  # минимальная высота в метрах
        self.visota_max=visota_max  # максимальная высота в метрах
        self.visota_airplane=visota_airplane  # текущая высота в метрах
        if self.visota_airplane < self.visota_min:
            self.visota_airplane = self.visota_min
        if self.visota_airplane > self.visota_max:
            self.visota_airplane = self.visota_max
        self.zadana_visota=self.visota_airplane  # целевая высота в метрах
        self.visota_do=self.visota_airplane  # высота на прошлом кадре, для стрелки

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
        self.turb_aktiv=False  # идёт снос и выравнивание
        self.turb_vnutri=False  # сейчас внутри зоны
        self.turb_viravnen=False  # заход уже выровнен, ждём выход
        self.turb_t0=0  # момент захода, секунды
        self.turb_napravlenie=0  # градусы сноса зоны
        self.turb_skorost=0  # скорость сноса, всегда 1 пиксель за кадр; столько же секунд длится возврат
        self.turb_visota0=0  # высота в момент захода
        self.turb_visota_na_15=0  # высота после падения, с неё идёт возврат
        self.turb_zameren_15=False  # высота на 1.5 с уже снята
        self.scorOpt=2  # оптимальная скорость (минимальный расход)
        self.rashodbenz=0.01  # базовый расход топлива за кадр
        self.max=False  # подпись MAX на табличке (в коде не включается)
        self.min=False  # подпись MIN на табличке (в коде не включается)
        self.ball_benz=0  # уже сожжённое топливо для баллов
        self.__koef_ball=1  # множитель расхода: 1 обычный, 2 после выравнивания в зоне
        self.click_camolet=False  # выбран ли этот самолёт
        self.avtopilot = True  # сам доворачивает к аэропорту
        self.aeroport_x = None  # центр аэропорта X, None пока карта не задала
        self.aeroport_y = None  # центр аэропорта Y
        self.aeroport_rx = None  # половина ширины картинки аэропорта
        self.aeroport_ry = None  # половина высоты картинки аэропорта

        self.command_last_time=time.time()  # когда последний раз применили команду
        self.command=None  # текущая команда курса или скорости
        self.command_wait=0.5  # пауза между шагами команды, секунды
        self.command_speed=0.2  # шаг изменения скорости
        self.command_angle=15  # шаг поворота в градусах


    # Рисует спрайт, формуляр, линию курса и след из последних 150 точек.
    def render(self):
        self.camolet.render()
        self.__render_vektor()
        Figyrs.print_text(self.display,self.x+self.dx/2,self.y,23,(70, 220, 230),f"{self.name}")
        Figyrs.print_text(self.display,self.x+self.dx/2,self.y+38,18,(70, 220, 230),self.visota_text())
        Figyrs.print_text(self.display,self.x+self.dx/2,self.y+48,18,(70, 220, 230),f"{self.skorost_kmch()}")
        #pygame.draw.circle(self.display,(255,0,0),(self.x+self.dx/2,self.y+self.dy/2),self.dx/2,2)

        if len(self.points) > 1:
            self.count_points = max(0, len(self.points) - 150)
            for i in range(self.count_points + 1, len(self.points)):
                n = self.points[i - 1]  # предыдущая точка следа
                m = self.points[i]  # текущая точка следа
                pygame.draw.line(self.display, (0, 0, 0), (n.x, n.y), (m.x, m.y))

    # Курс после доворота к аэропорту не больше чем на AVTOPILOT_GRAD. Без аэропорта угол тот же.
    def __dovorot(self, cx, cy, angle):
        if self.aeroport_x is None:
            return angle
        cel = math.degrees(math.atan2(cy - self.aeroport_y, self.aeroport_x - cx))  # курс на центр аэропорта
        raznica = (cel - angle + 180) % 360 - 180  # кратчайший доворот, градусы
        if raznica > AVTOPILOT_GRAD:
            raznica = AVTOPILOT_GRAD
        elif raznica < -AVTOPILOT_GRAD:
            raznica = -AVTOPILOT_GRAD
        return angle + raznica

    # True, если точка внутри картинки аэропорта.
    def __v_kartinke(self, x, y):
        if self.aeroport_x is None or self.aeroport_rx is None:
            return False
        return abs(x - self.aeroport_x) <= self.aeroport_rx and abs(y - self.aeroport_y) <= self.aeroport_ry

    # Точка, где отрезок входит в картинку аэропорта.
    def __vhod_v_aeroport(self, x1, y1, x2, y2):
        left = self.aeroport_x - self.aeroport_rx  # левый край картинки
        right = self.aeroport_x + self.aeroport_rx  # правый край картинки
        top = self.aeroport_y - self.aeroport_ry  # верхний край картинки
        bottom = self.aeroport_y + self.aeroport_ry  # нижний край картинки
        dx = x2 - x1  # шаг по X
        dy = y2 - y1  # шаг по Y
        t_hit = 1  # доля шага до границы
        if dx != 0:
            for i in (left, right):
                t = (i - x1) / dx  # доля шага до вертикального края
                y = y1 + t * dy  # Y на этом крае
                if 0 <= t <= 1 and top <= y <= bottom and t < t_hit:
                    t_hit = t
        if dy != 0:
            for i in (top, bottom):
                t = (i - y1) / dy  # доля шага до горизонтального края
                x = x1 + t * dx  # X на этом крае
                if 0 <= t <= 1 and left <= x <= right and t < t_hit:
                    t_hit = t
        return (x1 + t_hit * dx, y1 + t_hit * dy)

    # Линия не длиннее VEKTOR_KADROV кадров. На краю картинки аэропорта обрывается. Снос не входит.
    def __render_vektor(self):
        if self.click_camolet == True:
            cvet = (0, 210, 220)  # выбранный самолёт
        else:
            cvet = (0, 120, 130)  # остальные тусклее
        cx = self.x + self.dx / 2  # центр самолёта по X
        cy = self.y + self.dy / 2  # центр самолёта по Y
        angle = self.angle  # курс на шаге линии
        avto = self.avtopilot == True and isinstance(self.command, command_airplane_angle) == False  # дуга к аэропорту
        tochki = [(cx, cy)]  # точки линии
        if self.__v_kartinke(cx, cy) == False:
            for _ in range(VEKTOR_KADROV):
                if avto == True:
                    angle = self.__dovorot(cx, cy, angle)
                rad = math.radians(angle)  # курс шага в радианах
                nx = cx + self.speed * math.cos(rad)  # следующий X
                ny = cy - self.speed * math.sin(rad)  # следующий Y
                if self.__v_kartinke(nx, ny) == True:
                    tochki.append(self.__vhod_v_aeroport(cx, cy, nx, ny))
                    break
                cx = nx
                cy = ny
                tochki.append((cx, cy))
        if len(tochki) > 1:
            pygame.draw.lines(self.display, cvet, False, tochki, 2)

    # Четыре цифры: высота в десятках метров.
    def desyatki_metrov(self, metry):
        desyatki = int(round(metry / 10))  # десятки метров
        return f"{desyatki:04d}"

    # Формуляр высоты: десятки метров, стрелка и заданная, если она другая.
    def visota_text(self):
        tek = self.desyatki_metrov(self.visota_airplane)  # текущая высота
        tekst = tek  # строка формуляра
        if self.visota_airplane > self.visota_do:
            tekst = tekst + "↑"
        elif self.visota_airplane < self.visota_do:
            tekst = tekst + "↓"
        zadana = self.desyatki_metrov(self.zadana_visota)  # заданная высота
        if zadana != tek:
            tekst = tekst + " " + zadana
        return tekst

    # Путевая скорость в км/ч.
    def skorost_kmch(self):
        return int(round(self.speed * SKOROST_KMCH))

    # Ставит целевую высоту в метрах и зажимает её в пределах самолёта.
    def set_zadana_visota(self, metry):
        if metry < self.visota_min:
            metry = self.visota_min
        if metry > self.visota_max:
            metry = self.visota_max
        self.zadana_visota = metry

    # Ставит команду поворота, если другой команды ещё нет, и снимает самолёт с маршрута.
    def add_angle(self,angle):
        if self.command is None:
            self.avtopilot = False
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

    # Запоминает центр и половину размера картинки аэропорта. Без центра курс не меняется.
    def set_aeroport(self, x, y, rx, ry):
        self.aeroport_x = x
        self.aeroport_y = y
        self.aeroport_rx = rx
        self.aeroport_ry = ry

    # Включает автопилот и снимает незаконченный поворот.
    def na_marshrut(self):
        self.avtopilot = True
        if isinstance(self.command, command_airplane_angle):
            self.command = None

    # Задаёт множитель расхода топлива (1 обычный, 2 после выравнивания в зоне).
    def ymn_koef_ball(self,koef_ball):
        self.__koef_ball=koef_ball

    # Начинает снос при новом заходе. Пока таймер идёт, повторный заход его не сбрасывает.
    def turb_zahod(self, zona):
        if zona is None:
            self.turb_vnutri = False
            self.Zapr_zon = False
            return
        self.Zapr_zon = True
        if self.turb_vnutri == True:
            return
        self.turb_vnutri = True
        if self.turb_aktiv == True:
            return
        self.turb_aktiv = True
        self.turb_viravnen = False
        self.turb_zameren_15 = False
        self.turb_t0 = time.time()
        self.turb_napravlenie = zona.napravlenie
        self.turb_skorost = 1
        self.turb_visota0 = self.visota_airplane

    # 2 после выравнивания, пока самолёт ещё в зоне, иначе 1.
    def turb_koef(self):
        if self.turb_vnutri == True and self.turb_viravnen == True and self.turb_aktiv == False:
            return 2
        return 1

    # Двигает самолёт за кадр: курс, скорость, высота, снос, топливо.
    def move(self):
        if self.benzin<=0:
            self.benzin=0
            self.poteryan=True
            return
        if self.finish==True or self.stolk==True or self.poteryan==True:
            return
        self.visota_do = self.visota_airplane
        sdvig = 0  # доля сноса: 1 в сторону зоны, -1 обратно, 0 нет
        if self.turb_aktiv == True:
            t = time.time() - self.turb_t0  # секунды с захода в зону
            t_obratno = TURB_NACHALO + TURB_OBRATNO  # конец обратного сноса
            konec = t_obratno + self.turb_skorost  # конец возврата, секунды
            if t >= TURB_NACHALO and self.turb_zameren_15 == False:
                spad = self.turb_visota0 - TURB_PADENIE * TURB_NACHALO  # высота к концу падения
                if spad < self.visota_min:
                    spad = self.visota_min
                self.turb_visota_na_15 = spad
                self.turb_zameren_15 = True
            if t >= konec:
                self.visota_airplane = self.zadana_visota
                self.turb_aktiv = False
                self.turb_viravnen = True
            elif t >= t_obratno:
                dolya = (t - t_obratno) / self.turb_skorost  # 0 в начале возврата, 1 в конце
                self.visota_airplane = self.turb_visota_na_15 + (self.zadana_visota - self.turb_visota_na_15) * dolya
                sdvig = -(1 - dolya)
            elif t >= TURB_NACHALO:
                self.visota_airplane = self.turb_visota_na_15
                sdvig = -1
            else:
                self.visota_airplane = self.turb_visota0 - TURB_PADENIE * t
                sdvig = 1
            if self.visota_airplane < self.visota_min:
                self.visota_airplane = self.visota_min
            if self.visota_airplane > self.visota_max:
                self.visota_airplane = self.visota_max
        else:
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

        if self.avtopilot == True and isinstance(self.command, command_airplane_angle) == False:
            cx = self.x + self.dx / 2  # центр самолёта по X
            cy = self.y + self.dy / 2  # центр самолёта по Y
            self.angle = self.__dovorot(cx, cy, self.angle)
            self.camolet.set_angle(self.angle)

        angle_rad = math.radians(self.angle)  # курс в радианах для cos/sin

        # Рассчитываем смещение по осям
        dx = self.speed * math.cos(angle_rad)  # сдвиг по X за кадр
        dy = self.speed * math.sin(angle_rad)  # сдвиг по Y (на экране вниз со знаком минус)
        if sdvig != 0:
            snos_rad = math.radians(self.turb_napravlenie)  # направление сноса в радианах
            dx = dx + self.turb_skorost * sdvig * math.cos(snos_rad)
            dy = dy + self.turb_skorost * sdvig * math.sin(snos_rad)

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
