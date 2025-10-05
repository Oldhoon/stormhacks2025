# # game/main.py
# import pygame
# import random

# # --- package / script friendly imports ---
# try:
#     from .config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
#     from .ui.problem_panel import ProblemPanel
#     from .ui.snippet_board import SnippetBoard
#     from .problems.loader import get as load_by_slug, random_problem, random_other
# except ImportError:
#     # running as: python game/main.py
#     from config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
#     from ui.problem_panel import ProblemPanel
#     from ui.snippet_board import SnippetBoard
#     from problems.loader import get as load_by_slug, random_problem, random_other


# # --------------- Helpers ---------------

# def _meta_from_problem(p):
#     """ProblemPanel expects a dict with these keys."""
#     return {
#         "id": p.id,
#         "slug": p.slug,
#         "title": p.title,
#         "difficulty": p.difficulty,
#         "tags": p.tags,
#         "url": p.url,
#         "text": p.text,
#     }


# def show_problem(problem_panel: ProblemPanel, board: SnippetBoard, p, deterministic_seed: bool):
#     """Load meta + palette into UI; optionally deterministic shuffle by id."""
#     if p is None:
#         return "Unknown problem"
#     problem_panel.set_meta(_meta_from_problem(p))
#     seed = int(p.id) if deterministic_seed else None
#     board.set_lines(p.snippets, scramble=True, seed=seed)
#     return f"Loaded ✓ {p.title} [{p.difficulty}] — snippets shuffled"


# def grade_submission(p, submitted_lines: list[str]):
#     """Counts lines that are in the correct position (whitespace-insensitive at ends)."""
#     answer = p.snippets
#     correct = 0
#     upto = min(len(answer), len(submitted_lines))
#     for i in range(upto):
#         if submitted_lines[i].strip() == answer[i].strip():
#             correct += 1
#     return correct, len(answer)


# # -------------------- Main --------------------

# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
#     pygame.display.set_caption("Pygame — Problems")
#     clock = pygame.time.Clock()

#     # fonts
#     font = pygame.font.SysFont(None, 24)
#     big  = pygame.font.SysFont(None, 36)
#     mono = pygame.font.SysFont("consolas", 18)

#     # layout
#     right_rect = pygame.Rect(LEFT_W + PADDING, 90, WIDTH - LEFT_W - PADDING * 2, HEIGHT - 120)
#     left_rect  = pygame.Rect(32, 90, LEFT_W - PADDING * 2, HEIGHT - 120)

#     # components
#     problem_panel = ProblemPanel(right_rect, fonts=(big, font, mono))
#     board         = SnippetBoard(left_rect,  fonts=(font, big, mono))

#     # state
#     current = random_problem()            # grab any problem from the YAML bank
#     last_action = show_problem(problem_panel, board, current, deterministic_seed=True)

#     # score banner + auto-advance scheduling
#     banner_text = None
#     banner_until_ms = 0
#     next_problem_pending = None

#     running = True
#     while running:
#         dt = clock.tick(120) / 1000.0
#         now = pygame.time.get_ticks()

#         # auto-advance after banner timeout
#         if banner_text and now >= banner_until_ms:
#             if next_problem_pending is not None:
#                 current = next_problem_pending
#                 last_action = show_problem(problem_panel, board, current, deterministic_seed=False)
#             banner_text = None
#             next_problem_pending = None

#         for e in pygame.event.get():
#             if e.type == pygame.QUIT:
#                 running = False
#             elif e.type == pygame.KEYDOWN:
#                 if e.key == pygame.K_ESCAPE:
#                     running = False
#                 elif e.key == pygame.K_p:
#                     # load a different random problem from the bank
#                     current = random_other(current.slug)
#                     last_action = show_problem(problem_panel, board, current, deterministic_seed=False)

#             # submit/reset wiring for the snippet board
#             def submit_handler(_code_ignored: str):
#                 submitted = [b.text for b in board.palette]  # current order on the board
#                 got, total = grade_submission(current, submitted)
#                 # show banner for 1.2s, then queue a new random problem
#                 nonlocal_banner = f"Score: {got}/{total} correct"
#                 nonlocal_duration_ms = 1200
#                 nonlocal banner_text, banner_until_ms, next_problem_pending
#                 banner_text = nonlocal_banner
#                 banner_until_ms = pygame.time.get_ticks() + nonlocal_duration_ms
#                 next_problem_pending = random_other(current.slug)

#             board.handle_event(
#                 e,
#                 on_submit=submit_handler,
#                 on_reset=lambda: board.set_lines(current.snippets, scramble=True, seed=None),
#             )
#             problem_panel.handle_event(e)

#         board.update(dt)

#         # draw
#         screen.fill(BG)
#         screen.blit(big.render("Pygame + LeetCode Demo", True, FG), (PADDING, 20))
#         hint = "Press [P] Next random • [Esc] Quit"
#         screen.blit(font.render(hint, True, ACCENT), (PADDING, 48))

#         board.draw(screen)
#         problem_panel.draw(screen)

#         # score banner overlay
#         if banner_text:
#             pad = 12
#             msg = f"{banner_text} — loading next..."
#             text_surf = big.render(msg, True, (240, 240, 245))
#             w = text_surf.get_width() + pad * 2
#             h = text_surf.get_height() + pad * 2
#             x = (WIDTH - w) // 2
#             y = 18  # under the title
#             overlay = pygame.Surface((w, h), pygame.SRCALPHA)
#             overlay.fill((20, 20, 30, 180))
#             pygame.draw.rect(overlay, ACCENT, overlay.get_rect(), width=2, border_radius=10)
#             overlay.blit(text_surf, (pad, pad))
#             screen.blit(overlay, (x, y))

#         pygame.display.flip()

#     pygame.quit()


# if __name__ == "__main__":
#     main()
import pygame

try:
    from .config import WIDTH, HEIGHT
    from .leetcode_app import LeetCodeGame
except ImportError:  # pragma: no cover
    from config import WIDTH, HEIGHT
    from leetcode_app import LeetCodeGame


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
    pygame.display.set_caption("Pygame - Problems")
    clock = pygame.time.Clock()
    game = LeetCodeGame(screen, strict_mode=False)

    running = True
    while running:
        dt = clock.tick(120) / 1000.0
        for event in pygame.event.get():
            game.process_event(event)
            if game.get_result() == "quit":
                running = False
                break
        if not running:
            break
        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
