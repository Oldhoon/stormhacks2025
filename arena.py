import pygame
import sys
from pygame.locals import *

FPS = pygame.time.Clock()

FPS.tick(60)


pygame.init()


DISPLAYSURF = pygame.display.set_mode((300,300))
# Game loop begins
while True:
    #TODO
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()



