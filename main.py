# подключаем  библиотеки
import pygame
import sys
import Game

# инициализация библиотеке pygame
pygame.init()
screenx = 1900
screeny = 1005

g=Game.Game(screenx,screeny)
g.run()
