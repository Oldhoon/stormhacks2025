import pygame
import sys
from pygame.locals import *

FPS = pygame.time.Clock()

FPS.tick(60)


pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

knight_a1_sprite_sheet_image = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 1.png").convert_alpha()
knight_a2_sprite_sheet_image = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 2.png").convert_alpha()
knight_a3_sprite_sheet_image = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 3.png").convert_alpha()
knight_d_sprite_sheet_image = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/DEATH.png").convert_alpha()
knight_h_sprite_sheet_image = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/HURT.png").convert_alpha()
knight_i_sprite_sheet_image = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/IDLE.png").convert_alpha()
knight_w_sprite_sheet_image = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/WALK.png").convert_alpha()

# Clock for frame rate
clock = pygame.time.Clock()
FPS = 60

#test smth
background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
# Game loop begins
while True:
    #TODO
    
    screen.blit(background, (0, 0))
    screen.blit(knight_w_sprite_sheet_image, (0, 0))
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()
sys.exit()



