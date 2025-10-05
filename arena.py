from dataclasses import dataclass

import pygame
import sys
from samurai import Samurai
from pygame.locals import *
from knight import Knight

# Import problem scene components
try:
    from game.ui.problem_panel import ProblemPanel
    from game.ui.snippet_board import SnippetBoard
    from game.problems.loader import random_problem
    from game.config import BG as PROBLEM_BG, FG as PROBLEM_FG, ACCENT as PROBLEM_ACCENT
except ImportError as e:
    print(f"Warning: Could not import problem scene components: {e}")
    ProblemPanel = None
    SnippetBoard = None
    random_problem = None

@dataclass
class PlayerInput:
    left:bool = False
    right:bool = False
    attack:bool = False

TIMER = 180000  # 3 minutes in milliseconds
PROBLEM_TIMER = 60000  # 60 seconds for problem solving in milliseconds

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
        
        # Problem scene state
        self.in_problem_scene = False
        self.problem_scene_active = False
        self.problem_timer_start = None
        self.problem_duration = PROBLEM_TIMER
        self.current_problem = None
        self.game_won = False
        
        # Setup problem scene components if available
        if ProblemPanel and SnippetBoard:
            # Fonts for problem scene
            problem_font = pygame.font.SysFont(None, 24)
            problem_big = pygame.font.SysFont(None, 36)
            problem_mono = pygame.font.SysFont("consolas", 18)
            
            # Layout for problem scene (adjust to fit arena screen)
            left_w = int(self.screen_width * 0.52)
            padding = 16
            right_rect = pygame.Rect(left_w + padding, 90, self.screen_width - left_w - padding * 2, self.screen_height - 120)
            left_rect = pygame.Rect(32, 90, left_w - padding * 2, self.screen_height - 120)
            
            self.problem_panel = ProblemPanel(right_rect, fonts=(problem_big, problem_font, problem_mono))
            self.snippet_board = SnippetBoard(left_rect, fonts=(problem_font, problem_big, problem_mono))
        else:
            self.problem_panel = None
            self.snippet_board = None
        
    def check_timer(self):
        if not self.game_over and not self.in_problem_scene:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            if elapsed_time >= self.game_duration:
                self.game_over = True
      
    def start_problem_scene(self):
        """Start the problem scene when knight dies"""
        if not random_problem or not self.problem_panel or not self.snippet_board:
            return
        
        self.in_problem_scene = True
        self.problem_scene_active = True
        self.problem_timer_start = pygame.time.get_ticks()
        
        # Load a random problem
        self.current_problem = random_problem()
        
        # Setup problem panel
        meta = {
            "id": self.current_problem.id,
            "slug": self.current_problem.slug,
            "title": self.current_problem.title,
            "difficulty": self.current_problem.difficulty,
            "tags": self.current_problem.tags,
            "url": self.current_problem.url,
            "text": self.current_problem.text,
        }
        self.problem_panel.set_meta(meta)
        
        # Setup snippet board with scrambled lines
        seed = int(self.current_problem.id)
        self.snippet_board.set_lines(self.current_problem.snippets, scramble=True, seed=seed)
    
    def check_problem_timer(self):
        """Check if problem timer has expired"""
        if self.problem_timer_start is None:
            return False
        
        elapsed = pygame.time.get_ticks() - self.problem_timer_start
        if elapsed >= self.problem_duration:
            return True
        return False
    
    def get_problem_remaining_time(self):
        """Get remaining time for problem in seconds"""
        if self.problem_timer_start is None:
            return self.problem_duration // 1000
        
        elapsed = pygame.time.get_ticks() - self.problem_timer_start
        remaining = max(0, self.problem_duration - elapsed)
        return remaining // 1000
    
    def end_problem_scene(self, success=False):
        """End the problem scene and return to arena"""
        self.in_problem_scene = False
        self.problem_scene_active = False
        self.problem_timer_start = None
        
        if success:
            # Player solved the problem - game won!
            self.game_won = True
            self.game_over = True
        else:
            # Timer expired - revive knight at half health
            self.knight.revive()
      
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
                if event.key == K_SPACE and not self.in_problem_scene:
                    p1_attack_once = True
                if event.key == K_w and not self.in_problem_scene:
                    p2_attack_once = True

            # Handle problem scene events
            if self.in_problem_scene and self.snippet_board and self.problem_panel:
                def submit_handler(_code_ignored: str):
                    # Check if solution is correct
                    submitted = [b.text for b in self.snippet_board.palette]
                    answer = self.current_problem.snippets
                    correct = 0
                    upto = min(len(answer), len(submitted))
                    for i in range(upto):
                        if submitted[i].strip() == answer[i].strip():
                            correct += 1
                    
                    # If all correct, player wins!
                    if correct == len(answer):
                        self.end_problem_scene(success=True)
                
                self.snippet_board.handle_event(
                    event,
                    on_submit=submit_handler,
                    on_reset=lambda: self.snippet_board.set_lines(
                        self.current_problem.snippets, scramble=True, seed=None
                    ),
                )
                self.problem_panel.handle_event(event)
                continue  # Don't process arena movement if in problem scene

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

            

        keys = pygame.key.get_pressed()
        
        # Only process movement if not in problem scene
        if not self.in_problem_scene:
            p1 = PlayerInput(
                left=keys[pygame.K_a],
                right=keys[pygame.K_d],
                attack=p1_attack_once
            )
            self.samurai.apply_input(p1)
    
    def update(self):
        if self.game_over or self.in_problem_scene:
            return
        
        self.check_timer()
        
        # Check if knight just died (transition to problem scene)
        if not self.knight.alive and not self.in_problem_scene:
            self.start_problem_scene()
            return
        
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
            
            if self.knight.is_hit_active() and not self.knight.attack_hit_applied:
                self.samurai.take_damage()
                self.knight.attack_hit_applied = True
            
        else:
            self.samurai.can_move_right=True
            self.knight.can_move_left=True
            self.samurai.can_take_damage= False
            self.knight.can_take_damage= False 
    
    def draw(self):
        # If in problem scene, draw problem UI instead of arena
        if self.in_problem_scene:
            self.draw_problem_scene()
            return
        
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
            
            if self.game_won:
                game_over_text = self.font.render("YOU WIN!", True, (0, 255, 0))
            else:
                game_over_text = self.font.render("TIME'S UP!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 120))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.update()
        pygame.display.flip()
    
    def draw_problem_scene(self):
        """Draw the problem scene UI"""
        if not self.problem_panel or not self.snippet_board:
            return
        
        # Check if timer expired
        if self.check_problem_timer():
            self.end_problem_scene(success=False)
            return
        
        # Fill background
        self.screen.fill(PROBLEM_BG if PROBLEM_BG else (18, 18, 20))
        
        # Draw title
        problem_big = pygame.font.SysFont(None, 36)
        problem_font = pygame.font.SysFont(None, 24)
        problem_small = pygame.font.SysFont(None, 20)
        
        title_surf = problem_big.render("Solve the Problem to Continue!", True, PROBLEM_FG if PROBLEM_FG else (230, 230, 235))
        self.screen.blit(title_surf, (16, 20))
        
        # Draw timer countdown
        remaining = self.get_problem_remaining_time()
        timer_color = (255, 120, 120) if remaining <= 10 else (PROBLEM_ACCENT if PROBLEM_ACCENT else (120, 180, 255))
        timer_surf = problem_big.render(f"Time: {remaining}s", True, timer_color)
        self.screen.blit(timer_surf, (16, 48))
        
        # Draw tags and URL if available
        if self.current_problem:
            y_offset = 48
            if self.current_problem.tags:
                tags_text = "Tags: " + ", ".join(self.current_problem.tags[:3])  # Limit to first 3 tags
                tags_surf = problem_small.render(tags_text, True, (170, 170, 180))
                self.screen.blit(tags_surf, (self.screen_width - tags_surf.get_width() - 16, y_offset))
            
            if self.current_problem.url:
                url_surf = problem_small.render(f"Problem URL: {self.current_problem.url[:50]}...", True, (170, 170, 180))
                self.screen.blit(url_surf, (self.screen_width - url_surf.get_width() - 16, y_offset + 22))
        
        # Draw problem panel and snippet board
        self.snippet_board.draw(self.screen)
        self.problem_panel.draw(self.screen)
        
        pygame.display.update()
        pygame.display.flip()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Get delta time in seconds
            
            self.handle_events()
            
            # Update problem scene if active
            if self.in_problem_scene and self.snippet_board:
                self.snippet_board.update(dt)
            
            # Update arena if not in problem scene and not game over
            if not self.game_over and not self.in_problem_scene:
                self.update()
            
            self.draw()


if __name__ == "__main__":
    Arena().run()