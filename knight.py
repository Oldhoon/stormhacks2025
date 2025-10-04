import pygame
import sys
from pygame.locals import *

class Knight:

    def __init__(self):
        # Load sprite sheets
        self.attack1_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 1.png").convert_alpha()
        self.attack2_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 2.png").convert_alpha()
        self.attack3_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/ATTACK 3.png").convert_alpha()
        self.death_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/DEATH.png").convert_alpha()
        self.hurt_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/HURT.png").convert_alpha()
        self.idle_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/IDLE.png").convert_alpha()
        self.walk_sheet = pygame.image.load(r"assets/Knight 2D Pixel Art/Sprites/without_outline/WALK.png").convert_alpha()
        
        # Current animation state
        self.current_sheet = self.walk_sheet
        self.position = (0, 0)
        
    def update(self):
        """Update knight state"""
        # TODO: Add animation frame logic
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