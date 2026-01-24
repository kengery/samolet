# подключаем  библиотеки
import pygame
import sys
import GameEngine
import time
import numpy as np
import Microphon

# инициализация библиотеке pygame
pygame.init()
screenx = 1900
screeny = 1005



# Запускаем поток распознавания речи
global running_speech
running_speech = True
speech_thread = Microphon.threading.Thread(target=Microphon.speech_recognizer_thread, daemon=True)
speech_thread.start()

g=GameEngine.GameEngine(screenx,screeny)
g.run()
