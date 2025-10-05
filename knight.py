import pygame
import spritesheet

FW = 96
FH = 84
MAX_HP =100
START_X = 200
START_Y = 300# top left corner for now #TODO

class Knight(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # Load sprite sheets
        self.attack1_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 1.png").convert_alpha()
        self.death_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/DEATH.png").convert_alpha()
        self.idle_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/IDLE.png").convert_alpha()
        self.walk_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/WALK.png").convert_alpha()

        ss_attack = spritesheet.SpriteSheet(self.attack1_sheet)
        ss_hurt = spritesheet.SpriteSheet(self.death_sheet)
        ss_idle = spritesheet.SpriteSheet(self.idle_sheet)
        ss_walk = spritesheet.SpriteSheet(self.walk_sheet)

        def slice_all(ss, sheet):
            frames =[]
            count = sheet.get_width()//FW
            for i in range(count):
                frames.append(ss.get_image)

        # Current animation state
        self.current_sheet = self.walk_sheet
        self.position = (0, 0)
        
    def update(self):
        """Update knight state"""

        pass
    
    def draw(self, screen):
        """Draw knight on screen"""
        screen.blit(self.current_sheet, self.position)
    
    def set_animation(self, animation_type):
        """Change animation type"""
        animations = {
            'attack1': self.attack1_sheet,
            'attack2': self.attack2_sheet,
            'attack3': self.attack3_sheet,
            'death': self.death_sheet,
            'hurt': self.hurt_sheet,
            'idle': self.idle_sheet,
            'walk': self.walk_sheet
        }
        if animation_type in animations:
            self.current_sheet = animations[animation_type]

