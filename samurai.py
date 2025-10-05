from asyncio import timeout

import pygame.time

import spritesheet
import pygame as pg
import spritesheet

FW = 96
FH = 84
MAX_HP =100
START_X = 0
START_Y = 300# top left corner for now #TODO
SCALE = 4
COLOR = (0,0,0)
MOVE_BY = 5

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
        # attack
        for i in range(animation_steps[0]):
            self.attack_list.append(spritesheet_attack.get_image(i, FW, FH, SCALE, COLOR))
        # hurt
        for i in range(animation_steps[1]):
            self.hurt_list.append(spritesheet_hurt.get_image(i, FW, FH, SCALE, COLOR))
        # idle
        for i in range(animation_steps[2]):
            self.idle_list.append(spritesheet_idle.get_image(i, FW, FH, SCALE, COLOR))
        # run
        for i in range(animation_steps[3]):
            self.run_list.append(spritesheet_run.get_image(i, FW,FH,SCALE,COLOR))

        self.animations = {
            "attack": self.attack_list,
            "hurt": self.hurt_list,
            "idle": self.idle_list,
            "run": self.run_list
        }

        self.animation_type = "idle"
        self.frame_index = 0
        self.position = (START_X,START_Y)
        self.last_update = pg.time.get_ticks()

    def update(self):
        """Update samurai state"""
        now = pg.time.get_ticks()
        if not hasattr(self, "last_update"):
            self.last_update = now
        if now - self.last_update >= animation_cooldown:
            self.last_update = now
            frames = self.animations[self.animation_type]
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)

    def draw(self, screen):
        """Draw samurai on screen"""
        animation_list = self.animations[self.animation_type]
        screen.blit(animation_list[self.frame_index], self.position)

    def set_animation(self, animation_type):
        """Change animation type"""
        if animation_type in self.animations and animation_type != self.animation_type:
            self.animation_type = animation_type
            self.frame_index = 0
            self.last_update = pg.time.get_ticks()

    def idle(self):
        self.set_animation("idle")

    def move_right(self):
        self.set_animation("run")
        self.position = (self.position[0] + MOVE_BY, self.position[1])

    def move_left(self):
        self.set_animation("run")
        self.position = (self.position[0] - MOVE_BY, self.position[1])

    def attack(self):
        self.set_animation("attack")

    def apply_input(self, inp):
        if inp.left:
            self.move_left()
        if inp.right:
            self.move_right()
        if inp.attack:
            self.attack()