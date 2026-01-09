import random
import Tyrbylentnost
import airplane
import Class
import pygame
import Figyrs
from Image import Image
import board
import math
import new_game_file
import json

class GameScene(Class.Scene):
    def __init__(self, game, display):
        super().__init__(game)
        self.display = display
        self.button_exit = Image(game.screenx * 0.902, game.screeny * 0, game.screenx * 0.1, game.screeny * 0.09, self.display,'image\\bsxod.PNG')
        self.button_pravo = Image(game.screenx * 0.6, game.screeny * 0, game.screenx * 0.1, game.screeny * 0.09,self.display, 'image\\pravo.png')
        self.button_levo = Image(game.screenx * 0.5, game.screeny * 0, game.screenx * 0.1, game.screeny * 0.1,self.display, 'image\\levo.png')
        self.button_increase = Image(game.screenx * 0.4, game.screeny * 0, game.screenx * 0.1, game.screeny * 0.093,self.display, 'image\\increase.png')
        self.button_reduce = Image(game.screenx * 0.3, game.screeny * 0, game.screenx * 0.1, game.screeny * 0.09,self.display, 'image\\reduse.png')
        self.Radar = Image(game.screenx * -0.125, game.screeny * -0.6, game.screenx * 1.3, game.screeny * 2.3,self.display, 'image\\Radar3.png')
        self.game=game
        self.display=display
        self.click_airplane = []
        self.circle_x=0
        self.circle_y=0
        self.circle_radiusx = 0
        self.circle_radiusy = 0
        self.play_new_game=True
        self.end_game=False
        self.airplanes_stolk=0
        self.airplanes_finish=0
        self.airplanes_poteryan=0
        self.ball = 0

        self.__init_new_game()


    def handle_events(self, events):
        for event in events:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_exit.click(mouse_x, mouse_y):
                    self.game.change_scene("menu")
                    self.play_new_game=True
                    n=new_game_file.new_game_file(self.airplanes,self.Tyrbylentnost, self.circle_x, self.circle_y, self.circle_radiusx,self.circle_radiusy)

                    print(n.to_json())

                self.__select_airplane(mouse_x, mouse_y)

                if self.click_airplane is not None:
                    if  self.button_pravo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(-8)
                    if self.button_levo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(8)
                    if self.button_increase.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(0.4)
                    if self.button_reduce.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(-0.4)

    def update(self):
        if self.play_new_game == True:
            self.__init_new_game()
            self.play_new_game = False

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
                if 0 >= self.airplanes[i].x or self.game.screenx <= self.airplanes[i].x + self.airplanes[i].dx or 0 >= \
                        self.airplanes[i].y or self.game.screeny <= self.airplanes[i].y + self.airplanes[i].dy:
                    self.airplanes[i].poteryan = True

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

        # TODO сделать через image
        pygame.draw.circle(self.display, (255, 0, 0), (self.circle_x, self.circle_y),self.circle_radiusx)

        self.__render_tyrbylentnost()
        self.__render_airplanes()
        self.__render_button_airplanes()

        if self.end_game == True:
            self.__render_end_game()

    def __render_tyrbylentnost(self):
        for i in range(0, len(self.Tyrbylentnost)):
            self.Tyrbylentnost[i].render()

    def __render_airplanes(self):
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                self.airplanes[i].render()

    def __render_end_game(self):
        Figyrs.kvadr_poly(self.game.screenx*0.25,self.game.screeny*0.25,self.game.screenx*0.5,self.game.screeny*0.4,200,self.display)
        Figyrs.print_text(self.display, self.game.screenx * 0.505, self.game.screeny * 0.35,80, (0, 0, 0),f"Баллы = {int(self.ball)}")
        Figyrs.print_text(self.display, self.game.screenx * 0.4,self.game.screeny * 0.45,40,(0,0,0),f"Столкнулись = {self.airplanes_stolk}")
        Figyrs.print_text(self.display, self.game.screenx * 0.5, self.game.screeny * 0.5, 40, (0, 0, 0),f"Потерены = {self.airplanes_poteryan}")
        Figyrs.print_text(self.display, self.game.screenx * 0.62, self.game.screeny * 0.45,40, (0, 0, 0),f"Прилетели в аэропорт = {self.airplanes_finish}")


    def __render_button_airplanes(self):
        if self.button_airplane is None:
            return
        for i in range(0, len(self.button_airplane)):
            if self.airplanes[i].stolk == True:
                self.button_stolk[i].render()
            else:
                self.button_airplane[i].render()
            if self.airplanes[i].poteryan == True:
                self.button_stolk[i].render()
            else:
                self.button_airplane[i].render()
            if self.airplanes[i].benzin <= 0:
                self.button_stolk[i].render()
            if self.airplanes[i].finish == True:
                self.button_finish[i].render()

    def __update_move_airplanes(self):
        for i in range(0,len(self.airplanes)):
            self.airplanes[i].move()

            k=0
            for j in range(0, len(self.Tyrbylentnost)):
                if self.Tyrbylentnost[j].select(self.airplanes[i].x,self.airplanes[i].y,self.airplanes[i].dx,self.airplanes[i].dy,self.game.screenx * 0.09,self.game.screeny * 0.12)==True:
                    k=1
                    break
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
                self.click_airplane = self.button_airplane[i].airplane
                break
        # выбор самолета
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].click(mouse_x, mouse_y):
                self.click_airplane = self.airplanes[i]
                break

    def __init_new_game(self):

        """
        self.circle_x=self.game.screenx*0.8
        self.circle_y=self.game.screeny*0.07
        self.circle_radiusx = self.game.screenx * 0.03
        self.circle_radiusy = self.game.screeny * 0.06
        """
        self.__new_game_from_file("levels\\level1.json")

        #self.__init_airplanes()
        #self.__init_tyrbylentnost()

    def __new_game_from_file(self, file :str):

        with open(file, 'r', encoding='utf-8') as file:
            file_text = file.read()

        n=new_game_file.new_game_file([],[],0,0,0,0)
        nn=n.from_json( self.display,file_text)
        self.circle_x = nn.finish_x
        self.circle_y = nn.finish_y
        self.circle_radiusx = nn.finish_rx
        self.circle_radiusy = nn.finish_ry


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
            a = board.board(self.game.screenx * 0, i * self.game.screeny * 0.07, self.game.screenx * 0.11,
                            self.game.screeny * 0.07,
                            self.display, 'image\\button.png', self.airplanes[i])
            s = board.board(self.game.screenx * 0, i * self.game.screeny * 0.07, self.game.screenx * 0.11,
                            self.game.screeny * 0.07,
                            self.display, 'image\\button_green.png', self.airplanes[i])
            d = board.board(self.game.screenx * 0, i * self.game.screeny * 0.07, self.game.screenx * 0.11,
                            self.game.screeny * 0.07,
                            self.display, 'image\\button_red.png', self.airplanes[i])
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)

        self.Tyrbylentnost = []
        for i in nn.tyrbylentnosts:
            s = Tyrbylentnost.Tyrbylentnost(self.display, i.x,i.y, i.dx,i.dy,i.file)
            self.Tyrbylentnost.append(s)



    def __init_airplanes(self):
        self.play_new_game = False
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
            s = airplane.airplane(self.scx, self.scy, self.game.screenx * 0.017,
                                  self.game.screeny * 0.03,
                                  self.display, 'image\\camolet2.png', f"Рейс{n}",
                                  (self.speed_min + self.speed_max) / 2,
                                  self.speed_min, self.speed_max, self.angle,
                                  1500)
            self.airplanes.append(s)


        self.button_finish = []
        self.button_airplane = []
        self.button_stolk = []

        for i in range(0, len(self.airplanes)):
            a = board.board(self.game.screenx * 0, i * self.game.screeny * 0.07, self.game.screenx * 0.11, self.game.screeny * 0.07,
                            self.display, 'image\\button.png', self.airplanes[i])
            s = board.board(self.game.screenx * 0, i * self.game.screeny * 0.07, self.game.screenx * 0.11, self.game.screeny * 0.07,
                            self.display, 'image\\button_green.png', self.airplanes[i])
            d = board.board(self.game.screenx * 0, i * self.game.screeny * 0.07, self.game.screenx * 0.11, self.game.screeny * 0.07,
                            self.display, 'image\\button_red.png', self.airplanes[i])
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)

    def __init_tyrbylentnost(self):
        self.Tyrbylentnost=[]
        for i in range(0,2):
            self.gora_x = random.randint(3, 7) / 10
            self.gora_y = random.randint(3, 7) / 10
            s= Tyrbylentnost.Tyrbylentnost(self.display, self.game.screenx*self.gora_x, self.game.screeny*self.gora_y, self.game.screeny * 0.2, self.game.screeny * 0.22,'image\\Tyrbylent-Photoroom.png')
            self.Tyrbylentnost.append(s)