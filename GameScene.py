import random
import MenuLevel
import Pogoda
import Tyrbylentnost
import airplane
import Class
import pygame
import Figyrs
from Image import Image
import board
import math
import new_game_file
import queue
import Zona
import point
import time
import MyMicrophone
command_queue = queue.Queue()  # очередь для передачи голосовых команд
VISOTA_SBLIGENIA_AIRPLANE = 305  # метры: столкновение, если разница высот меньше этого

# Сцена симуляции: самолёты, зоны, кнопки, счёт и голос.
class GameScene(Class.Scene):
    # Создаёт кнопки, поле и поля раунда. Самолёты появятся при загрузке карты.
    def __init__(self, gameEngine, display):
        super().__init__(gameEngine)
        self.display = display  # окно pygame
        self.button_exit = Image(gameEngine.screenx * 0.902, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09, self.display,'image\\bsxod.PNG')  # выход в меню
        self.button_pravo = Image(gameEngine.screenx * 0.6, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09,self.display, 'image\\pravo.png')  # поворот вправо
        self.button_levo = Image(gameEngine.screenx * 0.5, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.1,self.display, 'image\\levo.png')  # поворот влево
        self.button_increase = Image(gameEngine.screenx * 0.4, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.093,self.display, 'image\\increase.png')  # быстрее
        self.button_reduce = Image(gameEngine.screenx * 0.3, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09,self.display, 'image\\reduse.png')  # медленнее
        self.button_visota = Image(gameEngine.screenx * 0.72, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09, self.display, 'image\\button1.png')  # ввод высоты
        self.button_marshrut = Image(gameEngine.screenx * 0.82, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\button1.png')  # возврат на маршрут к своей цели
        self.visota_input = False  # открыта ли плашка ввода высоты
        self.visota_text = ""  # набранные метры
        self.pole_x = 260  # левый край поля, справа от табличек
        self.pole_y = 100  # верхний край поля
        self.pole_x2 = 1820  # правый край поля
        self.pole_y2 = 965  # нижний край поля
        self.fon_cvet = (6, 16, 28)  # цвет фона за полем
        self.pole_cvet = (10, 28, 46)  # заливка поля
        self.ramka_cvet = (0, 210, 220)  # цвет рамки поля
        self.Aroport=0  # картинка аэропорта, ставится при загрузке карты
        self.gameEngine=gameEngine  # движок сцен
        self.display=display  # окно pygame
        self.click_airplane = None  # выбранный самолёт
        self.circle_x=0  # центр аэропорта X
        self.circle_y=0  # центр аэропорта Y
        self.circle_radiusx = 0  # половина ширины аэропорта
        self.circle_radiusy = 0  # половина высоты аэропорта
        self.end_game=False  # все самолёты уже имеют исход
        self.airplanes_stolk=0  # сколько столкнулись
        self.airplanes_finish=0  # сколько сели в аэропорт
        self.airplanes_granica=0  # сколько ушли через свой проём
        self.airplanes_poteryan=0  # сколько потеряны
        self.v_hody = []  # проёмы на рамке этой карты
        self.ball = 0  # сумма расхода и штрафов
        #self.points=[point.point(200, 300), point.point(700, 200), point.point(700, 800), point.point(500, 400)]
        self.n_zona=[]  # запретные многоугольники карты
        self.my_microphone = MyMicrophone.MyMicrophone()  # запись голоса по пробелу

    # Клики, клавиши, голос и кнопки курса/скорости/высоты.
    def handle_events(self, events):
        self.__process_voice_commands()
        for event in events:
            if self.visota_input and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.visota_input = False
                    self.visota_text = ""
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.__apply_visota_input()
                elif event.key == pygame.K_BACKSPACE:
                    self.visota_text = self.visota_text[:-1]
                elif event.unicode.isdigit() and len(self.visota_text) < 7:
                    self.visota_text += event.unicode
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if getattr(event, "repeat", 0) == 0:
                    self.my_microphone.space_pressed()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.my_microphone.space_released()

            mouse_x, mouse_y = pygame.mouse.get_pos()  # координаты курсора

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_exit.click(mouse_x, mouse_y):
                    self.gameEngine.change_scene("menu")
                for i in range(0, len(self.airplanes)):
                #    if self.airplanes[i].click(mouse_x, mouse_y):
                        self.__select_airplane(mouse_x, mouse_y)

                if self.click_airplane is not None:
                    if self.button_pravo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(-15)
                    if self.button_levo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(15)
                    if self.button_increase.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(1)
                    if self.button_reduce.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(-1)
                    if self.button_visota.click(mouse_x, mouse_y):
                        self.visota_input = True
                        self.visota_text = ""
                    if self.button_marshrut.click(mouse_x, mouse_y):
                        self.click_airplane.na_marshrut()


    # Движение, столкновения, посадка, проём на рамке, поле, запретные зоны и конец раунда.
    def update(self):

        self.__update_tyrbylentnost()
        self.__update_move_airplanes()
        self.__calc_balls()

        game_end = 0  # сколько своих самолётов уже с исходом
        svoih = 0  # сколько своих самолётов на карте
        self.airplanes_stolk = 0
        self.airplanes_finish = 0
        self.airplanes_granica = 0
        self.airplanes_poteryan = 0
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].nash == False:
                if self.airplanes[i].ushel == False:
                    if self.airplanes[i].x < self.pole_x or self.airplanes[i].x + self.airplanes[i].dx > self.pole_x2 or \
                            self.airplanes[i].y < self.pole_y or self.airplanes[i].y + self.airplanes[i].dy > self.pole_y2:
                        self.airplanes[i].ushel = True
                continue
            svoih = svoih + 1
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                for j in range(i + 1, len(self.airplanes)):
                    if self.airplanes[j].nash == False:
                        continue
                    if self.airplanes[j].stolk == False and self.airplanes[j].finish == False:
                        x_2 = self.airplanes[i].x + self.airplanes[i].dx / 2  # центр первого по X
                        x_1 = self.airplanes[j].x + self.airplanes[j].dx / 2  # центр второго по X
                        y_2 = self.airplanes[i].y + self.airplanes[i].dy / 2  # центр первого по Y
                        y_1 = self.airplanes[j].y + self.airplanes[j].dy / 2  # центр второго по Y

                        # находим растояние между центром самолётов
                        d = math.sqrt((x_2 - x_1) * (x_2 - x_1) + (y_2 - y_1) * (y_2 - y_1))  # расстояние между центрами
                        stolk_airplane = self.airplanes[i].dx / 2 + self.airplanes[j].dx / 2 >= d or self.airplanes[i].dy / 2 + \
                                self.airplanes[j].dy / 2 >= d  # близко на карте
                        min_na_stolk_visota = math.fabs(self.airplanes[i].visota_airplane - self.airplanes[j].visota_airplane) < VISOTA_SBLIGENIA_AIRPLANE  # разница высот меньше 305 м
                        if stolk_airplane and min_na_stolk_visota:
                            self.airplanes[i].stolk = True
                            self.airplanes[j].stolk = True

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False and self.airplanes[i].na_v_hod == False:
                x1 = self.airplanes[i].x + self.airplanes[i].dx / 2  # центр самолёта X
                y1 = self.airplanes[i].y + self.airplanes[i].dy / 2  # центр самолёта Y
                x2 = self.circle_x  # центр аэропорта X
                y2 = self.circle_y  # центр аэропорта Y
                # находим растояние между центром самолёта и финиша
                d = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))  # расстояние до аэропорта
                if self.airplanes[i].dx + self.circle_radiusx / 2 >= d or self.airplanes[
                    i].dy + self.circle_radiusy / 2 >= d:
                    self.airplanes[i].finish = True

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                ishod = self.__ishod_ramki(self.airplanes[i])  # успех в проёме, ещё летит или потеря
                if ishod == "uspeh":
                    self.airplanes[i].finish = True
                    self.airplanes[i].cherez_granicu = True
                elif ishod == "poteryan":
                    self.airplanes[i].poteryan = True
            """
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                for j in range(0, len(self.Pogoda)):
                    if self.Pogoda[j].select(self.airplanes[i].x, self.airplanes[i].y, self.airplanes[i].dx,self.airplanes[i].dy) == True:
                        self.airplanes[i].stolk=True
            """

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                for j in range(0, len(self.n_zona)):
                    if self.n_zona[j].select(self.airplanes[i].x+self.airplanes[i].dx/2,self.airplanes[i].y+self.airplanes[i].dy/2)==True:
                        self.airplanes[i].poteryan = True

            if self.airplanes[i].stolk == True:
                self.airplanes_stolk = self.airplanes_stolk + 1
            if self.airplanes[i].finish == True and self.airplanes[i].cherez_granicu == False:
                self.airplanes_finish = self.airplanes_finish + 1
            if self.airplanes[i].cherez_granicu == True:
                self.airplanes_granica = self.airplanes_granica + 1
            if self.airplanes[i].poteryan == True:
                self.airplanes_poteryan = self.airplanes_poteryan + 1

            if self.airplanes[i].stolk == True or self.airplanes[i].finish == True or self.airplanes[
                i].poteryan == True:
                game_end = game_end + 1

        if svoih > 0 and game_end == svoih:
            self.end_game = True

    # Рисует тёмный фон окна и прямоугольник поля с рамкой.
    def __render_pole(self):
        self.display.fill(self.fon_cvet)
        pole = (self.pole_x, self.pole_y, self.pole_x2 - self.pole_x, self.pole_y2 - self.pole_y)  # прямоугольник поля
        pygame.draw.rect(self.display, self.pole_cvet, pole)  # заливка поля
        pygame.draw.rect(self.display, self.ramka_cvet, pole, 2)  # рамка поля толщиной 2
        self.__render_proemy()

    # Рисует разрыв рамки на каждом проёме и засечки по концам.
    def __render_proemy(self):
        for v_hod in self.v_hody:
            self.__render_proem(v_hod)

    # Закрашивает отрезок рамки цветом поля и ставит короткие засечки.
    def __render_proem(self, v_hod):
        a = v_hod.a  # начало проёма вдоль рамки
        b = v_hod.b  # конец проёма вдоль рамки
        if v_hod.storona == "verh" or v_hod.storona == "niz":
            y = self.pole_y if v_hod.storona == "verh" else self.pole_y2  # сторона рамки
            pygame.draw.line(self.display, self.pole_cvet, (a, y), (b, y), 4)  # разрыв бирюзовой линии
            pygame.draw.line(self.display, self.ramka_cvet, (a, y - 8), (a, y + 8), 2)  # засечка в начале
            pygame.draw.line(self.display, self.ramka_cvet, (b, y - 8), (b, y + 8), 2)  # засечка в конце
        else:
            x = self.pole_x if v_hod.storona == "levo" else self.pole_x2  # сторона рамки
            pygame.draw.line(self.display, self.pole_cvet, (x, a), (x, b), 4)  # разрыв бирюзовой линии
            pygame.draw.line(self.display, self.ramka_cvet, (x - 8, a), (x + 8, a), 2)  # засечка в начале
            pygame.draw.line(self.display, self.ramka_cvet, (x - 8, b), (x + 8, b), 2)  # засечка в конце

    # True, если край спрайта вышел за прямоугольник поля.
    def __za_polem(self, plane):
        return plane.x < self.pole_x or plane.x + plane.dx > self.pole_x2 or plane.y < self.pole_y or plane.y + plane.dy > self.pole_y2

    # True, если центр самолёта уже за этой стороной рамки.
    def __centr_za(self, plane, storona):
        cx = plane.x + plane.dx / 2  # центр по X
        cy = plane.y + plane.dy / 2  # центр по Y
        if storona == "verh":
            return cy <= self.pole_y
        if storona == "niz":
            return cy >= self.pole_y2
        if storona == "levo":
            return cx <= self.pole_x
        if storona == "pravo":
            return cx >= self.pole_x2
        return False

    # True, если координата центра вдоль рамки лежит в отрезке своего проёма.
    def __vdol_proema(self, plane):
        cx = plane.x + plane.dx / 2  # центр по X
        cy = plane.y + plane.dy / 2  # центр по Y
        if plane.granica_storona == "verh" or plane.granica_storona == "niz":
            return plane.granica_a <= cx <= plane.granica_b
        return plane.granica_a <= cy <= plane.granica_b

    # None, пока спрайт в поле. Иначе uspeh, letit или poteryan.
    def __ishod_ramki(self, plane):
        if self.__za_polem(plane) == False:
            return None
        if plane.na_v_hod == False:
            return "poteryan"
        vdol = self.__vdol_proema(plane)  # центр вдоль рамки в своём отрезке
        svoya = self.__centr_za(plane, plane.granica_storona)  # центр пересёк сторону проёма
        drugaya = False  # центр пересёк другую сторону
        for storona in ("verh", "niz", "levo", "pravo"):
            if storona != plane.granica_storona and self.__centr_za(plane, storona) == True:
                drugaya = True
        if svoya == True and vdol == True and drugaya == False:
            return "uspeh"
        v_proem = False  # край спрайта вышел в сторону своего проёма
        if plane.granica_storona == "levo" and plane.x < self.pole_x:
            v_proem = True
        elif plane.granica_storona == "pravo" and plane.x + plane.dx > self.pole_x2:
            v_proem = True
        elif plane.granica_storona == "verh" and plane.y < self.pole_y:
            v_proem = True
        elif plane.granica_storona == "niz" and plane.y + plane.dy > self.pole_y2:
            v_proem = True
        if vdol == True and drugaya == False and svoya == False and v_proem == True:
            return "letit"
        return "poteryan"

    # Рисует поле, зоны, кнопки, аэропорт, самолёты и итог раунда.
    def render(self):
        self.__render_pole()
        self.__render_tyrbylentnost()
        self.Aroport.render()
        self.__render_airplanes()
        self.display.set_clip(None)

        self.__render_button_airplanes()

        self.button_exit.render()
        self.button_pravo.render()
        self.button_levo.render()
        self.button_increase.render()
        self.button_reduce.render()
        self.button_visota.render()
        self.button_marshrut.render()
        Figyrs.print_text(self.display, self.button_visota.x + self.gameEngine.screenx * 0.05, self.button_visota.y + self.gameEngine.screeny * 0.045, 22, (0, 0, 0), "Высота")
        Figyrs.print_text(self.display, self.button_marshrut.x + self.gameEngine.screenx * 0.04, self.button_marshrut.y + self.gameEngine.screeny * 0.045, 22, (0, 0, 0), "Маршрут")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.45, self.gameEngine.screeny * 0.12, 20, (0, 0, 0), f"Столкновение, если разница высот < {VISOTA_SBLIGENIA_AIRPLANE} м")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.45, self.gameEngine.screeny * 0.15, 20, (0, 0, 0), f"Ветер, если разница высот < {Tyrbylentnost.VISOTA_SLOIA} м")
        self.__render_visota_input()

        if self.end_game == True:
            self.__render_end_game()
            self.end_game=False

    # Рисует турбулентность и запретные зоны.
    def __render_tyrbylentnost(self):
        for i in range(0, len(self.Tyrbylentnost)):
            self.Tyrbylentnost[i].render()
        for i in range(0, len(self.n_zona)):
            self.n_zona[i].render()
        #for i in range(0, len(self.Pogoda)):
        #    self.Pogoda[i].render()

    # Рисует летящие самолёты: свой ромбом, чужой тусклым квадратом.
    def __render_airplanes(self):
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].ushel == True:
                continue
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                self.airplanes[i].render()

    # Показывает итоговое окно: баллы, столкнулись, потеряны, сели и ушли через границу.
    def __render_end_game(self):
        Figyrs.kvadr_poly(self.gameEngine.screenx*0.25,self.gameEngine.screeny*0.25,self.gameEngine.screenx*0.5,self.gameEngine.screeny*0.4,200,self.display)
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.505, self.gameEngine.screeny * 0.35,80, (0, 0, 0),f"Баллы = {int(self.ball)}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.4,self.gameEngine.screeny * 0.45,40,(0,0,0),f"Столкнулись = {self.airplanes_stolk}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, self.gameEngine.screeny * 0.5, 40, (0, 0, 0),f"Потерянны = {self.airplanes_poteryan}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.62, self.gameEngine.screeny * 0.45,40, (0, 0, 0),f"Прилетели в аэропорт = {self.airplanes_finish}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, self.gameEngine.screeny * 0.56, 40, (0, 0, 0), f"Ушли через границу = {self.airplanes_granica}")


    # Рисует таблички слева: обычная, красная или зелёная.
    def __render_button_airplanes(self):
        if self.button_airplane is None:
            return
        for i in range(0, len(self.button_airplane)):
            if self.airplanes[i].nash == False:
                continue
            if self.airplanes[i].stolk != True:
                self.button_airplane[i].render_poloska()
            else:
                self.button_stolk[i].render_poloska()
            if self.airplanes[i].poteryan == True:
                self.button_stolk[i].render_poloska()
            if self.airplanes[i].benzin <= 0:
                self.button_stolk[i].render_poloska()
            if self.airplanes[i].finish == True:
                self.button_finish[i].render_poloska()

    # Сдвигает зоны ветра по их курсу и по высоте слоя.
    def __update_tyrbylentnost(self):
        for i in range(0, len(self.Tyrbylentnost)):
            self.Tyrbylentnost[i].move()

    # Двигает самолёты: доклад зоны при входе, снос и множитель топлива.
    def __update_move_airplanes(self):
        for i in range(0,len(self.airplanes)):
            if self.airplanes[i].nash == False:
                self.airplanes[i].move()
                continue
            zona = None  # зона, в которой самолёт в этом кадре
            for j in range(0, len(self.Tyrbylentnost)):
                popal = self.Tyrbylentnost[j].select(self.airplanes[i].x,self.airplanes[i].y,self.airplanes[i].dx,self.airplanes[i].dy,self.airplanes[i].visota_airplane)  # самолёт в турбулентной зоне
                if popal == True:
                    if self.airplanes[i].turb_vnutri == False:
                        self.Tyrbylentnost[j].doklad()
                    zona = self.Tyrbylentnost[j]
                    break
            self.airplanes[i].turb_zahod(zona)
            self.airplanes[i].ymn_koef_ball(self.airplanes[i].turb_koef())
            self.airplanes[i].move()

    # Считает баллы: сожжённое топливо или полный бак за разбитых и потерянных.
    def __calc_balls(self):
        self.ball=0
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].nash == False:
                continue
            if self.airplanes[i].stolk == False and self.airplanes[i].poteryan == False:
                self.ball = self.ball + self.airplanes[i].ball_benz
            else:
                self.ball = self.ball + self.airplanes[i].izn_benzin

    # Записывает набранную высоту выбранному самолёту.
    def __apply_visota_input(self):
        if self.visota_text == "" or self.click_airplane is None:
            return
        self.click_airplane.set_zadana_visota(int(self.visota_text))
        self.visota_input = False
        self.visota_text = ""

    # Рисует плашку ввода высоты в метрах.
    def __render_visota_input(self):
        if self.visota_input == False:
            return
        x = self.gameEngine.screenx * 0.35  # левый край плашки
        y = self.gameEngine.screeny * 0.35  # верхний край плашки
        Figyrs.kvadr_poly(x, y, self.gameEngine.screenx * 0.3, self.gameEngine.screeny * 0.18, 220, self.display)
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, y + self.gameEngine.screeny * 0.04, 32, (0, 0, 0), "Высота, метры")
        if self.visota_text != "":
            shown = self.visota_text  # набранные метры
        else:
            shown = "_"  # подчёркивание, пока ничего не введено
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, y + self.gameEngine.screeny * 0.09, 36, (0, 0, 0), shown)
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, y + self.gameEngine.screeny * 0.14, 22, (0, 0, 0), "Enter — записать, Escape — отмена")

    # Берёт голосовые команды и применяет поворот или скорость к самолёту.
    def __process_voice_commands(self):
        if not getattr(self, "airplanes", None):
            while self.my_microphone.pop_command() is not None:
                pass
            return

        while True:
            cmd = self.my_microphone.pop_command()  # одна распознанная команда

            if cmd is None:
                break
            print(f"ищем {cmd["name"]} ")
            plane = None  # найденный самолёт по имени
            for p in self.airplanes:
                if p.nash == False:
                    continue
                if MyMicrophone.MyMicrophone.same_plane_name(p.name.lower(), cmd["name"]):
                    plane = p
                    break
            if plane is None:
                print(f"{cmd["name"]} не найден")
                continue
            if cmd["type"] == "turn":
                plane.add_angle(cmd["value"]/100)
            elif cmd["type"] == "speed":
                plane.add_speed(cmd["value"]/100)

    # Выбирает самолёт кликом по табличке или по спрайту.
    def __select_airplane(self, mouse_x, mouse_y):
        # Выбор таблички самолета
        for i in range(0, len(self.button_airplane)):
            if self.button_airplane[i].airplane.nash == False:
                continue
            if self.button_airplane[i].click(mouse_x, mouse_y):
                if self.click_airplane is not None:
                    self.click_airplane.click_camolet=False

                self.click_airplane = self.button_airplane[i].airplane
                self.click_airplane.click_camolet=True
                return

        # выбор самолета
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].click(mouse_x, mouse_y):
                if self.click_airplane is not None:
                    self.click_airplane.click_camolet=False
                self.click_airplane = self.airplanes[i]
                self.click_airplane.click_camolet = True


    # Начинает раунд: грузит карту из JSON.
    def init_new_game(self, level):
        self.visota_input = False
        self.visota_text = ""
        self.__new_game_from_file(level)

        #self.__init_airplanes()
        #self.__init_tyrbylentnost()

    # Читает JSON карты и создаёт самолёты, таблички, зоны и аэропорт.
    def __new_game_from_file(self, file :str):

        with open(file, 'r', encoding='utf-8') as filef:
            file_text = filef.read()  # текст файла уровня

        n=new_game_file.new_game_file([],[],[],0,0,0,0)  # пустая карта, чтобы вызвать from_json
        nn=n.from_json( self.display,file_text)  # загруженная карта
        self.circle_x = nn.finish_x
        self.circle_y = nn.finish_y
        self.circle_radiusx = nn.finish_rx
        self.circle_radiusy = nn.finish_ry
        self.Aroport=Image(self.circle_x-self.circle_radiusx, self.circle_y-self.circle_radiusy, self.circle_radiusx*2 , self.circle_radiusy*2 , self.display,'image\\Aroport.png')


        self.airplanes=[]  # самолёты этого раунда
        for i in nn.airplanes:
            s = airplane.airplane(i.x, i.y, i.dx,i.dy,  # копия самолёта с карты
                                  self.display, i.file, i.name,
                                  i.speed,
                                  i.speed_min, i.speed_max, i.angle,
                                  i.benzin, i.visota_airplane, i.visota_min, i.visota_max, i.nash, i.v_hod)
            s.set_aeroport(self.circle_x, self.circle_y, self.circle_radiusx, self.circle_radiusy)
            if s.v_hod is not None:
                for j in nn.v_hody:
                    if j.id == s.v_hod:
                        s.set_v_hod(j.storona, j.a, j.b, self.pole_x, self.pole_y, self.pole_x2, self.pole_y2)
            self.airplanes.append(s)

        self.v_hody = nn.v_hody

        self.button_finish = []  # зелёные таблички (сел)
        self.button_airplane = []  # обычные таблички
        self.button_stolk = []  # красные таблички (разбит или потерян)

        for i in range(0, len(self.airplanes)):
            tab_y = 12 + i * 110  # верх таблички
            a = board.board(12, tab_y, 220, 96, self.display, 'image\\button1.png', self.airplanes[i], (0, 210, 220))  # летит, бирюзовая рамка
            s = board.board(12, tab_y, 220, 96, self.display, 'image\\button_green.png', self.airplanes[i], (0, 255, 0))  # сел или ушёл через проём
            d = board.board(12, tab_y, 220, 96, self.display, 'image\\button_red.png', self.airplanes[i], (255, 0, 0))  # потерян, красная рамка
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)

        self.Tyrbylentnost = []  # турбулентные зоны карты
        for i in nn.tyrbylentnosts:
            s = Tyrbylentnost.Tyrbylentnost(self.display, i.x,i.y, i.dx,i.dy,i.file)
            self.Tyrbylentnost.append(s)
        if len(self.Tyrbylentnost) > 0:
            self.Tyrbylentnost[0].doklad()  # на старте карты известен один доклад

        self.n_zona = []  # запретные зоны карты
        for i in nn.zona:
            s = Zona.zona(self.display, i.points,i.color)
            self.n_zona.append(s)

    # Случайные самолёты без JSON. На карты сейчас не влияет.
    def __init_airplanes(self):
        self.airplanes = []
        n = 0  # номер рейса
        for i in range(0, 2):
            n = n + 1
            self.scx = random.randint(200, 1600)  # случайный X
            self.scy = random.randint(200, 800)  # случайный Y
            self.speed_min = random.randint(2, 6)  # нижний предел скорости
            self.speed_min = self.speed_min / 10
            self.speed_max = random.randint(3, 5)  # верхний предел скорости
            self.angle = random.randint(0, 360)  # случайный курс
            s = airplane.airplane(self.scx, self.scy, self.gameEngine.screenx * 0.017,
                                  self.gameEngine.screeny * 0.03,
                                  self.display, 'image\\camolet2.png', f"Рейс{n}",
                                  (self.speed_min + self.speed_max) / 2,
                                  self.speed_min, self.speed_max, self.angle,
                                  1500, 914, 305, 3048)
            self.airplanes.append(s)


        self.button_finish = []  # зелёные таблички
        self.button_airplane = []  # обычные таблички
        self.button_stolk = []  # красные таблички

        for i in range(0, len(self.airplanes)):
            tab_y = 12 + i * 110  # верх таблички
            a = board.board(12, tab_y, 220, 96, self.display, 'image\\button1.png', self.airplanes[i], (0, 210, 220))  # летит, бирюзовая рамка
            s = board.board(12, tab_y, 220, 96, self.display, 'image\\button_green.png', self.airplanes[i], (70, 190, 120))  # сел, зелёная рамка
            d = board.board(12, tab_y, 220, 96, self.display, 'image\\button_red.png', self.airplanes[i], (190, 70, 80))  # потерян, красная рамка
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)
