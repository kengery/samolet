import pygame

class Image:
    def __init__(self,x,y,dx,dy,display,file, angle=0):
        self.x=x
        self.y=y
        self.__dx=dx
        self.__dy=dy
        self.__display=display
        self.angle=angle
        image_file=pygame.image.load(file)
        self.__image = pygame.transform.scale(image_file, (self.__dx, self.__dy))

    def render(self):

        if (self.angle!=0):
            rotated_image = pygame.transform.rotate(self.__image, self.angle)
            rect = rotated_image.get_rect(center=(self.x + self.__dx / 2, self.y + self.__dy / 2))
            self.__display.blit(rotated_image, rect)
        else:
            self.__display.blit(self.__image,(self.x,self.y))

    def set_angle(self, angle):
        self.angle=angle

    def click(self,mouse_x,mouse_y)->bool:
        if self.x <mouse_x < self.x+self.__dx and self.y < mouse_y < self.y + self.__dy:
            return  True
        else:
            return False
    def set_x_y(self,x,y):
        self.x=x
        self.y=y


