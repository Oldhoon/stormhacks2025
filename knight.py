import pygame
import spritesheet
from samurai import MOVE_BY

FW = 96
FH = 84
MAX_HP =100
START_X = 200
START_Y = 300# top left corner for now #TODO
SCALE = 3
COLOR = (0,0,0)
ANIMATION_COOLDOWN = 200

class Knight:

    def __init__(self):

        # Load sprite sheets
        self.attack1_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 1.png").convert_alpha()
        self.death_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/DEATH.png").convert_alpha()
        self.idle_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/IDLE.png").convert_alpha()
        self.walk_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/WALK.png").convert_alpha()

        ss_attack = spritesheet.SpriteSheet(self.attack1_sheet)
        ss_death = spritesheet.SpriteSheet(self.death_sheet)
        ss_idle = spritesheet.SpriteSheet(self.idle_sheet)
        ss_walk = spritesheet.SpriteSheet(self.walk_sheet)

        def slice_all(ss, sheet):
            frames =[]
            count = sheet.get_width()//FW
            for i in range(count):
                frames.append(ss.get_image(i, FW, FH, SCALE, COLOR))
            return frames

        self.animations = {
            "attack": slice_all(ss_attack, self.attack1_sheet),
            "dead": slice_all(ss_death, self.death_sheet),
            "idle":slice_all(ss_idle, self.idle_sheet),
            "walk":slice_all(ss_walk, self.walk_sheet)
        }

        # Current animation state
        self.animation_type = "idle"
        self.frame_index = 0
        self.position = (START_X, START_Y)
        self.last_update = pygame.time.get_ticks()

        #required sprite fields
        self.image = self.animations[self.animation_type][self.frame_index]
        self.rect = self.image.get_rect()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= ANIMATION_COOLDOWN:
            self.last_update = now
            frames = self.animations[self.animation_type]
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)
                self.image = frames[self.frame_index]

    def draw(self, screen):
        animation_list = self.animations[self.animation_type]
        screen.blit(animation_list[self.frame_index], self.position)

    def set_animation(self, name):
        if name in self.animations and name != self.animation_type:
            self.animation_type = name
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            self.image = self.animations[self.animation_type][self.frame_index]

    def idle(self):
        self.set_animation("idle")

    def move_right(self):
        self.set_animation("walk")
        self.rect.x += MOVE_BY

    def move_left(self):
        self.set_animation("walk")
        self.rect.x -= MOVE_BY

    def attack(self):
        self.set_animation("attack")

    def dead(self):
        self.set_animation("dead")


    def apply_input(self, inp):
        if inp.left:
            self.move_left()
        if inp.right:
            self.move_right()
        if inp.attack:
            self.attack()