from dataclasses import dataclass

import pygame
import sys
from samurai import Samurai
from pygame.locals import *
from knight import Knight

@dataclass
class PlayerInput:
    left:bool = False
    right:bool = False
    attack:bool = False


class Arena:
    def __init__(self):
        pygame.init()
        
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Leetcode Arena")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.frames = self.fps / 10
        
        self.background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        
        self.samurai = Samurai()
        self.knight = Knight()
        
        self.running = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        p1 = PlayerInput(
            left=keys[pygame.K_LEFT],
            right=keys[pygame.K_RIGHT],
            attack=keys[pygame.K_SPACE]
        )
        p2 = PlayerInput(
            left=keys[pygame.K_a],
            right=keys[pygame.K_d],
            attack=keys[pygame.K_w]
        )
        self.samurai.apply_input(p1)
        self.knight.apply_input(p2)
    
    def update(self):
        self.knight.ai_update(self.samurai)
        self.knight.update()
        self.samurai.update()

    def check_screen_collision(self):
        samurai_rect = self.samurai.get_rect()
        if samurai_rect.x <= -400:
            self.samurai.can_move_left = False
        else:
            self.samurai.can_move_left = True
        knight_rect = self.knight.get_rect()
        if knight_rect.x >= self.screen_width - 150:
            self.knight.can_move_right = False
        else:
            self.knight.can_move_right = True

    def check_collision(self):
        if self.knight.get_rect().colliderect(self.samurai.get_rect()):
            self.samurai.can_move_right=False
            self.knight.can_move_left=False
        else:
            self.samurai.can_move_right=True
            self.knight.can_move_left=True
    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        
        self.knight.draw(self.screen)
        self.samurai.draw(self.screen)
        
        pygame.display.update()
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
            self.check_collision()
            self.check_screen_collision()


Arena().run()