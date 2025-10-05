import pygame
import spritesheet

FW = 96
FH = 84
MAX_HP =100
START_X = 900
START_Y = 430
SCALE = 3
COLOR = (0,0,0)
ANIMATION_COOLDOWN = 200
MOVE_BY = 5

HEALTH_FW = 48  # Health frame width
HEALTH_FH = 16  # Health frame height
HEALTH_SCALE = 2  # Health scale
HEALTH_STYLE = 0  # 0=blue, 1=green, 2=gray, 3=pink, 4=purple, 5=red/orange
HEALTH_DISPLAY_SCALE = 1.5
DAMAGE_AMOUNT = 100 # Amount of damage taken when hurt

class Knight:

    def __init__(self):

        # Load sprite sheets
        self.attack1_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 1.png").convert_alpha()
        self.death_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/DEATH.png").convert_alpha()
        self.idle_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/IDLE.png").convert_alpha()
        self.walk_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/WALK.png").convert_alpha()
    
        health_sheet_full = pygame.image.load(r"assets/health.png").convert_alpha()
        y_start = 16 + (HEALTH_STYLE * 16)  # Skip first row (hearts), start at row 1
        self.health_sheet = health_sheet_full.subsurface((0, y_start, 256, 16)).copy()

        self.attack1_sheet = pygame.transform.flip(self.attack1_sheet, True, False)
        self.death_sheet = pygame.transform.flip(self.death_sheet, True, False)
        self.idle_sheet = pygame.transform.flip(self.idle_sheet, True, False)
        self.walk_sheet = pygame.transform.flip(self.walk_sheet, True, False)

        ss_attack = spritesheet.SpriteSheet(self.attack1_sheet)
        ss_death = spritesheet.SpriteSheet(self.death_sheet)
        ss_idle = spritesheet.SpriteSheet(self.idle_sheet)
        ss_walk = spritesheet.SpriteSheet(self.walk_sheet)
        ss_health = spritesheet.SpriteSheet(self.health_sheet)


        def slice_all(ss, sheet):
            frames =[]
            count = sheet.get_width()//FW
            for i in range(count):
                frames.append(ss.get_image(i, FW, FH, SCALE, COLOR))
            return frames
    
        def slice_health(ss, sheet):
            frames = []
            count = sheet.get_width() // HEALTH_FW
            for i in range(count):
                frames.append(ss.get_image(i, HEALTH_FW, HEALTH_FH, HEALTH_SCALE, COLOR))
            return frames

        self.animations = {
            "attack": slice_all(ss_attack, self.attack1_sheet),
            "dead": slice_all(ss_death, self.death_sheet),
            "idle":slice_all(ss_idle, self.idle_sheet),
            "health":slice_health(ss_health, self.health_sheet),
            "walk":slice_all(ss_walk, self.walk_sheet)
        }
        self.animations["walk"].reverse()

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
        self.can_move_right = True
        self.hp = MAX_HP
        # self.dead_time = None
        # self.speed = MOVE_BY // 2
        
        # combat related fields
        self.alive = True
        self.attack_hit_applied = False
        self.can_take_damage = False
        self.is_attacking = False

    
    def revive(self):
        self.hp = MAX_HP // 2
        self.alive = True
        self.idle()
        
    # def ai_update(self, samurai):
    #     if not self.alive:
    #         if self.dead_time and pygame.time.get_ticks() - self.dead_time > 15000:
    #             self.revive()
    #         return
        
    #     samurai_x, samurai_y = samurai.position
    #     knight_x, knight_y = self.position
        
    #     dist_x = samurai_x - knight_x
        
    #     if abs(dist_x) > 100:
    #         if dist_x > 0:
    #             self.position = (knight_x + self.speed, knight_y)
    #         else:
    #             self.position = (knight_x - self.speed, knight_y)
    #         self.set_animation("walk")
    #     else:
    #         self.attack()
            
    def get_health_frame_index(self):
        if len(self.animations["health"]) == 0:
            return 0
        
        health_percent = self.hp / MAX_HP
        max_index = len(self.animations["health"]) - 1
        
        # Map health percentage to frame index
        frame_index = max_index - int(health_percent * max_index)
        return min(frame_index, max_index)


    def update(self):
        now = pygame.time.get_ticks()
        if not hasattr(self, "last_update"):
            self.last_update = now
        if now - self.last_update >= ANIMATION_COOLDOWN:
            self.last_update = now
            frames = self.animations[self.animation_type]
            if frames:
                self.frame_index += 1
                if self.animation_type == "attack":
                    if self.frame_index >= len(frames):
                        self.is_attacking = False
                        self.frame_index = 0
                        self.idle()
                else:
                    self.frame_index %= len(frames)
        self.rect.midleft = self.position
        self.image = self.animations[self.animation_type][self.frame_index]




    def draw(self, screen):
        # Always draw the flipped image
        screen.blit(self.image, self.position)
        if self.animations["health"]:
            health_index = self.get_health_frame_index()
            health_frame = self.animations["health"][health_index]            
            original_width = health_frame.get_width()
            original_height = health_frame.get_height()
            new_width = int(original_width * HEALTH_DISPLAY_SCALE)
            new_height = int(original_height * HEALTH_DISPLAY_SCALE)
            health_frame = pygame.transform.scale(health_frame, (new_width, new_height))
            # Position health bar above knight (adjust these values)
            health_x = self.position[0] + 80  # Move horizontally
            health_y = self.position[1] - 20  # Closer to head (increase negative to go higher)
            screen.blit(health_frame, (health_x, health_y))

    def set_animation(self, name):
        if name == "attack":
            if self.is_attacking:
                return
            self.is_attacking = True
            self.attack_hit_applied = False
            
        """Change animation type"""
        if name in self.animations and name != self.animation_type:
            self.animation_type = name
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            self.image = self.animations[self.animation_type][self.frame_index]
            
    def take_damage(self):
        if self.can_take_damage and not self.is_attacking:
            self.hp -= DAMAGE_AMOUNT
            if self.hp <= 0:
                self.hp = 0
                self.alive = False
                self.set_animation("dead")
           
        
    def is_hit_active(self) -> bool:
        return self.is_attacking and 1 <= self.frame_index <= 4

    def idle(self):
        self.set_animation("idle")

    def move_right(self):
        if self.can_move_right:
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

    def get_rect(self):
        return self.rect