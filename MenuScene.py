import Class
import pygame

import Figyrs
import GameScene
import board
import airplane
import random
import sys
from Image import Image

# Главное меню: «Начать» и «Выход».
class MenuScene(Class.Scene):
    # Создаёт фон и две кнопки меню.
    def __init__(self, gameEngine,display):
        super().__init__(gameEngine)
        self.gameEngine=gameEngine  # движок сцен
        self.display=display  # окно pygame
        self.Button_play = Image(gameEngine.screenx * 0.42, gameEngine.screeny * 0.25, gameEngine.screenx * 0.17,gameEngine.screeny * 0.14, self.display,
                                 'image\\Button.png')  # кнопка «Начать»
        self.Button_exit = Image(gameEngine.screenx * 0.42, gameEngine.screeny * 0.4, gameEngine.screenx * 0.17,gameEngine.screeny * 0.14, self.display,
                                 'image\\Button.png')  # кнопка «Выход»
        self.fon_planer = Image(gameEngine.screenx * 0, gameEngine.screeny * 0, gameEngine.screenx, gameEngine.screeny * 0.95, self.display,
                                'image\\fon_planer.jpg')  # фон меню

    # «Начать» открывает выбор карты, «Выход» закрывает игру.
    def handle_events(self, events):
        for event in events:
            mouse_x, mouse_y = pygame.mouse.get_pos()  # координаты курсора
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Логика кликов по меню
                if self.Button_play.click(mouse_x,mouse_y):
                    self.gameEngine.change_scene("Menu_game")


                if self.Button_exit.click(mouse_x,mouse_y):
                    pygame.quit()
                    sys.exit()

    # В меню логики кадра нет.
    def update(self):
        return

    # Рисует фон, кнопки и подписи «Начать» / «Выход».
    def render(self):
        #Figyrs.kvadrat(self.display,(255,0,0),100,100,50)
        self.fon_planer.render()
        self.Button_play.render()
        Figyrs.print_text(self.display,self.gameEngine.screenx * 0.505,self.gameEngine.screeny * 0.315,85,(0,0,0),"Начать")
        self.Button_exit.render()
        Figyrs.print_text(self.display,self.gameEngine.screenx * 0.505,self.gameEngine.screeny * 0.465,85,(0,0,0),"Выход")
