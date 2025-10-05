from dataclasses import dataclass

import pygame
import sys
from samurai import Samurai
from pygame.locals import *
from knight import Knight

# Import game modules for LeetCode problem UI
try:
    from game.ui.problem_panel import ProblemPanel
    from game.ui.snippet_board import SnippetBoard
    from game.problems.loader import random_problem
    from game.main import _meta_from_problem, show_problem, grade_submission
except ImportError as e:
    print(f"Warning: Could not import game modules: {e}")
    ProblemPanel = None
    SnippetBoard = None

@dataclass
class PlayerInput:
    left:bool = False
    right:bool = False
    attack:bool = False

TIMER = 180000  # 3 minutes in milliseconds 
PROBLEM_TIMER = 60000  # 60 seconds for solving LeetCode problem

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
        
        # LeetCode problem state
        self.problem_mode = False  # True when showing LeetCode problem
        self.problem_start_time = None
        self.current_problem = None
        self.problem_panel = None
        self.snippet_board = None
        self.victory = False
        
        # Initialize LeetCode UI components if available
        if ProblemPanel is not None and SnippetBoard is not None:
            # Create fonts for problem UI
            ui_font = pygame.font.SysFont(None, 24)
            ui_big = pygame.font.SysFont(None, 36)
            ui_mono = pygame.font.SysFont("consolas", 18)
            
            # Create UI components with appropriate layout
            right_rect = pygame.Rect(self.screen_width // 2 + 20, 80, 
                                    self.screen_width // 2 - 40, self.screen_height - 140)
            left_rect = pygame.Rect(20, 80, 
                                   self.screen_width // 2 - 40, self.screen_height - 140)
            
            self.problem_panel = ProblemPanel(right_rect, fonts=(ui_big, ui_font, ui_mono))
            self.snippet_board = SnippetBoard(left_rect, fonts=(ui_font, ui_big, ui_mono))
        
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
    
    def get_problem_remaining_time(self):
        """Get remaining time for solving the LeetCode problem."""
        if self.problem_start_time is None:
            return 60
        elapsed_time = pygame.time.get_ticks() - self.problem_start_time
        remaining_time = max(0, PROBLEM_TIMER - elapsed_time)
        seconds = int(remaining_time / 1000)
        return seconds
    
    def start_problem_mode(self):
        """Trigger LeetCode problem mode when knight dies."""
        if self.problem_panel is None or self.snippet_board is None:
            # If UI components not available, just end the game
            self.game_over = True
            self.victory = True
            return
            
        self.problem_mode = True
        self.problem_start_time = pygame.time.get_ticks()
        
        # Load a random problem
        self.current_problem = random_problem()
        if self.current_problem:
            show_problem(self.problem_panel, self.snippet_board, 
                        self.current_problem, deterministic_seed=False)
    
    def end_problem_mode_victory(self):
        """Called when player solves the problem in time."""
        self.problem_mode = False
        self.game_over = True
        self.victory = True
    
    def end_problem_mode_timeout(self):
        """Called when time runs out - return to arena and revive knight."""
        self.problem_mode = False
        self.problem_start_time = None
        self.current_problem = None
        # Revive the knight
        self.knight.revive()
    
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
                if event.key == K_SPACE and not self.problem_mode:
                    p1_attack_once = True
                if event.key == K_w:
                    p2_attack_once = True

            if self.game_over:
                return  # Don't process movement if game is over
            
            # Handle problem mode events
            if self.problem_mode:
                if self.snippet_board and self.problem_panel:
                    def submit_handler(_code_ignored: str):
                        submitted = [b.text for b in self.snippet_board.palette]
                        got, total = grade_submission(self.current_problem, submitted)
                        # Check if solution is correct (all lines match)
                        if got == total:
                            self.end_problem_mode_victory()
                        # If not correct, player can keep trying until time runs out
                    
                    self.snippet_board.handle_event(
                        event,
                        on_submit=submit_handler,
                        on_reset=lambda: self.snippet_board.set_lines(
                            self.current_problem.snippets, scramble=True, seed=None
                        ),
                    )
                    self.problem_panel.handle_event(event)
                continue  # Don't process arena movement in problem mode

            

        if not self.problem_mode:
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
        
        # In problem mode, check for timeout
        if self.problem_mode:
            if self.get_problem_remaining_time() <= 0:
                self.end_problem_mode_timeout()
            # Update snippet board animation
            if self.snippet_board:
                self.snippet_board.update(1/60.0)
            return
        
        self.check_timer()
        # set movement and damage flags first 
        self.check_collision()
        self.check_screen_collision()
        
        # Check if knight just died to trigger problem mode
        knight_was_alive = self.knight.alive
        
        # then update each character
        self.knight.ai_update(self.samurai)

        self.knight.update()
        self.samurai.update()
        
        # Trigger problem mode when knight dies
        if knight_was_alive and not self.knight.alive:
            self.start_problem_mode()
        

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
        
        # Draw problem mode UI overlay
        if self.problem_mode:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(200)
            overlay.fill((10, 10, 15))
            self.screen.blit(overlay, (0, 0))
            
            # Draw problem title
            title_text = self.font.render("LeetCode Challenge!", True, (120, 180, 255))
            title_rect = title_text.get_rect(center=(self.screen_width // 2, 30))
            self.screen.blit(title_text, title_rect)
            
            # Draw problem timer
            remaining = self.get_problem_remaining_time()
            timer_color = (255, 100, 100) if remaining <= 10 else (255, 255, 255)
            timer_text = self.small_font.render(f"Time: {remaining}s", True, timer_color)
            timer_rect = timer_text.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
            self.screen.blit(timer_text, timer_rect)
            
            # Draw problem UI components
            if self.snippet_board:
                self.snippet_board.draw(self.screen)
            if self.problem_panel:
                self.problem_panel.draw(self.screen)
        else:
            # Draw normal arena timer
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
            
            if self.victory:
                game_over_text = self.font.render("VICTORY!", True, (0, 255, 100))
                text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(game_over_text, text_rect)
                
                victory_msg = self.small_font.render("You defeated the Knight!", True, (255, 255, 255))
                msg_rect = victory_msg.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
                self.screen.blit(victory_msg, msg_rect)
            else:
                game_over_text = self.font.render("TIME'S UP!", True, (255, 0, 0))
                text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 120))
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