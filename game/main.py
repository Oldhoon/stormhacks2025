import pygame
import random

try:
    from .config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from .ui.problem_panel import ProblemPanel
    from .ui.snippet_board import SnippetBoard
except ImportError:
    from config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from ui.problem_panel import ProblemPanel
    from ui.snippet_board import SnippetBoard


# -------------------- Problem Text --------------------
TWO_SUM_TEXT = """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:
Input: nums = [3,3], target = 6
Output: [0,1]

Constraints:
2 <= nums.length <= 10^4
-10^9 <= nums[i] <= 10^9
-10^9 <= target <= 10^9
Only one valid answer exists.
Follow-up: Can you come up with an algorithm that is less than O(n^2) time complexity?"""

FIZZ_BUZZ_TEXT = """Given an integer n, return a string array answer (1-indexed) where:
- answer[i] == "FizzBuzz" if i is divisible by 3 and 5.
- answer[i] == "Fizz" if i is divisible by 3.
- answer[i] == "Buzz" if i is divisible by 5.
- answer[i] == i (as a string) if none of the above conditions are true.

Example:
Input: n = 5
Output: ["1","2","Fizz","4","Buzz"]

Constraints:
1 <= n <= 10^4"""


# -------------------- Meta + Snippets --------------------
PROBLEM_META = {
    "two-sum": {
        "id": "1",
        "slug": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "tags": ["Array", "Hash Table"],
        "url": "https://leetcode.com/problems/two-sum/",
        "text": TWO_SUM_TEXT,
    },
    "fizz-buzz": {
        "id": "412",
        "slug": "fizz-buzz",
        "title": "Fizz Buzz",
        "difficulty": "Easy",
        "tags": ["Math", "String"],
        "url": "https://leetcode.com/problems/fizz-buzz/",
        "text": FIZZ_BUZZ_TEXT,
    },
}

SNIPPETS = {
    "two-sum": [
        "def twoSum(nums, target):",
        "    seen = {}",
        "    for i, x in enumerate(nums):",
        "        need = target - x",
        "        if need in seen: return [seen[need], i]",
        "        seen[x] = i",
        "    return []",
    ],
    "fizz-buzz": [
        "def fizzBuzz(n):",
        "    res = []",
        "    for i in range(1, n + 1):",
        "        if i % 15 == 0:",
        "            res.append(\"FizzBuzz\")",
        "        elif i % 3 == 0:",
        "            res.append(\"Fizz\")",
        "        elif i % 5 == 0:",
        "            res.append(\"Buzz\")",
        "        else:",
        "            res.append(str(i))",
        "    return res",
    ],
}

PROBLEM_SLUGS = list(PROBLEM_META.keys())


def hardcoded_meta(slug: str):
    return PROBLEM_META.get(slug)


# --------------- Helpers: load, grade, choose next ---------------

def show_problem(problem_panel: ProblemPanel, board: SnippetBoard, slug: str, deterministic_seed: bool):
    """Load meta + palette into UI; shuffle palette."""
    meta = hardcoded_meta(slug)
    if not meta:
        return "Unknown problem"
    problem_panel.set_meta(meta)
    seed = int(meta["id"]) if deterministic_seed else None
    board.set_lines(SNIPPETS[slug], scramble=True, seed=seed)
    return f"Loaded ✓ {meta['title']} [{meta['difficulty']}] — snippets shuffled"


def grade_submission(slug: str, submitted_lines: list[str]):
    """Count lines in the correct position (case/space-preserving except leading/trailing)."""
    answer = SNIPPETS[slug]
    n = max(len(answer), len(submitted_lines))
    correct = 0
    for i in range(min(len(answer), len(submitted_lines))):
        if submitted_lines[i].strip() == answer[i].strip():
            correct += 1
    return correct, len(answer)


def random_other_slug(current_slug: str):
    choices = [s for s in PROBLEM_SLUGS if s != current_slug]
    return random.choice(choices) if choices else current_slug


# -------------------- Main --------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
    pygame.display.set_caption("Pygame — Problems")
    clock = pygame.time.Clock()

    # fonts
    font = pygame.font.SysFont(None, 24)
    big  = pygame.font.SysFont(None, 36)
    mono = pygame.font.SysFont("consolas", 18)

    # layout
    right_rect = pygame.Rect(LEFT_W + PADDING, 90, WIDTH - LEFT_W - PADDING * 2, HEIGHT - 120)
    left_rect  = pygame.Rect(32, 90, LEFT_W - PADDING * 2, HEIGHT - 120)

    # components
    problem = ProblemPanel(left_rect, fonts=(big, font, mono))
    board   = SnippetBoard(right_rect, fonts=(font, big, mono))

    # state
    current_slug = "two-sum"
    last_action = "Press [P] Two Sum • [F] Fizz Buzz • [Esc] quit"

    # score banner + auto-advance scheduling
    banner_text = None
    banner_until_ms = 0
    next_slug_pending = None

    # auto-load first problem (deterministic order)
    last_action = show_problem(problem, board, current_slug, deterministic_seed=True)

    running = True
    while running:
        dt = clock.tick(120) / 1000.0
        now = pygame.time.get_ticks()

        # auto-advance after banner timeout
        if banner_text and now >= banner_until_ms:
            if next_slug_pending:
                current_slug = next_slug_pending
                last_action = show_problem(problem, board, current_slug, deterministic_seed=False)
            banner_text = None
            next_slug_pending = None

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_p:
                    current_slug = "two-sum"
                    last_action = show_problem(problem, board, current_slug, deterministic_seed=False)
                elif e.key == pygame.K_f:
                    current_slug = "fizz-buzz"
                    last_action = show_problem(problem, board, current_slug, deterministic_seed=False)

            # delegate events (wire submit/reset)
            def submit_handler(code: str):
                # Gather the palette's current order
                submitted = [b.text for b in board.palette]
                got, total = grade_submission(current_slug, submitted)
                # show banner for 1.2 seconds
                nonlocal_banner = f"Score: {got}/{total} correct"
                nonlocal_duration_ms = 1200
                nonlocal next_slug_pending
                nonlocal banner_text, banner_until_ms
                banner_text = nonlocal_banner
                banner_until_ms = pygame.time.get_ticks() + nonlocal_duration_ms
                next_slug_pending = random_other_slug(current_slug)

            board.handle_event(
                e,
                on_submit=submit_handler,
                on_reset=lambda: board.set_lines(SNIPPETS[current_slug], scramble=True, seed=None),
            )
            problem.handle_event(e)

        board.update(dt)

        # draw
        screen.fill(BG)
        screen.blit(big.render("Pygame + LeetCode Demo", True, FG), (PADDING, 20))
        hint = "Press [P] Two Sum • [F] Fizz Buzz • [Esc] quit"
        screen.blit(font.render(hint, True, ACCENT), (PADDING, 48))

        board.draw(screen)
        problem.draw(screen)

        # score banner overlay
        if banner_text:
            pad = 12
            msg = f"{banner_text} — loading next..."
            text_surf = big.render(msg, True, (240, 240, 245))
            w = text_surf.get_width() + pad * 2
            h = text_surf.get_height() + pad * 2
            x = (WIDTH - w) // 2
            y = 18  # under the title
            # semi-transparent bg
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((20, 20, 30, 180))
            pygame.draw.rect(overlay, ACCENT, overlay.get_rect(), width=2, border_radius=10)
            overlay.blit(text_surf, (pad, pad))
            screen.blit(overlay, (x, y))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
