import random
import Microphon
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
import time
# Очередь для передачи команд
command_queue = queue.Queue()
class GameScene(Class.Scene):
    def __init__(self, gameEngine, display):
        super().__init__(gameEngine)
        self.display = display
        self.button_exit = Image(gameEngine.screenx * 0.902, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09, self.display,'image\\bsxod.PNG')
        self.button_pravo = Image(gameEngine.screenx * 0.6, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09,self.display, 'image\\pravo.png')
        self.button_levo = Image(gameEngine.screenx * 0.5, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.1,self.display, 'image\\levo.png')
        self.button_increase = Image(gameEngine.screenx * 0.4, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.093,self.display, 'image\\increase.png')
        self.button_reduce = Image(gameEngine.screenx * 0.3, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09,self.display, 'image\\reduse.png')
        self.Radar = Image(gameEngine.screenx * -0.125, gameEngine.screeny * -0.6, gameEngine.screenx * 1.3, gameEngine.screeny * 2.3,self.display, 'image\\Radar3.png')
        self.Aroport=0
        self.gameEngine=gameEngine
        self.display=display
        self.click_airplane = None
        self.circle_x=0
        self.circle_y=0
        self.circle_radiusx = 0
        self.circle_radiusy = 0
        self.end_game=False
        self.airplanes_stolk=0
        self.airplanes_finish=0
        self.airplanes_poteryan=0
        self.ball = 0

    def handle_events(self, events):
        for event in events:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_exit.click(mouse_x, mouse_y):
                    self.gameEngine.change_scene("menu")
                for i in range(0, len(self.airplanes)):
                #    if self.airplanes[i].click(mouse_x, mouse_y):
                        self.__select_airplane(mouse_x, mouse_y)

                if self.click_airplane is not None:
                    if self.button_pravo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(-30)
                    if self.button_levo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(30)
                    if self.button_increase.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(1.5)
                    if self.button_reduce.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(-1.5)
        Microphon.vabor(self.click_airplane)

    def update(self):

        self.__update_move_airplanes()
        self.__calc_balls()

        game_end = 0
        self.airplanes_stolk = 0
        self.airplanes_finish = 0
        self.airplanes_poteryan = 0
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False:
                for j in range(i + 1, len(self.airplanes)):
                    if self.airplanes[j].stolk == False and self.airplanes[i].finish == False:
                        x_2 = self.airplanes[i].x + self.airplanes[i].dx / 2
                        x_1 = self.airplanes[j].x + self.airplanes[j].dx / 2
                        y_2 = self.airplanes[i].y + self.airplanes[i].dy / 2
                        y_1 = self.airplanes[j].y + self.airplanes[j].dy / 2

                        # находим растояние между центром самолётов
                        d = math.sqrt((x_2 - x_1) * (x_2 - x_1) + (y_2 - y_1) * (y_2 - y_1))
                        if self.airplanes[i].dx / 2 + self.airplanes[j].dx / 2 >= d or self.airplanes[i].dy / 2 + \
                                self.airplanes[j].dy / 2 >= d:
                            self.airplanes[i].stolk = True
                            self.airplanes[j].stolk = True

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False:
                x1 = self.airplanes[i].x + self.airplanes[i].dx / 2
                y1 = self.airplanes[i].y + self.airplanes[i].dy / 2
                x2 = self.circle_x
                y2 = self.circle_y
                # находим растояние между центром самолёта и финиша
                d = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
                if self.airplanes[i].dx + self.circle_radiusx / 2 >= d or self.airplanes[
                    i].dy + self.circle_radiusy / 2 >= d:
                    self.airplanes[i].finish = True

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                if 0 >= self.airplanes[i].x or self.gameEngine.screenx <= self.airplanes[i].x + self.airplanes[i].dx or 0 >= \
                        self.airplanes[i].y or self.gameEngine.screeny <= self.airplanes[i].y + self.airplanes[i].dy:
                    self.airplanes[i].poteryan = True
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                for j in range(0, len(self.Pogoda)):
                    if self.Pogoda[j].select(self.airplanes[i].x, self.airplanes[i].y, self.airplanes[i].dx,self.airplanes[i].dy) == True:
                        self.airplanes[i].stolk=True

            if self.airplanes[i].stolk == True:
                self.airplanes_stolk = self.airplanes_stolk + 1
            if self.airplanes[i].finish == True:
                self.airplanes_finish = self.airplanes_finish + 1
            if self.airplanes[i].poteryan == True:
                self.airplanes_poteryan = self.airplanes_poteryan + 1

            if self.airplanes[i].stolk == True or self.airplanes[i].finish == True or self.airplanes[
                i].poteryan == True:
                game_end = game_end + 1

        if game_end == len(self.airplanes):
            self.end_game = True
        else:
            self.Radar.angle = self.Radar.angle - 4

    def render(self):
        self.Radar.render()
        self.button_exit.render()
        self.button_pravo.render()
        self.button_levo.render()
        self.button_increase.render()
        self.button_reduce.render()
        self.Aroport.render()

        self.__render_tyrbylentnost()
        self.__render_airplanes()
        self.__render_button_airplanes()

        if self.end_game == True:
            self.__render_end_game()
            self.end_game=False

    def __render_tyrbylentnost(self):
        for i in range(0, len(self.Tyrbylentnost)):
            self.Tyrbylentnost[i].render()
        for i in range(0, len(self.Pogoda)):
            self.Pogoda[i].render()

    def __render_airplanes(self):
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                if self.airplanes[i].click_camolet==True:
                    self.airplanes[i].camolet = Image(self.airplanes[i].x, self.airplanes[i].y, self.airplanes[i].dx,
                                                      self.airplanes[i].dy, self.display, "image\\camolet3.png",self.airplanes[i].angle)

                else:
                    self.airplanes[i].camolet = Image(self.airplanes[i].x, self.airplanes[i].y, self.airplanes[i].dx,
                                                     self.airplanes[i].dy, self.display, "image\\camolet2.png",self.airplanes[i].angle)

                self.airplanes[i].render()

    def __render_end_game(self):
        Figyrs.kvadr_poly(self.gameEngine.screenx*0.25,self.gameEngine.screeny*0.25,self.gameEngine.screenx*0.5,self.gameEngine.screeny*0.4,200,self.display)
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.505, self.gameEngine.screeny * 0.35,80, (0, 0, 0),f"Баллы = {int(self.ball)}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.4,self.gameEngine.screeny * 0.45,40,(0,0,0),f"Столкнулись = {self.airplanes_stolk}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, self.gameEngine.screeny * 0.5, 40, (0, 0, 0),f"Потерены = {self.airplanes_poteryan}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.62, self.gameEngine.screeny * 0.45,40, (0, 0, 0),f"Прилетели в аэропорт = {self.airplanes_finish}")


    def __render_button_airplanes(self):
        if self.button_airplane is None:
            return
        for i in range(0, len(self.button_airplane)):
            if self.airplanes[i].stolk != True:
                self.button_airplane[i].render()
                if self.airplanes[i].Zapr_zon == True:
                    Figyrs.print_text(self.display, self.button_airplane[i].x + self.button_airplane[i].dx / 2,
                                      self.button_airplane[i].y+self.gameEngine.screeny*0.01+ self.button_airplane[i].dy, 20, (0, 0, 0),
                                      f"Самолёт в ветреной зоне")
            else:
                self.button_stolk[i].render()
            if self.airplanes[i].poteryan == True:
                self.button_stolk[i].render()
            if self.airplanes[i].benzin <= 0:
                self.button_stolk[i].render()
            if self.airplanes[i].finish == True:
                self.button_finish[i].render()

    def __update_move_airplanes(self):
        for i in range(0,len(self.airplanes)):
            self.airplanes[i].move()

            k=0
            for j in range(0, len(self.Tyrbylentnost)):
                if self.Tyrbylentnost[j].select(self.airplanes[i].x,self.airplanes[i].y,self.airplanes[i].dx,self.airplanes[i].dy)==True:
                    self.airplanes[i].Zapr_zon=True
                    k=1
                    break
                else:
                    self.airplanes[i].Zapr_zon=False
            if k==0:
                self.airplanes[i].ymn_koef_ball(1)
            else:
                self.airplanes[i].ymn_koef_ball(5)

    def __calc_balls(self):
        self.ball=0
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].stolk == False and self.airplanes[i].poteryan == False:
                self.ball = self.ball + self.airplanes[i].ball_benz
            else:
                self.ball = self.ball + self.airplanes[i].izn_benzin

    def __select_airplane(self, mouse_x, mouse_y):
        # Выбор таблички самолета
        for i in range(0, len(self.button_airplane)):
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


    def init_new_game(self, level):

        self.__new_game_from_file(level)

        #self.__init_airplanes()
        #self.__init_tyrbylentnost()

    def __new_game_from_file(self, file :str):

        with open(file, 'r', encoding='utf-8') as filef:
            file_text = filef.read()

        n=new_game_file.new_game_file([],[],[],0,0,0,0)
        nn=n.from_json( self.display,file_text)
        self.circle_x = nn.finish_x
        self.circle_y = nn.finish_y
        self.circle_radiusx = nn.finish_rx
        self.circle_radiusy = nn.finish_ry
        self.Aroport=Image(self.circle_x-self.circle_radiusx, self.circle_y-self.circle_radiusy, self.circle_radiusx*2 , self.circle_radiusy*2 , self.display,'image\\Aroport.png')


        self.airplanes=[]
        for i in nn.airplanes:
            s = airplane.airplane(i.x, i.y, i.dx,i.dy,
                                  self.display, i.file, i.name,
                                  i.speed,
                                  i.speed_min, i.speed_max, i.angle,
                                  i.benzin)
            self.airplanes.append(s)

        self.button_finish = []
        self.button_airplane = []
        self.button_stolk = []

        for i in range(0, len(self.airplanes)):
            a = board.board(self.gameEngine.screenx * 0, i*1.4 * self.gameEngine.screeny * 0.07, self.gameEngine.screenx * 0.11,
                            self.gameEngine.screeny * 0.08,
                            self.display, 'image\\button1.png', self.airplanes[i])
            s = board.board(self.gameEngine.screenx * 0, i*1.4 * self.gameEngine.screeny * 0.07, self.gameEngine.screenx * 0.11,
                            self.gameEngine.screeny * 0.08,
                            self.display, 'image\\button_green.png', self.airplanes[i])
            d = board.board(self.gameEngine.screenx * 0, i*1.4 * self.gameEngine.screeny * 0.07, self.gameEngine.screenx * 0.11,
                            self.gameEngine.screeny * 0.08,
                            self.display, 'image\\button_red.png', self.airplanes[i])
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)

        self.Tyrbylentnost = []
        for i in nn.tyrbylentnosts:
            s = Tyrbylentnost.Tyrbylentnost(self.display, i.x,i.y, i.dx,i.dy,i.file)
            self.Tyrbylentnost.append(s)

        self.Pogoda=[]
        for i in nn.pogoda:
            s = Pogoda.Pogoda(self.display, i.x,i.y, i.dx,i.dy,i.file)
            self.Pogoda.append(s)

    def __init_airplanes(self):
        self.airplanes = []
        n = 0
        for i in range(0, 2):
            n = n + 1
            self.scx = random.randint(200, 1600)
            self.scy = random.randint(200, 800)
            self.speed_min = random.randint(2, 6)
            self.speed_min = self.speed_min / 10
            self.speed_max = random.randint(3, 5)
            self.angle = random.randint(0, 360)
            s = airplane.airplane(self.scx, self.scy, self.gameEngine.screenx * 0.017,
                                  self.gameEngine.screeny * 0.03,
                                  self.display, 'image\\camolet2.png', f"Рейс{n}",
                                  (self.speed_min + self.speed_max) / 2,
                                  self.speed_min, self.speed_max, self.angle,
                                  1500)
            self.airplanes.append(s)


        self.button_finish = []
        self.button_airplane = []
        self.button_stolk = []

        for i in range(0, len(self.airplanes)):
            a = board.board(self.gameEngine.screenx * 0, i * self.gameEngine.screeny * 0.07, self.gameEngine.screenx * 0.11, self.gameEngine.screeny * 0.08,
                            self.display, 'image\\button.png', self.airplanes[i])
            s = board.board(self.gameEngine.screenx * 0, i * self.gameEngine.screeny * 0.07, self.gameEngine.screenx * 0.11, self.gameEngine.screeny * 0.08,
                            self.display, 'image\\button_green.png', self.airplanes[i])
            d = board.board(self.gameEngine.screenx * 0, i * self.gameEngine.screeny * 0.07, self.gameEngine.screenx * 0.11, self.gameEngine.screeny * 0.08,
                            self.display, 'image\\button_red.png', self.airplanes[i])
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)

