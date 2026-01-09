import GameScene
import MenuScene
import pygame
import sys
import random
import airplane
import board


class Game:
    def __init__(self, screenx,screeny):
        self.__clock = pygame.time.Clock()
        self.__white = (255, 255, 255)
        self.screenx=screenx
        self.screeny=screeny
        self.__display = pygame.display.set_mode((self.screenx, self.screeny), 0, 32)

        # Словарь сцен
        self.__scenes = {
            'menu': MenuScene.MenuScene(self,self.__display),
            'game': GameScene.GameScene(self,self.__display),
        }
        self.current_scene = 'menu'

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.__display.fill(self.__white)

            # Получаем текущую сцену
            scene = self.__scenes[self.current_scene]

            # Обработка событий для текущей сцены
            scene.handle_events(events)

            # Обновление логики текущей сцены
            scene.update()

            # Отрисовка текущей сцены
            scene.render()

            pygame.display.flip()
            pygame.display.update()
            pygame.time.wait(30)

    def change_scene(self, scene_name):
        """Переключение на другую сцену"""
        if scene_name in self.__scenes:
            self.current_scene = scene_name



