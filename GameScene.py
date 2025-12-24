import random
import airplane
import Class
import pygame
import Figyrs
from Image import Image
import board
import math


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
        self.circle_x=self.game.screenx*0.8
        self.circle_y=self.game.screeny*0.07
        self.circle_radiusx = self.game.screenx * 0.03
        self.circle_radiusy = self.game.screeny * 0.06
        self.gorax = random.randint(3, 7) / 10
        self.goray = random.randint(3, 7) / 10

        self.airplanes=[]
        n=0
        for i in range(0,1):
            n=n+1
            self.scx = random.randint(200, 1600)
            self.scy = random.randint(200, 800)
            self.speed_min = 1
            self.speed_max = 5
            self.angle = random.randint(0, 360)
            s=airplane.airplane(game,self.scx,self.scy,game.screenx * 0.017,game.screeny * 0.03,display,'image\\camolet2.png',f"Рейс {n}",self.speed_min,self.speed_min,self.speed_max,self.angle)
            self.airplanes.append(s)


        self.button_finish = []
        self.button_airplane=[]
        self.button_stolk=[]
        for i in range(0,len(self.airplanes)):
            a=board.board(game.screenx * 0,i*game.screeny * 0.07,game.screenx * 0.1,game.screeny * 0.07,self.display,'image\\button.png',self.airplanes[i])
            s=board.board(game.screenx * 0,i*game.screeny * 0.07,game.screenx * 0.1,game.screeny * 0.07,self.display, 'image\\button_green.png',self.airplanes[i])
            d=board.board(game.screenx * 0,i*game.screeny * 0.07, game.screenx * 0.1, game.screeny*0.07,self.display, 'image\\button_red.png', self.airplanes[i])
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)


    def handle_events(self, events):
        for event in events:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_exit.click(mouse_x, mouse_y):
                    self.game.change_scene("menu")
                    self.airplanes = []
                    n=0
                    for i in range(0, 1):
                        n=n+1
                        self.scx = random.randint(200, 1600)
                        self.scy = random.randint(200, 800)
                        self.speed_min = random.randint(2, 6)
                        self.speed_min = self.speed_min / 10
                        self.speed_max = random.randint(3, 5)
                        self.angle = random.randint(0, 360)
                        s = airplane.airplane(self.game, self.scx, self.scy, self.game.screenx * 0.017, self.game.screeny * 0.03,
                                              self.display, 'image\\camolet2.png', f"Рейс{n}", self.speed_min,
                                              self.speed_min, self.speed_max, self.angle)
                        self.airplanes.append(s)
                    self.gorax = random.randint(3, 7) / 10
                    self.goray = random.randint(3, 7) / 10
                    return

                for i in range(0,len(self.button_airplane)):
                    if self.button_airplane[i].click(mouse_x, mouse_y):
                        self.click_airplane=self.button_airplane[i].airplane

                for i in range(0, len(self.airplanes)):
                    if self.airplanes[i].click(mouse_x, mouse_y):
                        self.click_airplane=self.airplanes[i]
                    if self.click_airplane== self.airplanes[i]:
                        if self.button_pravo.click(mouse_x, mouse_y):
                            self.click_airplane.add_angle(-8)
                            break
                        if self.button_levo.click(mouse_x, mouse_y):
                            self.click_airplane.add_angle(8)
                            break
                        if self.button_increase.click(mouse_x, mouse_y):
                            self.click_airplane.add_speed(0.4)
                            break
                        if self.button_reduce.click(mouse_x, mouse_y):
                            self.click_airplane.add_speed(-0.4)
                            break

        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].stolk == False:
                for j in range(i + 1, len(self.airplanes)):
                    if self.airplanes[j].stolk == False:
                        x_2=self.airplanes[i].x + self.airplanes[i].dx / 2
                        x_1=self.airplanes[j].x + self.airplanes[j].dx / 2
                        y_2=self.airplanes[i].y + self.airplanes[i].dy / 2
                        y_1=self.airplanes[j].y + self.airplanes[j].dy / 2
                        # находим растояние между центром самолётов
                        d = math.sqrt((x_2 - x_1)*(x_2 - x_1) + (y_2 - y_1)*(y_2 - y_1))
                        if self.airplanes[i].dx/2 + self.airplanes[j].dx/2 >= d or self.airplanes[i].dy/2 + self.airplanes[j].dy/2 >= d:
                            self.airplanes[i].stolk = True
                            self.airplanes[j].stolk = True

        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].stolk == False:
                x1 = self.airplanes[i].x + self.airplanes[i].dx / 2
                y1 = self.airplanes[i].y + self.airplanes[i].dy / 2
                x2 = self.circle_x# + self.circle_radiusx/2-30
                y2 = self.circle_y# + self.circle_radiusy/2-30
                # находим растояние между центром самолётов
                d = math.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))
                if self.airplanes[i].dx + self.circle_radiusx/2 >= d or self.airplanes[i].dy/2 + self.circle_radiusy >= d:
                    self.airplanes[i].stolk = True
                    self.airplanes[i].finish = True

        self.Radar.angle = self.Radar.angle - 4

    def update(self):
        #self.air.move()
        for i in range(0,len(self.airplanes)):
            self.airplanes[i].move()
        return

    def render(self):
        self.Radar.render()
        self.button_exit.render()
        self.button_pravo.render()
        self.button_levo.render()
        self.button_increase.render()
        self.button_reduce.render()
        pygame.draw.circle(self.display, (255, 0, 0), (self.circle_x, self.circle_y),self.circle_radiusx)
        pygame.draw.circle(self.display, (0, 255, 0), (self.game.screenx*self.gorax, self.game.screeny*self.goray), self.circle_radiusx*1.3)



        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].stolk == False:
                self.airplanes[i].render()

        for i in range(0, len(self.button_airplane)):
            if self.airplanes[i].stolk == True:
                self.button_stolk[i].render()
            else:
                self.button_airplane[i].render()
            if self.airplanes[i].benzin<=0:
                self.button_stolk[i].render()
            if self.airplanes[i].finish == True:
                self.button_finish[i].render()


"""
self.speed_min = random.randint(2,6 )
self.speed_min=self.speed_min/10
self.speed_max = random.randint(5, 7)

            if self.airplanes[i].benzin>0 and self.airplanes[i].stolk == False:
                self.airplanes[i].benzin = self.airplanes[i].benzin + self.airplanes[i].minysben
                self.airplanes[i].move()
            else:
                if self.airplanes[i].benzin > 0:
                    self.airplanes[i].benzin=0
"""