import pygame
import sys
from pygame.locals import *

FPS = pygame.time.Clock()

FPS.tick(60)


pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Clock for frame rate
clock = pygame.time.Clock()
FPS = 60

#test smth
background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
# Game loop begins
while True:
    #TODO
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    screen.blit(background, (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()
sys.exit()



