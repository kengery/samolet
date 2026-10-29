import GameScene
import MenuScene
import pygame
import sys
import MenuLevel

# Цикл игры: окно, смена сцен, кадры.
class GameEngine:
    # Создаёт окно и три сцены: меню, выбор карты, симуляция.
    def __init__(self, screenx,screeny):
        self.__clock = pygame.time.Clock()  # часы pygame (в цикле не используются)
        self.__white = (255, 255, 255)  # цвет заливки кадра
        self.screenx=screenx  # ширина окна
        self.screeny=screeny  # высота окна
        self.__display = pygame.display.set_mode((self.screenx, self.screeny), 0, 32)  # поверхность окна

        # Словарь сцен
        self.__scenes = {  # имя сцены → объект сцены
            'menu': MenuScene.MenuScene(self,self.__display),
            'game': GameScene.GameScene(self,self.__display,),
            'Menu_game': MenuLevel.MenuLevel(self, self.__display),
        }
        self.current_scene = 'menu'  # какая сцена сейчас на экране

    # Главный цикл: события, обновление, отрисовка, пауза 30 мс.
    def run(self):
        while True:
            events = pygame.event.get()  # события кадра
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.__display.fill(self.__white)

            # Получаем текущую сцену
            scene = self.__scenes[self.current_scene]  # активная сцена

            # Обработка событий для текущей сцены
            scene.handle_events(events)

            # Обновление логики текущей сцены
            scene.update()

            # Отрисовка текущей сцены
            scene.render()

            pygame.display.flip()
            pygame.display.update()
            pygame.time.wait(100)

    # Переключает сцену; если есть путь к карте — запускает раунд.
    def change_scene(self, scene_name, level = ''):
        if scene_name in self.__scenes:
            self.current_scene = scene_name
            if level!='':
                self.__scenes["game"].init_new_game(level)
