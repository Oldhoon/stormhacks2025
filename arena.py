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

TIMER = 180000  # 3 minutes in milliseconds 

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
        self.game_over = False
        
        self.start_time = pygame.time.get_ticks()
        self.game_duration = TIMER  # 3 minutes in milliseconds (3 * 60 * 1000)

        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 48)
        
    def check_timer(self):
        if not self.game_over:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            if elapsed_time >= self.game_duration:
                self.game_over = True
      
    def get_remaining_time(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        remaining_time = max(0, self.game_duration - elapsed_time)
        minutes = int(remaining_time / 60000)
        seconds = int((remaining_time % 60000) / 1000)
        return minutes, seconds
    
    def handle_events(self):
        
        p1_attack_once = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if event.key == K_r and self.game_over:
                    self.__init__()  # Restart the game
                    return
                if event.key == K_SPACE:
                    p1_attack_once = True
                if event.key == K_w:
                    p2_attack_once = True

            if self.game_over:
                return  # Don't process movement if game is over

            

        keys = pygame.key.get_pressed()
        p1 = PlayerInput(
            left=keys[pygame.K_a],
            right=keys[pygame.K_d],
            attack=p1_attack_once
        )
        self.samurai.apply_input(p1)
    
    def update(self):
        if self.game_over:
            return
        self.check_timer()
        # set movement and damage flags first 
        self.check_collision()
        self.check_screen_collision()
        
        # then update each character
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
            # lock movement into each other 
            self.samurai.can_move_right=False
            self.knight.can_move_left=False
            # allow damage while in contact 
            self.samurai.can_take_damage= True
            self.knight.can_take_damage= True
            
            if self.samurai.is_hit_active() and not self.samurai.attack_hit_applied:
                self.knight.take_damage()
                self.samurai.attack_hit_applied = True
            
        else:
            self.samurai.can_move_right=True
            self.knight.can_move_left=True
            self.samurai.can_take_damage= False
            self.knight.can_take_damage= False 
    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        
        self.knight.draw(self.screen)
        self.samurai.draw(self.screen)
        
        
               # Draw timer
        minutes, seconds = self.get_remaining_time()
        timer_text = self.small_font.render(f"{minutes}:{seconds:02d}", True, (255, 255, 255))
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(timer_text, timer_rect)

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("TIME'S UP!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.update()
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            if not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(self.fps)


Arena().run()