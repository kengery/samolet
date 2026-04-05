# подключаем  библиотеки
import pygame
import sys
import GameEngine
import time
import numpy as np


# инициализация библиотеке pygame
pygame.init()
screenx = 1900
screeny = 1005



g=GameEngine.GameEngine(screenx,screeny)
g.run()
