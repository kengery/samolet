import pygame
#Рисует квадрат
def kvadrat(displey,color,x,y,l):
    pygame.draw.line(displey, color, (x, y), (x + l, y))
    pygame.draw.line(displey, color, (x + l, y), (x + l, y + l))
    pygame.draw.line(displey, color, (x + l, y + l), (x, y + l))
    pygame.draw.line(displey, color, (x, y + l), (x, y))

#Отображает текст
def print_text(display,x,y,len,color,text):
    font = pygame.font.SysFont('Angeme',len)
    text_surface = font.render(text, True, (color))
    text_rect = text_surface.get_rect()
    text_rect.center = (x,y)
    display.blit(text_surface, text_rect)

#полу прозрачный квадрат
def kvadr_poly(x,y,dx,dy,pol_prozr,display):
    s = pygame.Surface((dx, dy), pygame.SRCALPHA)  # per-pixel alpha
    s.fill((255, 255, 255, pol_prozr))  # notice the alpha value in the color
    display.blit(s, (x, y))  # прозрачный квадрат