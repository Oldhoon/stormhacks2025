import pygame.time

import spritesheet
import pygame as pg
import spritesheet

FW = 96
FH = 84
MAX_HP =100
START_X = 0
START_Y = 0 # top left corner for now #TODO
SCALE = 3
COLOR = (0,0,0)

animation_cooldown= 200

animation_steps = [7, 4, 10 ,16]
ATTACK_STEPS = 7
HURT_STEPS = 4
IDLE_STEPS = 10
RUN_STEPS = 16
class Samurai:

    def __init__(self):
        # Load sprite sheets
        self.attack_sheet= pg.image.load('assets/FREE_Samurai 2D Pixel Art v1.2/Sprites/ATTACK 1.png').convert_alpha()
        self.hurt_sheet = pg.image.load('assets/FREE_Samurai 2D Pixel Art v1.2/Sprites/HURT.png').convert_alpha()
        self.idle_sheet = pg.image.load('assets/FREE_Samurai 2D Pixel Art v1.2/Sprites/IDLE.png').convert_alpha()
        self.run_sheet = pg.image.load('assets/FREE_Samurai 2D Pixel Art v1.2/Sprites/RUN.png').convert_alpha()

        spritesheet_attack = spritesheet.SpriteSheet(self.attack_sheet)
        spritesheet_hurt = spritesheet.SpriteSheet(self.hurt_sheet)
        spritesheet_idle = spritesheet.SpriteSheet(self.idle_sheet)
        spritesheet_run = spritesheet.SpriteSheet(self.run_sheet)

        self.attack_list = []
        self.hurt_list = []
        self.idle_list = []
        self.run_list = []

        for i in range(animation_steps[0]):
            self.attack_list.append(spritesheet_attack.get_image(i, FW, FH, SCALE, COLOR))

        for i in range(HURT_STEPS):
            self.hurt_list.append(spritesheet_hurt.get_image(i, FW, FH, SCALE, COLOR))

        for i in range(IDLE_STEPS):
            self.idle_list.append(spritesheet_idle.get_image(i, FW, FH, SCALE, COLOR))

        for i in range(RUN_STEPS):
            self.run_list.append(spritesheet_run.get_image(i, FW,FH,SCALE,COLOR))

        self.current_sheet= self.idle_sheet
        # self.current_frames =
        self.frame_index = 0
        self.position = (START_X,START_Y)

    def update(self):
        """Update samurai state"""
        self.frame_index = (self.frame_index + 1) % 7
        pass

    def draw(self, screen):
        """Draw samurai on screen"""
        screen.blit(self.attack_list[self.frame_index], (0,0))

    def set_animation(self, animation_type):
        """Change animation type"""
        # if animation_type in self.animations:
        #     self.current_frames = self.animations[animation_type]
        #     self.frame_index=0
