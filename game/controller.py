# game/controller.py
"""
GameController: Manages state transitions between Arena and LeetCode screens.
"""
import pygame
import sys
from typing import Callable, Optional

try:
    from .config import WIDTH, HEIGHT, BG, FG, ACCENT
    from .ui.problem_panel import ProblemPanel
    from .ui.snippet_board import SnippetBoard
    from .problems.loader import random_problem
    from .api import LCClient
except ImportError:
    from config import WIDTH, HEIGHT, BG, FG, ACCENT
    from ui.problem_panel import ProblemPanel
    from ui.snippet_board import SnippetBoard
    from problems.loader import random_problem
    from api import LCClient


class GameController:
    """
    Top-level controller managing Arena and LeetCode screens.
    States: ARENA, LC, ENDED
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.state = "ARENA"
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Create arena screen (doesn't import arena.py to avoid auto-run)
        self.arena_screen = ArenaScreen(self.screen, on_knight_dead=self.start_leetcode)
        self.lc_screen = None
        self.ended_victory = False
        
    def start_arena(self):
        """Start or resume the Arena screen."""
        print("resume arena")
        self.state = "ARENA"
        self.lc_screen = None
        
    def start_leetcode(self):
        """Transition to LeetCode screen when Knight dies."""
        print("switch to LC")
        self.state = "LC"
        self.lc_screen = LCScreen(
            self.screen,
            on_victory=lambda: self.end_game(victory=True),
            on_timeout=self._on_lc_timeout
        )
        
    def _on_lc_timeout(self):
        """Called when LC timer expires - revive knight and return to arena."""
        self.arena_screen.revive_knight()
        self.start_arena()
        
    def end_game(self, victory=False):
        """End the game and show victory/defeat overlay."""
        print("victory" if victory else "game over")
        self.state = "ENDED"
        self.ended_victory = victory
        
    def handle_events(self):
        """Delegate event handling to active screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.state == "ENDED":
                    # Restart game
                    self.__init__(self.screen)
                    return True
        
        # Delegate to active screen
        if self.state == "ARENA":
            return self.arena_screen.handle_events()
        elif self.state == "LC":
            return self.lc_screen.handle_events()
        
        return True
        
    def update(self, dt):
        """Update active screen."""
        if self.state == "ARENA":
            self.arena_screen.update(dt)
        elif self.state == "LC":
            self.lc_screen.update(dt)
            
    def draw(self):
        """Draw active screen."""
        if self.state == "ARENA":
            self.arena_screen.draw()
        elif self.state == "LC":
            self.lc_screen.draw()
        elif self.state == "ENDED":
            self._draw_ended()
            
    def _draw_ended(self):
        """Draw game over overlay."""
        # Draw last screen state underneath
        if hasattr(self, 'arena_screen'):
            self.arena_screen.draw()
        
        # Overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Message
        font = pygame.font.Font(None, 74)
        small_font = pygame.font.Font(None, 48)
        
        if self.ended_victory:
            text = font.render("VICTORY!", True, (0, 255, 0))
        else:
            text = font.render("GAME OVER", True, (255, 0, 0))
            
        rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, rect)
        
        # Instructions
        hint = small_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
        hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 80))
        self.screen.blit(hint, hint_rect)
        
        pygame.display.flip()
        
    def run(self):
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            running = self.handle_events()
            if not running:
                break
                
            self.update(dt)
            self.draw()
            
        pygame.quit()


class ArenaScreen:
    """
    Wrapper around Arena to provide screen interface and knight-death callback.
    """
    
    def __init__(self, screen, on_knight_dead: Callable[[], None]):
        self.screen = screen
        self.on_knight_dead = on_knight_dead
        self._knight_dead_fired = False
        
        # Import and instantiate Arena
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from arena import Arena
        from samurai import Samurai
        from knight import Knight
        
        # Initialize arena components directly
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Load background
        self.background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        
        # Create characters
        self.samurai = Samurai()
        self.knight = Knight()
        
        # Timer
        self.start_time = pygame.time.get_ticks()
        self.game_duration = 180000  # 3 minutes
        self.game_over = False
        
        # Fonts
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 48)
        
        # Input state
        from arena import PlayerInput
        self.PlayerInput = PlayerInput
        
    def revive_knight(self):
        """Revive the knight at half HP and reset flags."""
        self.knight.revive()
        self._knight_dead_fired = False
        
    def handle_events(self):
        """Handle arena-specific events."""
        from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_r, K_SPACE, K_w
        
        p1_attack_once = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                if event.key == K_r and self.game_over:
                    self.__init__(self.screen, self.on_knight_dead)
                    return True
                if event.key == K_SPACE:
                    p1_attack_once = True
                    
        if self.game_over:
            return True
            
        # Process movement
        keys = pygame.key.get_pressed()
        p1 = self.PlayerInput(
            left=keys[pygame.K_a],
            right=keys[pygame.K_d],
            attack=p1_attack_once
        )
        self.samurai.apply_input(p1)
        
        return True
        
    def update(self, dt):
        """Update arena state."""
        if self.game_over:
            return
            
        # Check timer
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time >= self.game_duration:
            self.game_over = True
            return
            
        # Check collision and update characters
        self._check_collision()
        self._check_screen_collision()
        
        self.knight.ai_update(self.samurai)
        self.knight.update()
        self.samurai.update()
        
        # Check if knight just died
        if not self.knight.alive and not self._knight_dead_fired:
            self._knight_dead_fired = True
            self.on_knight_dead()
            
    def _check_collision(self):
        """Check collision between samurai and knight."""
        if self.knight.get_rect().colliderect(self.samurai.get_rect()):
            self.samurai.can_move_right = False
            self.knight.can_move_left = False
            self.samurai.can_take_damage = True
            self.knight.can_take_damage = True
            
            if self.samurai.is_hit_active() and not self.samurai.attack_hit_applied:
                self.knight.take_damage()
                self.samurai.attack_hit_applied = True
                
            if self.knight.is_hit_active() and not self.knight.attack_hit_applied:
                self.samurai.take_damage()
                self.knight.attack_hit_applied = True
        else:
            self.samurai.can_move_right = True
            self.knight.can_move_left = True
            self.samurai.can_take_damage = False
            self.knight.can_take_damage = False
            
    def _check_screen_collision(self):
        """Check screen boundaries."""
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
            
    def draw(self):
        """Draw arena."""
        self.screen.blit(self.background, (0, 0))
        
        self.knight.draw(self.screen)
        self.samurai.draw(self.screen)
        
        # Draw timer
        elapsed_time = pygame.time.get_ticks() - self.start_time
        remaining_time = max(0, self.game_duration - elapsed_time)
        minutes = int(remaining_time / 60000)
        seconds = int((remaining_time % 60000) / 1000)
        timer_text = self.small_font.render(f"{minutes}:{seconds:02d}", True, (255, 255, 255))
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(timer_text, timer_rect)
        
        # Draw game over if applicable
        if self.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            text = self.font.render("TIME'S UP!", True, (255, 0, 0))
            rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text, rect)
            
            hint = self.small_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
            hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 120))
            self.screen.blit(hint, hint_rect)
            
        pygame.display.flip()


class LCScreen:
    """
    LeetCode problem screen with timer, submission handling, and victory/timeout callbacks.
    """
    
    def __init__(self, screen, on_victory: Callable[[], None], on_timeout: Callable[[], None]):
        self.screen = screen
        self.on_victory = on_victory
        self.on_timeout = on_timeout
        
        # Timer setup
        self.start_time = pygame.time.get_ticks()
        self.duration = 120000  # 120 seconds in milliseconds
        
        # Fonts
        self.font = pygame.font.SysFont(None, 24)
        self.big = pygame.font.SysFont(None, 36)
        self.mono = pygame.font.SysFont("consolas", 18)
        
        # Layout
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        left_w = int(screen_width * 0.52)
        padding = 16
        
        right_rect = pygame.Rect(left_w + padding, 90, screen_width - left_w - padding * 2, screen_height - 120)
        left_rect = pygame.Rect(32, 90, left_w - padding * 2, screen_height - 120)
        
        # UI components
        self.problem_panel = ProblemPanel(right_rect, fonts=(self.big, self.font, self.mono))
        self.snippet_board = SnippetBoard(left_rect, fonts=(self.font, self.big, self.mono))
        
        # Load problem
        self.current_problem = None
        self.error_message = None
        self._load_problem()
        
    def _load_problem(self):
        """Load problem from API or fallback to YAML bank."""
        # Try API first
        try:
            client = LCClient(timeout=3)
            meta = client.problem_meta("two-sum")
            
            # Convert API meta to Problem-like object for UI
            class APIProblem:
                def __init__(self, m):
                    self.id = str(m.get("id", "1"))
                    self.slug = m.get("slug", "two-sum")
                    self.title = m.get("title", "Unknown")
                    self.difficulty = m.get("difficulty", "Easy")
                    self.tags = m.get("tags", [])
                    self.url = m.get("url", "")
                    self.text = m.get("text", "")
                    # For API problems without snippets, use a placeholder
                    self.snippets = [
                        "def twoSum(self, nums, target):",
                        "    seen = {}",
                        "    for i, num in enumerate(nums):",
                        "        if target - num in seen:",
                        "            return [seen[target - num], i]",
                        "        seen[num] = i",
                    ]
            
            self.current_problem = APIProblem(meta)
            print(f"Loaded problem from API: {self.current_problem.title}")
            
        except Exception as e:
            print(f"API failed ({e}), falling back to YAML bank")
            # Fallback to YAML bank
            try:
                self.current_problem = random_problem()
                print(f"Loaded problem from bank: {self.current_problem.title}")
            except Exception as e2:
                print(f"Failed to load from bank: {e2}")
                self.error_message = "Failed to load problem"
                return
        
        # Setup UI
        if self.current_problem:
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
            seed = int(self.current_problem.id) if self.current_problem.id.isdigit() else None
            self.snippet_board.set_lines(self.current_problem.snippets, scramble=True, seed=seed)
            
    def get_remaining_seconds(self):
        """Get remaining time in seconds."""
        elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, self.duration - elapsed)
        return remaining // 1000
        
    def handle_events(self):
        """Handle LC screen events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
            # Handle snippet board events
            if self.snippet_board and self.current_problem:
                def submit_handler(_code_ignored: str):
                    """Check if solution is correct."""
                    submitted = [b.text for b in self.snippet_board.palette]
                    answer = self.current_problem.snippets
                    correct = 0
                    upto = min(len(answer), len(submitted))
                    for i in range(upto):
                        if submitted[i].strip() == answer[i].strip():
                            correct += 1
                    
                    # If all correct, victory!
                    if correct == len(answer):
                        self.on_victory()
                        
                self.snippet_board.handle_event(
                    event,
                    on_submit=submit_handler,
                    on_reset=lambda: self.snippet_board.set_lines(
                        self.current_problem.snippets, scramble=True, seed=None
                    ),
                )
                
            if self.problem_panel:
                self.problem_panel.handle_event(event)
                
        return True
        
    def update(self, dt):
        """Update LC screen state."""
        # Check timer
        if self.get_remaining_seconds() <= 0:
            self.on_timeout()
            
        # Update snippet board animations
        if self.snippet_board:
            self.snippet_board.update(dt)
            
    def draw(self):
        """Draw LC screen."""
        # Background
        self.screen.fill(BG if BG else (18, 18, 20))
        
        # Title
        title_surf = self.big.render("Solve the LeetCode Problem!", True, FG if FG else (230, 230, 235))
        self.screen.blit(title_surf, (16, 20))
        
        # Timer
        remaining = self.get_remaining_seconds()
        timer_color = (255, 120, 120) if remaining <= 10 else (ACCENT if ACCENT else (120, 180, 255))
        timer_surf = self.big.render(f"Time: {remaining}s", True, timer_color)
        self.screen.blit(timer_surf, (16, 52))
        
        # Error message if problem failed to load
        if self.error_message:
            error_surf = self.font.render(self.error_message, True, (255, 100, 100))
            self.screen.blit(error_surf, (16, 90))
        
        # Problem UI
        if self.snippet_board:
            self.snippet_board.draw(self.screen)
        if self.problem_panel:
            self.problem_panel.draw(self.screen)
            
        pygame.display.flip()
