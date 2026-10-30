import pygame
# Рисует квадрат линиями по координатам и стороне l.
def kvadrat(display,color,x,y,l):
    pygame.draw.line(display, color, (x, y), (x + l, y))  # верхняя сторона квадрата
    pygame.draw.line(display, color, (x + l, y), (x + l, y + l))  # правая сторона квадрата
    pygame.draw.line(display, color, (x + l, y + l), (x, y + l))  # нижняя сторона квадрата
    pygame.draw.line(display, color, (x, y + l), (x, y))  # левая сторона квадрата

# Рисует текст слева от точки (x, y): x — левый край строки.
def print_text_left(display, x, y, size, color, text):
    font = pygame.font.SysFont('Angeme', size)  # шрифт нужного размера
    text_surface = font.render(text, True, (color))  # картинка текста
    text_rect = text_surface.get_rect()  # прямоугольник текста
    text_rect.midleft = (x, y)
    display.blit(text_surface, text_rect)

# Рисует текст справа от точки (x, y): x — правый край строки.
def print_text_right(display, x, y, size, color, text):
    font = pygame.font.SysFont('Angeme', size)  # шрифт нужного размера
    text_surface = font.render(text, True, (color))  # картинка текста
    text_rect = text_surface.get_rect()  # прямоугольник текста
    text_rect.midright = (x, y)
    display.blit(text_surface, text_rect)

# Рисует текст по центру точки (x, y).
def print_text(display,x,y,len,color,text):
    font = pygame.font.SysFont('Angeme',len)  # шрифт нужного размера
    text_surface = font.render(text, True, (color))  # картинка текста
    text_rect = text_surface.get_rect()  # прямоугольник текста
    text_rect.center = (x,y)
    display.blit(text_surface, text_rect)

# Рисует полупрозрачный прямоугольник.
def kvadr_poly(x,y,dx,dy,pol_prozr,display):
    s = pygame.Surface((dx, dy), pygame.SRCALPHA)  # поверхность с прозрачностью
    s.fill((255, 255, 255, pol_prozr))  # белая заливка с альфой pol_prozr
    display.blit(s, (x, y))  # прозрачный квадрат
