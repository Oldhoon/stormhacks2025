import pygame
import sys
from samurai import Samurai
from pygame.locals import *
from knight import Knight

class Arena:
    def __init__(self):
        pygame.init()
        
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Leetcode Arena")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.frames = self.fps / 12
        
        self.background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        
        # self.knight = Knight()
        self.samurai = Samurai()
        
        self.running = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
    
    def update(self):
        # self.knight.update()
        self.samurai.update()

    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        
        # self.knight.draw(self.screen)
        self.samurai.draw(self.screen)
        
        pygame.display.update()
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)


Arena().run()