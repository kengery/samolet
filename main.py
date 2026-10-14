# подключаем  библиотеки
import pygame
import sys
import GameEngine
import time
import numpy as np


# инициализация библиотеке pygame
pygame.init()
screenx = 1900  # ширина окна
screeny = 1005  # высота окна



g=GameEngine.GameEngine(screenx,screeny)  # игровой движок и цикл сцен
g.run()
