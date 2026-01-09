import Class
import pygame
import GameScene
import board
import airplane
import random
import sys
from Image import Image

class MenuScene(Class.Scene):
    def __init__(self, game,display):
        super().__init__(game)
        self.game=game
        self.display=display
        self.button_play = Image(game.screenx * 0.42, game.screeny * 0.25, game.screenx * 0.17, game.screeny * 0.14, self.display,
                                 'image\\igrat.PNG')
        self.button_exit = Image(game.screenx * 0.42, game.screeny * 0.4, game.screenx * 0.17, game.screeny * 0.14, self.display,
                                 'image\\bsxod.PNG')
        self.fon_planer = Image(game.screenx * 0, game.screeny * 0, game.screenx, game.screeny * 0.95, self.display,
                                'image\\fon_planer.jpg')

    def handle_events(self, events):
        for event in events:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Логика кликов по меню
                if self.button_play.click(mouse_x,mouse_y):
                    self.game.change_scene("game")


                if self.button_exit.click(mouse_x,mouse_y):
                    pygame.quit()
                    sys.exit()

    def update(self):
        return

    def render(self):
        #Figyrs.kvadrat(self.display,(255,0,0),100,100,50)
        self.fon_planer.render()
        self.button_play.render()
        self.button_exit.render()