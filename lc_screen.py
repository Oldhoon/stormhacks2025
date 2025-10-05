"""
LeetCode Screen - Wraps the LeetCode problem UI to render on a surface
"""
import pygame
import random

try:
    from game.config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from game.ui.problem_panel import ProblemPanel
    from game.ui.snippet_board import SnippetBoard
    from game.problems.loader import random_problem, random_other
except ImportError:
    from config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from ui.problem_panel import ProblemPanel
    from ui.snippet_board import SnippetBoard
    from problems.loader import random_problem, random_other


class LCScreen:
    """Renders the LeetCode problem-solving interface on a surface with timer"""
    
    def __init__(self, surface, timer_duration=30000):  # 30 seconds default
        self.surface = surface
        self.width = surface.get_width()
        self.height = surface.get_height()
        
        # Timer
        self.timer_duration = timer_duration
        self.timer_start = None
        self.timer_active = False
        
        # Fonts
        self.font = pygame.font.SysFont(None, 24)
        self.big = pygame.font.SysFont(None, 36)
        self.mono = pygame.font.SysFont("consolas", 18)
        self.timer_font = pygame.font.Font(None, 64)
        
        # Layout - use screen dimensions
        right_rect = pygame.Rect(LEFT_W + PADDING, 90, self.width - LEFT_W - PADDING * 2, self.height - 120)
        left_rect = pygame.Rect(32, 90, LEFT_W - PADDING * 2, self.height - 120)
        
        # Components
        self.problem_panel = ProblemPanel(right_rect, fonts=(self.big, self.font, self.mono))
        self.board = SnippetBoard(left_rect, fonts=(self.font, self.big, self.mono))
        
        # State
        self.current_problem = None
        self.problem_solved = False
        
    def start_timer(self):
        """Start or restart the timer"""
        self.timer_start = pygame.time.get_ticks()
        self.timer_active = True
        self.problem_solved = False
        
    def get_remaining_time(self):
        """Returns remaining time in milliseconds, or 0 if expired"""
        if not self.timer_active or self.timer_start is None:
            return self.timer_duration
        
        elapsed = pygame.time.get_ticks() - self.timer_start
        remaining = max(0, self.timer_duration - elapsed)
        return remaining
    
    def is_timer_expired(self):
        """Check if timer has run out"""
        return self.timer_active and self.get_remaining_time() <= 0
    
    def load_problem(self, problem=None):
        """Load a problem into the UI"""
        if problem is None:
            problem = random_problem()
        
        self.current_problem = problem
        self.problem_solved = False
        
        # Set up problem panel
        meta = {
            "id": problem.id,
            "slug": problem.slug,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "tags": problem.tags,
            "url": problem.url,
            "text": problem.text,
        }
        self.problem_panel.set_meta(meta)
        
        # Set up snippet board with scrambled snippets
        seed = int(problem.id)
        self.board.set_lines(problem.snippets, scramble=True, seed=seed)
        
    def handle_event(self, event):
        """Handle events for the LC screen"""
        def submit_handler(_code_ignored: str):
            # Grade submission
            submitted = [b.text for b in self.board.palette]
            answer = self.current_problem.snippets
            correct = 0
            for i in range(min(len(answer), len(submitted))):
                if submitted[i].strip() == answer[i].strip():
                    correct += 1
            
            # Check if all correct
            if correct == len(answer) and len(submitted) == len(answer):
                self.problem_solved = True
                self.timer_active = False
        
        self.board.handle_event(
            event,
            on_submit=submit_handler,
            on_reset=lambda: self.board.set_lines(self.current_problem.snippets, scramble=True, seed=None)
        )
        self.problem_panel.handle_event(event)
    
    def update(self, dt):
        """Update the LC screen state"""
        self.board.update(dt)
    
    def draw(self):
        """Draw the LC screen to its surface"""
        # Background
        self.surface.fill(BG)
        
        # Title
        title_text = "Solve to Win - or Wait for Revival!"
        self.surface.blit(self.big.render(title_text, True, FG), (PADDING, 20))
        
        # Draw timer
        remaining_ms = self.get_remaining_time()
        seconds = int(remaining_ms / 1000)
        timer_color = (255, 80, 80) if seconds <= 5 else (255, 255, 255)
        timer_text = f"{seconds}s"
        timer_surf = self.timer_font.render(timer_text, True, timer_color)
        timer_rect = timer_surf.get_rect(center=(self.width // 2, 50))
        self.surface.blit(timer_surf, timer_rect)
        
        # Draw UI components
        self.board.draw(self.surface)
        self.problem_panel.draw(self.surface)
