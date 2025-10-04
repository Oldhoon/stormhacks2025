import pygame
FRAME_WIDTH = 96
FRAME_HEIGHT = 84

samurai_sheet = pygame.image.load("assets/FREE_Samurai 2D Pixel Art v1.2/Sprites/IDLE.png")


def get_sprite(sheet, x, y, width, height):
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    sprite.blit(sheet, (0,0), (x,y,width,height))
    return sprite

# animation frames
frames = []

for i in range(10):
    sp = get_sprite(samurai_sheet, i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
    frames.append(sp)