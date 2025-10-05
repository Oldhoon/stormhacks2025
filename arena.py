# from dataclasses import dataclass

# import pygame
# import sys
# from samurai import Samurai
# from pygame.locals import *
# from knight import Knight

# @dataclass
# class PlayerInput:
#     left:bool = False
#     right:bool = False
#     attack:bool = False

# TIMER = 180000  # 3 minutes in milliseconds 

# class Arena:
#     def __init__(self):
#         pygame.init()
        
#         self.screen_width = 1280
#         self.screen_height = 720
#         self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
#         pygame.display.set_caption("Leetcode Arena")
        
#         self.clock = pygame.time.Clock()
#         self.fps = 60
#         self.frames = self.fps / 10
        
#         self.background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
#         self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        
#         self.samurai = Samurai()
#         self.knight = Knight()
        
#         self.running = True
#         self.game_over = False
        
#         self.start_time = pygame.time.get_ticks()
#         self.game_duration = TIMER  # 3 minutes in milliseconds (3 * 60 * 1000)

#         self.font = pygame.font.Font(None, 74)
#         self.small_font = pygame.font.Font(None, 48)
        
#     def check_timer(self):
#         if not self.game_over:
#             elapsed_time = pygame.time.get_ticks() - self.start_time
#             if elapsed_time >= self.game_duration:
#                 self.game_over = True
      
#     def get_remaining_time(self):
#         elapsed_time = pygame.time.get_ticks() - self.start_time
#         remaining_time = max(0, self.game_duration - elapsed_time)
#         minutes = int(remaining_time / 60000)
#         seconds = int((remaining_time % 60000) / 1000)
#         return minutes, seconds
    
#     def handle_events(self):
        
#         p1_attack_once = False
        
#         for event in pygame.event.get():
#             if event.type == QUIT:
#                 self.running = False
#                 pygame.quit()
#                 sys.exit()
#             if event.type == KEYDOWN:
#                 if event.key == K_ESCAPE:
#                     self.running = False
#                     pygame.quit()
#                     sys.exit()
#                 if event.key == K_r and self.game_over:
#                     self.__init__()  # Restart the game
#                     return
#                 if event.key == K_SPACE:
#                     p1_attack_once = True
#                 if event.key == K_w:
#                     p2_attack_once = True

#             if self.game_over:
#                 return  # Don't process movement if game is over

            

#         keys = pygame.key.get_pressed()
#         p1 = PlayerInput(
#             left=keys[pygame.K_a],
#             right=keys[pygame.K_d],
#             attack=p1_attack_once
#         )
#         self.samurai.apply_input(p1)
    
#     def update(self):
#         if self.game_over:
#             return
#         self.check_timer()
#         # set movement and damage flags first 
#         self.check_collision()
#         self.check_screen_collision()
        
#         # then update each character
#         self.knight.ai_update(self.samurai)

#         self.knight.update()
#         self.samurai.update()
        

#     def check_screen_collision(self):
#         samurai_rect = self.samurai.get_rect()
#         if samurai_rect.x <= -400:
#             self.samurai.can_move_left = False
#         else:
#             self.samurai.can_move_left = True
#         knight_rect = self.knight.get_rect()
#         if knight_rect.x >= self.screen_width - 150:
#             self.knight.can_move_right = False
#         else:
#             self.knight.can_move_right = True

#     def check_collision(self):
#         if self.knight.get_rect().colliderect(self.samurai.get_rect()):
#             # lock movement into each other 
#             self.samurai.can_move_right=False
#             self.knight.can_move_left=False
#             # allow damage while in contact 
#             self.samurai.can_take_damage= True
#             self.knight.can_take_damage= True
            
#             if self.samurai.is_hit_active() and not self.samurai.attack_hit_applied:
#                 self.knight.take_damage()
#                 self.samurai.attack_hit_applied = True
            
#         else:
#             self.samurai.can_move_right=True
#             self.knight.can_move_left=True
#             self.samurai.can_take_damage= False
#             self.knight.can_take_damage= False 
    
#     def draw(self):
#         self.screen.blit(self.background, (0, 0))
        
#         self.knight.draw(self.screen)
#         self.samurai.draw(self.screen)
        
        
#                # Draw timer
#         minutes, seconds = self.get_remaining_time()
#         timer_text = self.small_font.render(f"{minutes}:{seconds:02d}", True, (255, 255, 255))
#         timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 50))
#         self.screen.blit(timer_text, timer_rect)

#         # Draw game over screen
#         if self.game_over:
#             overlay = pygame.Surface((self.screen_width, self.screen_height))
#             overlay.set_alpha(128)
#             overlay.fill((0, 0, 0))
#             self.screen.blit(overlay, (0, 0))
            
#             game_over_text = self.font.render("TIME'S UP!", True, (255, 0, 0))
#             text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
#             self.screen.blit(game_over_text, text_rect)
            
#             restart_text = self.small_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
#             restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
#             self.screen.blit(restart_text, restart_rect)

#         pygame.display.update()
#         pygame.display.flip()
    
#     def run(self):
#         while self.running:
#             self.handle_events()
#             if not self.game_over:
#                 self.update()
#             self.draw()
#             self.clock.tick(self.fps)


# Arena().run()
from dataclasses import dataclass

import pygame
from pygame.locals import *

from samurai import Samurai
from knight import Knight
from game.leetcode_app import LeetCodeGame


@dataclass
class PlayerInput:
    left: bool = False
    right: bool = False
    attack: bool = False


TIMER = 180_000  # 3 minutes
LEETCODE_TIME_LIMIT = 180  # seconds
PLAYER_MAX_LIVES = 5

class Arena:
    def __init__(self):
        pygame.init()

        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Leetcode Arena")

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.background = pygame.image.load(
            r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png"
        ).convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 48)

        self.game_duration = TIMER
        self._reset_state()

    # ------------------------------------------------------------------ state ------------------------------------------------------------------
    def _reset_state(self):
        self.samurai = Samurai()
        self.knight = Knight()

        self.running = True
        self.state = "battle"  # battle | challenge | victory | defeat
        self.challenge: LeetCodeGame | None = None

        self.start_time = pygame.time.get_ticks()
        self.pause_accumulated = 0
        self.pause_started_at = None

        self.game_over = False
        self.game_over_reason: str | None = None
        self.victory = False
        self.quit_requested = False

        self.info_message = None
        self.info_until_ms = 0

        self.level = 1
        self.knights_defeated = 0
        self.score = 0

        self.max_lives = PLAYER_MAX_LIVES
        self.player_lives = self.max_lives
        self.pending_knight_attack = False
        self._apply_level_scaling()

    def _apply_level_scaling(self):
        speed_bonus = min(max(0, self.level - 1), 4)
        self.knight.speed = max(1, 1 + speed_bonus)

    def _set_info(self, message: str, duration_ms: int = 2000):
        self.info_message = message
        self.info_until_ms = pygame.time.get_ticks() + duration_ms

    # ---------------------------------------------------------------- timer ------------------------------------------------------------------
    def check_timer(self):
        if self.state != "battle" or self.game_over:
            return
        elapsed_time = pygame.time.get_ticks() - self.start_time - self.pause_accumulated
        if elapsed_time >= self.game_duration:
            self.game_over = True
            self.game_over_reason = "timeout"
            self.state = "defeat"
            self._set_info("Time expired. Samurai defeated.", 3500)

    def get_remaining_time(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time - self.pause_accumulated
        remaining_time = max(0, self.game_duration - elapsed_time)
        minutes = int(remaining_time / 60000)
        seconds = int((remaining_time % 60000) / 1000)
        return minutes, seconds

    # ---------------------------------------------------------------- events ------------------------------------------------------------------
    def handle_events(self):
        p1_attack_once = False

        for event in pygame.event.get():
            if self.state == "challenge" and self.challenge:
                self.challenge.process_event(event)

            if event.type == QUIT:
                self.running = False
                self.quit_requested = True
                continue

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    self.quit_requested = True
                    continue
                if event.key == K_r and (self.game_over or self.victory):
                    self._reset_state()
                    continue
                if self.state == "battle" and not self.game_over:
                    if event.key == K_SPACE:
                        p1_attack_once = True

        if self.state == "battle" and not self.game_over:
            keys = pygame.key.get_pressed()
            p1 = PlayerInput(
                left=keys[pygame.K_a],
                right=keys[pygame.K_d],
                attack=p1_attack_once,
            )
            self.samurai.apply_input(p1)

    # ---------------------------------------------------------------- battle logic -------------------------------------------------------------
    def _update_battle(self):
        if self.game_over:
            return

        self.check_timer()

        if self.info_message and pygame.time.get_ticks() >= self.info_until_ms:
            self.info_message = None

        if self.pending_knight_attack:
            self._execute_pending_knight_attack()

        self.check_collision()
        self.check_screen_collision()

        self.knight.ai_update(self.samurai)
        self.knight.update()
        self.samurai.update()

        if not self.knight.alive and self.challenge is None and not self.victory and not self.game_over:
            self._start_challenge()

    def _execute_pending_knight_attack(self):
        sx, sy = self.samurai.position
        attack_x = min(self.screen_width - 220, max(sx + 140, 260))
        self.knight.position = (attack_x, self.knight.position[1])
        self.knight.rect.midleft = self.knight.position
        self.knight.attack()
        self.pending_knight_attack = False

    def _start_challenge(self):
        self.state = "challenge"
        self.challenge = LeetCodeGame(self.screen, strict_mode=True, time_limit_sec=LEETCODE_TIME_LIMIT)
        self.pause_started_at = pygame.time.get_ticks()

    def _finish_challenge(self):
        if not self.challenge:
            return

        result = self.challenge.get_result()
        reason = self.challenge.get_failure_reason()

        if result == "quit":
            self.running = False
            self.quit_requested = True
        else:
            now = pygame.time.get_ticks()
            if self.pause_started_at is not None:
                self.pause_accumulated += max(0, now - self.pause_started_at)
            self.pause_started_at = None

            if result == "success":
                self.knights_defeated += 1
                self.score += 100
                healed_note = ""
                if self.player_lives < self.max_lives:
                    self.player_lives += 1
                    healed_note = " | Life +1"
                self.level += 1
                self._set_info(f"Knight defeated! Level {self.level} incoming. Score: {self.score}{healed_note}", 3200)
                self.samurai = Samurai()
                self.knight = Knight()
                self._apply_level_scaling()
                self.pending_knight_attack = False
                self.state = "battle"
            else:
                if reason == "timeout":
                    self._set_info("Out of time! The knight strikes again.", 2500)
                else:
                    self._set_info("Incorrect order! The knight returns.", 2500)
                self.samurai = Samurai()
                self.knight = Knight()
                self._apply_level_scaling()
                self.pending_knight_attack = True
                self.state = "battle"
        self.challenge = None

    # ---------------------------------------------------------------- collisions ---------------------------------------------------------------
    def check_screen_collision(self):
        samurai_rect = self.samurai.get_rect()
        self.samurai.can_move_left = samurai_rect.x > -400

        knight_rect = self.knight.get_rect()
        self.knight.can_move_right = knight_rect.x < self.screen_width - 150

    def _on_knight_attack(self):
        self.knight.attack_hit_applied = True
        self.samurai.take_damage()
        if self.player_lives > 0:
            self.player_lives -= 1
        if self.player_lives <= 0:
            self.player_lives = 0
            self.game_over = True
            self.game_over_reason = "defeat"
            self.state = "defeat"
            self._set_info("Samurai has fallen...", 3500)
        else:
            self._set_info(f"Knight hit! Lives remaining: {self.player_lives}", 1800)

    def check_collision(self):
        if self.knight.get_rect().colliderect(self.samurai.get_rect()):
            self.samurai.can_move_right = False
            self.knight.can_move_left = False
            self.samurai.can_take_damage = True
            self.knight.can_take_damage = True

            if self.samurai.is_hit_active() and not self.samurai.attack_hit_applied:
                self.knight.take_damage()
                self.samurai.attack_hit_applied = True

            if self.knight.is_hit_active() and not self.knight.attack_hit_applied:
                self._on_knight_attack()
        else:
            self.samurai.can_move_right = True
            self.knight.can_move_left = True
            self.samurai.can_take_damage = False
            self.knight.can_take_damage = False

    # ---------------------------------------------------------------- rendering ---------------------------------------------------------------
    def _draw_timer(self):
        minutes, seconds = self.get_remaining_time()
        timer_text = self.small_font.render(f"{minutes}:{seconds:02d}", True, (255, 255, 255))
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(timer_text, timer_rect)

    def _draw_scoreboard(self):
        level_surf = self.small_font.render(f"Level {self.level}", True, (235, 235, 240))
        score_surf = self.small_font.render(f"Score {self.score}", True, (235, 235, 240))
        knights_surf = self.small_font.render(f"Knights {self.knights_defeated}", True, (180, 180, 190))

        padding = 20
        x = self.screen_width - padding
        self.screen.blit(score_surf, (x - score_surf.get_width(), 70))
        self.screen.blit(level_surf, (x - level_surf.get_width(), 40))
        self.screen.blit(knights_surf, (x - knights_surf.get_width(), 100))

    def _draw_lifebars(self):
        label = self.small_font.render("Lives", True, (240, 240, 240))
        self.screen.blit(label, (40, 24))
        bar_w = 46
        bar_h = 18
        spacing = 14
        base_x = 40
        base_y = 60
        for i in range(self.max_lives):
            rect = pygame.Rect(base_x + i * (bar_w + spacing), base_y, bar_w, bar_h)
            color = (220, 70, 70) if i < self.player_lives else (70, 70, 80)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, (20, 20, 25), rect, width=2, border_radius=6)

    def _draw_overlay(self, title: str, subtitle: str):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_text = self.font.render(title, True, (255, 255, 255))
        sub_text = self.small_font.render(subtitle, True, (200, 200, 200))

        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        sub_rect = sub_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(sub_text, sub_rect)

    def _draw_info_message(self):
        if not self.info_message or pygame.time.get_ticks() >= self.info_until_ms:
            return
        msg = self.small_font.render(self.info_message, True, (255, 255, 255))
        pad = 16
        box = pygame.Surface((msg.get_width() + pad * 2, msg.get_height() + pad), pygame.SRCALPHA)
        box.fill((0, 0, 0, 170))
        box.blit(msg, (pad, pad // 2))
        box_rect = box.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        self.screen.blit(box, box_rect)

    def _game_over_text(self):
        if self.game_over_reason == "defeat":
            return "Samurai Down!", "Press R to restart or ESC to quit"
        return "TIME'S UP!", "Press R to restart or ESC to quit"

    def draw(self):
        if self.state == "challenge" and self.challenge:
            self.challenge.draw()
            self._draw_scoreboard()
        else:
            self.screen.blit(self.background, (0, 0))
            self.knight.draw(self.screen)
            self.samurai.draw(self.screen)
            self._draw_timer()
            self._draw_lifebars()
            self._draw_scoreboard()
            self._draw_info_message()

            if self.victory:
                self._draw_overlay("Victory!", "Press R to restart or ESC to quit")
            elif self.game_over:
                title, subtitle = self._game_over_text()
                self._draw_overlay(title, subtitle)

        pygame.display.flip()

    # ---------------------------------------------------------------- main loop ---------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.handle_events()

            if self.state == "challenge" and self.challenge:
                self.challenge.update(dt)
                if self.challenge.is_finished():
                    self._finish_challenge()
            elif self.state == "battle":
                self._update_battle()
            elif self.state in {"victory", "defeat"}:
                if self.info_message and pygame.time.get_ticks() >= self.info_until_ms:
                    self.info_message = None

            self.draw()

        pygame.quit()

        if self.quit_requested:
            return "quit"
        if self.victory:
            return "victory"
        if self.game_over_reason == "timeout":
            return "timeout"
        if self.game_over_reason == "defeat":
            return "defeat"
        return "stopped"


if __name__ == "__main__":
    Arena().run()
