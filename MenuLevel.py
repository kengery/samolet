import Class
import pygame
import Figyrs
import GameScene
from Image import Image

class MenuLevel(Class.Scene):
    def __init__(self,gameEngine, display):
        super().__init__(gameEngine)

        self.display=display
        self.fon_planer = Image(gameEngine.screenx * 0, gameEngine.screeny * 0, gameEngine.screenx, gameEngine.screeny * 0.95, self.display,
                                'image\\fon_planer.jpg')
        self.button_exit = Image(gameEngine.screenx * 0.902, gameEngine.screeny * 0, gameEngine.screenx * 0.1, gameEngine.screeny * 0.09, self.display,'image\\bsxod.PNG')
        self.button_Igra1 = Image(gameEngine.screenx * 0.05, gameEngine.screeny * 0.4, gameEngine.screenx * 0.17, gameEngine.screeny * 0.14, self.display,
                                 'image\\Button.png')
        self.button_Igra2 = Image(gameEngine.screenx * 0.25, gameEngine.screeny * 0.4, gameEngine.screenx * 0.17, gameEngine.screeny * 0.14,
                                 self.display,
                                 'image\\Button.png')
        self.button_Igra3 = Image(gameEngine.screenx * 0.45, gameEngine.screeny * 0.4, gameEngine.screenx * 0.17, gameEngine.screeny * 0.14,
                                 self.display,
                                 'image\\Button.png')
        self.button_Igra4 = Image(gameEngine.screenx * 0.65, gameEngine.screeny * 0.4, gameEngine.screenx * 0.17, gameEngine.screeny * 0.14,
                                 self.display,
                                 'image\\Button.png')
        # Уровни
        self.levels = ["levels\\level1.json","levels\\level2.json","levels\\level3.json","levels\\level4.json"]

    def handle_events(self, events):
        for event in events:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_Igra1.click(mouse_x, mouse_y):
                    # Создаем игровую сцену и передаем выбранный уровень
                    self.gameEngine.change_scene("game", self.levels[0])

                if self.button_Igra2.click(mouse_x, mouse_y):
                    # Создаем игровую сцену и передаем выбранный уровень
                    self.gameEngine.change_scene("game", self.levels[1])
                if self.button_Igra3.click(mouse_x, mouse_y):
                    # Создаем игровую сцену и передаем выбранный уровень
                    self.gameEngine.change_scene("game", self.levels[2])
                if self.button_Igra4.click(mouse_x, mouse_y):
                    # Создаем игровую сцену и передаем выбранный уровень
                    self.gameEngine.change_scene("game", self.levels[3])

                if self.button_exit.click(mouse_x,mouse_y):
                    self.gameEngine.change_scene("menu")

    def update(self):
        return

    def render(self):
        self.fon_planer.render()
        self.button_exit.render()
        self.button_Igra1.render()
        self.button_Igra2.render()
        self.button_Igra3.render()
        self.button_Igra4.render()
        Figyrs.print_text(self.display,self.gameEngine.screenx * 0.14, self.gameEngine.screeny * 0.47,80,(0,0,0),"Карта 1")
        Figyrs.print_text(self.display,self.gameEngine.screenx * 0.34, self.gameEngine.screeny * 0.47,80,(0,0,0),"Карта 2")
        Figyrs.print_text(self.display,self.gameEngine.screenx * 0.54, self.gameEngine.screeny * 0.47,80,(0,0,0),"Карта 3")
        Figyrs.print_text(self.display,self.gameEngine.screenx * 0.74, self.gameEngine.screeny * 0.47,80,(0,0,0),"Карта 4")
