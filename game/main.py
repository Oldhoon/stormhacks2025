import pygame
try:
    from .config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from .ui.problem_panel import ProblemPanel
    from .ui.snippet_board import SnippetBoard
except ImportError:
    from config import WIDTH, HEIGHT, BG, FG, MUTED, ACCENT, ERR, PADDING, LEFT_W
    from ui.problem_panel import ProblemPanel
    from ui.snippet_board import SnippetBoard


# -------------------- Demo Problem Text --------------------
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

def hardcoded_meta(slug: str):
    if slug == "two-sum":
        return {
            "id": "1",
            "slug": "two-sum",
            "title": "Two Sum",
            "difficulty": "Easy",
            "tags": ["Array", "Hash Table"],
            "url": "https://leetcode.com/problems/two-sum/",
            "text": TWO_SUM_TEXT,
        }
    return None

# Snippets (we’ll shuffle these)
SNIPPET_TWO_SUM = [
    "def twoSum(nums, target):",
    "    seen = {}",
    "    for i, x in enumerate(nums):",
    "        need = target - x",
    "        if need in seen: return [seen[need], i]",
    "        seen[x] = i",
    "    return []",
]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
    pygame.display.set_caption("Pygame — Problems")
    clock = pygame.time.Clock()

    # fonts
    font = pygame.font.SysFont(None, 24)
    big  = pygame.font.SysFont(None, 36)
    mono = pygame.font.SysFont("consolas", 18)

    # layout rects
    right_rect = pygame.Rect(LEFT_W + PADDING, 90, WIDTH - LEFT_W - PADDING * 2, HEIGHT - 120)
    left_rect  = pygame.Rect(32, 90, LEFT_W - PADDING * 2, HEIGHT - 120)

    # components
    problem = ProblemPanel(left_rect, fonts=(big, font, mono))
    board   = SnippetBoard(right_rect, fonts=(font, big, mono))

    # ---------- AUTO-LOAD the question on startup (scrambled) ----------
    meta = hardcoded_meta("two-sum")
    if meta:
        problem.set_meta(meta)
        # deterministic order per question id; use seed=None for new random each run
        board.set_lines(SNIPPET_TWO_SUM, scramble=True, seed=int(meta["id"]))
        last_action = f"Loaded ✓ {meta['title']} [{meta['difficulty']}] — snippets shuffled"
    else:
        last_action = "Press [P] to load Two Sum • [Esc] quit"

    running = True
    while running:
        dt = clock.tick(120) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_p:
                    meta = hardcoded_meta("two-sum")
                    if meta:
                        problem.set_meta(meta)
                        # re-shuffle on demand; seed=None -> different order each time you press P
                        board.set_lines(SNIPPET_TWO_SUM, scramble=True, seed=None)
                        last_action = f"Reloaded ✓ {meta['title']} — snippets re-shuffled"

            # delegate events
            problem.handle_event(e)
            board.handle_event(
                e,
                on_submit=lambda code: print("SUBMIT clicked. Code (first 300 chars):\n", code[:300]),
                on_reset=lambda: board.set_lines(SNIPPET_TWO_SUM, scramble=True, seed=None),
            )

        # per-frame updates (smooth dragging)
        board.update(dt)

        # draw
        screen.fill(BG)
        screen.blit(big.render("Pygame + LeetCode Demo", True, FG), (PADDING, 20))
        screen.blit(font.render(last_action, True, ACCENT), (PADDING, 48))

        board.draw(screen)
        problem.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
