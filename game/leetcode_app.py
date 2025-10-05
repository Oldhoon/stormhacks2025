import random
import pygame

try:
    from .config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from .ui.problem_panel import ProblemPanel
    from .ui.snippet_board import SnippetBoard
    from .problems.loader import random_problem, random_other
except ImportError:  # pragma: no cover - fallback when run as a script
    from config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from ui.problem_panel import ProblemPanel
    from ui.snippet_board import SnippetBoard
    from problems.loader import random_problem, random_other


def _meta_from_problem(problem):
    return {
        "id": problem.id,
        "slug": problem.slug,
        "title": problem.title,
        "difficulty": problem.difficulty,
        "tags": problem.tags,
        "url": problem.url,
        "text": problem.text,
    }


def grade_submission(problem, submitted_lines):
    answer = problem.snippets
    correct = 0
    upto = min(len(answer), len(submitted_lines))
    for idx in range(upto):
        if submitted_lines[idx].strip() == answer[idx].strip():
            correct += 1
    return correct, len(answer)


class LeetCodeGame:
    """Reusable drag‑and‑drop LeetCode mini-game."""

    def __init__(self, screen, strict_mode=False, time_limit_sec=None):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.strict_mode = strict_mode
        self.time_limit_ms = int(time_limit_sec * 1000) if time_limit_sec else None

        # viewport (centre UI in whatever surface we are handed)
        self.view_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.view_rect.center = self.screen_rect.center

        # fonts
        self.font = pygame.font.SysFont(None, 24)
        self.big = pygame.font.SysFont(None, 36)
        self.mono = pygame.font.SysFont("consolas", 18)

        # layout
        problem_rect = pygame.Rect(
            self.view_rect.left + 32,
            self.view_rect.top + 90,
            LEFT_W - PADDING * 2,
            HEIGHT - 120,
        )
        board_rect = pygame.Rect(
            self.view_rect.left + LEFT_W + PADDING,
            self.view_rect.top + 90,
            WIDTH - LEFT_W - PADDING * 2,
            HEIGHT - 120,
        )

        self.problem_panel = ProblemPanel(problem_rect, fonts=(self.big, self.font, self.mono))
        self.board = SnippetBoard(board_rect, fonts=(self.font, self.big, self.mono))

        # state
        self.current_problem = random_problem()
        self.last_action = self._show_problem(self.current_problem, deterministic_seed=True)
        self.banner_text = None
        self.banner_until_ms = 0
        self.next_problem_pending = None

        self.status = "running"  # running | success | failure | quit
        self.result_message = None
        self.failure_reason = None
        self.lock_until_ms = 0
        self.quit_requested = False
        self.challenge_started_at = pygame.time.get_ticks()

    # ------------------------------------------------------------------ helpers
    def _show_problem(self, problem, deterministic_seed):
        if problem is None:
            self.problem_panel.set_meta({})
            self.board.set_lines([])
            return "Unknown problem"
        self.problem_panel.set_meta(_meta_from_problem(problem))
        seed = int(problem.id) if deterministic_seed else None
        self.board.set_lines(problem.snippets, scramble=True, seed=seed)
        self.challenge_started_at = pygame.time.get_ticks()
        return f"Loaded {problem.title} [{problem.difficulty}]"

    def _handle_submit(self):
        submitted = [block.text for block in self.board.palette]
        got, total = grade_submission(self.current_problem, submitted)
        if self.strict_mode:
            if got == total:
                self.status = "success"
                self.result_message = f"Solved! {got}/{total} correct"
                self.failure_reason = None
            else:
                self.status = "failure"
                self.failure_reason = "incorrect"
                self.result_message = f"{got}/{total} correct - Knight revives!"
            self.lock_until_ms = pygame.time.get_ticks() + 1500
        else:
            self.banner_text = f"Score: {got}/{total} correct"
            self.banner_until_ms = pygame.time.get_ticks() + 1200
            self.next_problem_pending = random_other(self.current_problem.slug)
        return got, total

    def _check_time_limit(self):
        if not (self.strict_mode and self.time_limit_ms and self.status == "running"):
            return
        elapsed = pygame.time.get_ticks() - self.challenge_started_at
        if elapsed >= self.time_limit_ms:
            self.status = "failure"
            self.failure_reason = "timeout"
            self.result_message = "Time's up! Knight revives!"
            self.lock_until_ms = pygame.time.get_ticks() + 1500

    # ------------------------------------------------------------------ public API
    def process_event(self, event):
        if self.status != "running":
            if event.type == pygame.QUIT:
                self.status = "quit"
                self.quit_requested = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.status = "quit"
                self.quit_requested = True
            return

        if event.type == pygame.QUIT:
            self.status = "quit"
            self.quit_requested = True
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.status = "quit"
                self.quit_requested = True
                return
            if not self.strict_mode and event.key == pygame.K_p:
                self.current_problem = random_other(self.current_problem.slug)
                self.last_action = self._show_problem(self.current_problem, deterministic_seed=False)

        def submit_handler(_ignored):
            self._handle_submit()

        def reset_handler():
            self.board.set_lines(self.current_problem.snippets, scramble=True, seed=None)

        self.board.handle_event(event, on_submit=submit_handler, on_reset=reset_handler)
        self.problem_panel.handle_event(event)

    def update(self, dt):
        if self.status == "running":
            self._check_time_limit()
            self.board.update(dt)
            if not self.strict_mode and self.banner_text:
                now = pygame.time.get_ticks()
                if now >= self.banner_until_ms:
                    if self.next_problem_pending is not None:
                        self.current_problem = self.next_problem_pending
                        self.last_action = self._show_problem(self.current_problem, deterministic_seed=False)
                    self.banner_text = None
                    self.next_problem_pending = None
        else:
            if self.lock_until_ms and pygame.time.get_ticks() >= self.lock_until_ms:
                self.lock_until_ms = 0

    def draw(self):
        self.screen.fill(BG)

        if self.screen_rect.size != self.view_rect.size:
            frame_rect = self.view_rect.inflate(32, 32)
            pygame.draw.rect(self.screen, (12, 12, 14), frame_rect)

        title_pos = (self.view_rect.left + PADDING, self.view_rect.top + 20)
        hint_pos = (self.view_rect.left + PADDING, self.view_rect.top + 48)

        title = self.big.render("LeetCode Arena", True, FG)
        hint_text = "Press [P] next random | [Esc] Quit" if not self.strict_mode else "Arrange lines, SUBMIT once"
        hint = self.font.render(hint_text, True, ACCENT)
        self.screen.blit(title, title_pos)
        self.screen.blit(hint, hint_pos)

        if self.strict_mode and self.time_limit_ms:
            remaining = max(0, self.time_limit_ms - (pygame.time.get_ticks() - self.challenge_started_at))
            seconds = remaining / 1000
            color = (255, 120, 120) if seconds <= 10 else ACCENT
            timer_text = self.big.render(f"{seconds:05.1f}s", True, color)
            timer_rect = timer_text.get_rect(topright=(self.view_rect.right - PADDING, self.view_rect.top + 16))
            self.screen.blit(timer_text, timer_rect)

        self.board.draw(self.screen)
        self.problem_panel.draw(self.screen)

        if self.last_action:
            footer = self.font.render(self.last_action, True, MUTED)
            self.screen.blit(footer, (self.view_rect.left + PADDING, self.view_rect.bottom - 28))

        if self.banner_text:
            pad = 12
            msg = f"{self.banner_text} - loading next..."
            text_surf = self.big.render(msg, True, (240, 240, 245))
            w = text_surf.get_width() + pad * 2
            h = text_surf.get_height() + pad * 2
            x = self.view_rect.left + (self.view_rect.width - w) // 2
            y = self.view_rect.top + 18
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((20, 20, 30, 180))
            pygame.draw.rect(overlay, ACCENT, overlay.get_rect(), width=2, border_radius=10)
            overlay.blit(text_surf, (pad, pad))
            self.screen.blit(overlay, (x, y))

        if self.strict_mode and self.status in {"success", "failure"}:
            overlay = pygame.Surface(self.view_rect.size, pygame.SRCALPHA)
            overlay.fill((10, 10, 14, 200))
            msg = self.big.render(self.result_message or "", True, FG)
            sub = self.font.render("Returning to arena...", True, MUTED)
            overlay.blit(
                msg,
                ((self.view_rect.width - msg.get_width()) // 2, (self.view_rect.height - msg.get_height()) // 2 - 20),
            )
            overlay.blit(
                sub,
                ((self.view_rect.width - sub.get_width()) // 2, (self.view_rect.height - sub.get_height()) // 2 + 20),
            )
            self.screen.blit(overlay, self.view_rect.topleft)

    def is_finished(self):
        if self.status in {"success", "failure", "quit"}:
            if self.lock_until_ms:
                return pygame.time.get_ticks() >= self.lock_until_ms
            return True
        return False

    def get_result(self):
        return self.status

    def get_failure_reason(self):
        return self.failure_reason

    def run(self):
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(120) / 1000.0
            for event in pygame.event.get():
                self.process_event(event)
            if self.status == "quit":
                break
            self.update(dt)
            self.draw()
            pygame.display.flip()
            if self.strict_mode and self.is_finished():
                break
        return self.status
