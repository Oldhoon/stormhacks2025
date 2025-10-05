import pygame
import spritesheet

FW = 96
FH = 84
MAX_HP =100
START_X = 800
START_Y = 430
SCALE = 3
COLOR = (0,0,0)
ANIMATION_COOLDOWN = 200
MOVE_BY = 5

class Knight:

    def __init__(self):

        # Load sprite sheets
        self.attack1_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 1.png").convert_alpha()
        self.death_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/DEATH.png").convert_alpha()
        self.idle_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/IDLE.png").convert_alpha()
        self.walk_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/WALK.png").convert_alpha()

        self.attack1_sheet = pygame.transform.flip(self.attack1_sheet, True, False)
        self.death_sheet = pygame.transform.flip(self.death_sheet, True, False)
        self.idle_sheet = pygame.transform.flip(self.idle_sheet, True, False)
        self.walk_sheet = pygame.transform.flip(self.walk_sheet, True, False)

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
        frame = self.animations[self.animation_type][self.frame_index]
        self.image = frame
        self.rect = self.image.get_rect(midleft=self.position)
        self.can_move_left = True
        self.hp = MAX_HP
        self.dead_time = None
        self.speed = MOVE_BY // 2
        self.alive = True

    def take_damage(self, amount):
        if self.alive:
            self.hp -= amount
            if self.hp <= 0:
                self.hp = 0
                self.alive = False
                self.dead()
                self.dead_time = pygame.time.get_ticks()
        self.position = (self.position[0] - 5, self.position[1])
    
    def revive(self):
        self.hp = MAX_HP // 2
        self.alive = True
        self.idle()
        
    def ai_update(self, samurai):
        if not self.alive:
            if self.dead_time and pygame.time.get_ticks() - self.dead_time > 15000:
                self.revive()
            return
        
        samurai_x, samurai_y = samurai.position
        knight_x, knight_y = self.position
        
        dist_x = samurai_x - knight_x
        
        if abs(dist_x) > 100:
            if dist_x > 0:
                self.position = (knight_x + self.speed, knight_y)
            else:
                self.position = (knight_x - self.speed, knight_y)
            self.set_animation("walk")
        else:
            self.attack()
            
        
    def is_alive(self):
        return self.alive


    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= ANIMATION_COOLDOWN:
            self.last_update = now
            frames = self.animations[self.animation_type]
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)
                frame = frames[self.frame_index]
                self.image = frame
        self.rect.midleft = self.position


    def draw(self, screen):
        # Always draw the flipped image
        screen.blit(self.image, self.position)

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
        self.position = (self.position[0] + MOVE_BY, self.position[1])


    def move_left(self):
        if self.can_move_left:
            self.set_animation("walk")
            self.position = (self.position[0] - MOVE_BY, self.position[1])

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

    def get_rect(self):
        return self.rect