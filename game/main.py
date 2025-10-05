# main.py
import pygame
import threading
import queue
import random

# ---------- optional integrations you already have ----------
try:
    from .api import LCClient
except ImportError:
    from api import LCClient

# optional local judge (safe if missing)
try:
    from local_cli.judge_cli import run_local as local_run
except Exception:
    local_run = None  # no local judge available

# ------- layout / colors -------
WIDTH, HEIGHT = 900, 600
BG = (18, 18, 20)
FG = (230, 230, 235)
MUTED = (170, 170, 180)
ACCENT = (120, 180, 255)
ERR = (255, 120, 120)
PADDING = 16
LEFT_W = int(WIDTH * 0.52)
# ------------------------------

def worker(fn, args, outq):
    try:
        result = fn(*args)
        outq.put(("ok", result))
    except Exception as e:
        outq.put(("err", str(e)))

def draw_wrapped(surface, text, font, color, x, y, max_w, line_h=None):
    if not text:
        return y
    words = text.split()
    line = ""
    lh = line_h or (font.get_height() + 2)
    for w in words:
        test = f"{line} {w}".strip()
        if font.size(test)[0] <= max_w:
            line = test
        else:
            surface.blit(font.render(line, True, color), (x, y))
            y += lh
            line = w
    if line:
        surface.blit(font.render(line, True, color), (x, y))
        y += lh
    return y

# ---------- snippet puzzles for Blocks mode ----------
SNIPPET_PUZZLES = {
    "two-sum": {
        "title": "Two Sum — Order the lines",
        "entrypoint": "twoSum",
        "template_preamble": "from typing import List",
        "blocks": [
            "def twoSum(nums: List[int], target: int):",
            "    seen = {}",
            "    for i, x in enumerate(nums):",
            "        need = target - x",
            "        if need in seen: return [seen[need], i]",
            "        seen[x] = i",
            "    return []",
        ],
        "distractors": [
            "    nums.sort()",
        ],
    },
    # add more slugs here if you want blocks for them
}

# ---------- Blocks mode UI ----------
class _Block:
    def __init__(self, text, uid):
        self.text = text
        self.uid = uid
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.dragging = False
        self.offset = (0, 0)

    def draw(self, surf, x, y, w, font, active=False):
        pad = 8
        txt = font.render(self.text, True, FG)
        h = txt.get_height() + pad * 2
        self.rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, (45, 45, 55), self.rect, border_radius=8)
        pygame.draw.rect(surf, ACCENT if active else (60, 60, 75), self.rect, 2, border_radius=8)
        surf.blit(txt, (x + pad, y + pad))
        return h + 6

class SnippetBoard:
    """Drag between left (palette) and right (assemble). RESET moves everything right→left."""
    def __init__(self, left_rect: pygame.Rect, right_rect: pygame.Rect, font, big, mono):
        self.left_rect = left_rect
        self.right_rect = right_rect
        self.font, self.big, self.mono = font, big, mono

        # Buttons
        self.btn_rect = pygame.Rect(self.right_rect.left, self.right_rect.bottom - 44, 130, 34)  # CHECK
        self.reset_rect = pygame.Rect(self.btn_rect.right + 12, self.btn_rect.y, 130, 34)        # RESET

        self.palette = []
        self.assemble = []
        self.title = "Snippet Puzzle"
        self.template_preamble = ""
        self.entrypoint = ""
        self.status = "Drag lines between panels. Press CHECK."

        # drag state
        self._drag = None
        self._drag_from = None              # 'palette' or 'assemble'
        self._drag_from_index = None        # original index in its source list
        self._insert_idx = None             # target insert position
        self._insert_target = None          # 'left' or 'right'

        # truth / scoring
        self.truth_ids = []
        self.distractor_ids = set()
        self.attempts = 0
        self.err_runs = 0
        self.tests_passed = 0
        self.tests_total = 0
        self.round_ms = 120_000
        self.start_ticks = pygame.time.get_ticks()

        # reveal score only after a submission
        self.show_score = False
        self.last_build = 0.0
        self.last_run = 0.0
        self.last_final = 0
        self.last_tbon = 0.0
        self.last_distractors = 0

        # layout helpers for consistent insert math
        self._left_list_top = self.left_rect.y + 50
        self._right_list_top = self.right_rect.y + 56
        self._row_h = 36  # row height used for insert-position math

        # original order map for proper RESET behavior
        self._initial_order = {}

    def load_puzzle(self, puzzle: dict | None):
        self.palette, self.assemble = [], []
        self.status = "Drag lines between panels. Press CHECK."
        if not puzzle:
            self.title = "No puzzle available for this problem"
            self.template_preamble = ""
            self.entrypoint = ""
            self.truth_ids = []
            self.distractor_ids = set()
            self._initial_order = {}
        else:
            self.title = puzzle.get("title", "Snippet Puzzle")
            self.template_preamble = puzzle.get("template_preamble", "")
            self.entrypoint = puzzle.get("entrypoint", "")
            blocks = [_Block(t, f"b{i}") for i, t in enumerate(puzzle.get("blocks", []), 1)]
            distract = [_Block(t, f"d{i}") for i, t in enumerate(puzzle.get("distractors", []), 1)]
            # keep ordered palette (don't shuffle)
            self.palette = blocks + distract
            self.truth_ids = [b.uid for b in blocks]
            self.distractor_ids = {d.uid for d in distract}
            # remember original left-side order for RESET
            self._initial_order = {b.uid: i for i, b in enumerate(self.palette)}

        # reset scoring/timing & hide score
        self.attempts = self.err_runs = 0
        self.tests_passed = self.tests_total = 0
        self.start_ticks = pygame.time.get_ticks()
        self.show_score = False
        self.last_build = self.last_run = self.last_tbon = 0.0
        self.last_final = 0
        self.last_distractors = 0

    def materialize_code(self):
        parts = []
        if self.template_preamble:
            parts.append(self.template_preamble)
        parts.extend(b.text for b in self.assemble)
        return "\n".join(parts) + "\n"

    # --- NEW: reset helper ---
    def reset_to_left(self):
        """Move everything from right to left and restore original left order."""
        all_blocks = self.palette + self.assemble
        # sort by original order; unknown ids go to the end
        all_blocks.sort(key=lambda b: self._initial_order.get(b.uid, 10**9))
        self.palette = all_blocks
        self.assemble = []
        # clear drag/insert hints
        self._drag = None
        self._insert_idx = None
        self._insert_target = None
        self._drag_from = None
        self._drag_from_index = None
        # do not change attempts/penalties; just update UI
        self.show_score = False
        self.status = "Reset: moved all snippets back to the left."

    def _clamp_idx(self, idx: int, side: str) -> int:
        if side == "left":
            return max(0, min(len(self.palette), idx))
        else:
            return max(0, min(len(self.assemble), idx))

    def handle_event(self, e, on_run=None):
        # quick keyboard reset (optional)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            self.reset_to_left()
            return

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = e.pos
            # RESET button
            if self.reset_rect.collidepoint(pos):
                self.reset_to_left()
                return

            # hit-test palette first, then assemble
            for src_name, lst in (("palette", self.palette), ("assemble", self.assemble)):
                for i, b in enumerate(lst):
                    if b.rect.collidepoint(pos):
                        self._drag = b
                        b.dragging = True
                        b.offset = (pos[0] - b.rect.x, pos[1] - b.rect.y)
                        self._drag_from = src_name
                        self._drag_from_index = i
                        # remove immediately from its source list (we'll place it on drop)
                        lst.pop(i)
                        self._insert_idx = None
                        self._insert_target = None
                        return

            # CHECK button
            if self.btn_rect.collidepoint(pos):
                code = self.materialize_code()
                try:
                    compile(code, "<user>", "exec")
                except SyntaxError as se:
                    self.status = f"SyntaxError line {se.lineno}: {se.msg}"
                    self.attempts += 1
                    self.err_runs += 1
                    self.show_score = False
                else:
                    res = on_run(code) if on_run else None
                    self.attempts += 1

                    # compute scoring in all cases (even if no judge)
                    if isinstance(res, dict):
                        if not res.get("ok"):
                            self.err_runs += 1
                            self.status = res.get("message") or "Run failed."

                        self.tests_passed = res.get("passed", 0)
                        self.tests_total = res.get("total", 0)
                    else:
                        self.tests_passed = 0
                        self.tests_total = 0
                        if res is None:
                            self.status = "Score updated (no judge)."

                    player_ids = [b.uid for b in self.assemble]
                    self.last_distractors = sum(1 for b in self.assemble if b.uid in self.distractor_ids)
                    self.last_build = build_score(player_ids, self.truth_ids, self.last_distractors)
                    self.last_run = run_score(self.tests_passed, self.tests_total)
                    elapsed = pygame.time.get_ticks() - self.start_ticks
                    self.last_tbon = time_bonus(elapsed, self.round_ms)
                    self.last_final = compute_final(
                        self.last_build, self.last_run, self.last_tbon,
                        self.attempts, 0, self.err_runs, self.last_distractors
                    )
                    self.show_score = True

                    if isinstance(res, dict) and res.get("ok"):
                        if self.tests_total and self.tests_passed == self.tests_total:
                            self.status = "All tests passed! 🎉"
                        else:
                            self.status = f"Passed {self.tests_passed}/{self.tests_total} tests"
                return

        if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self._drag:
            # decide final drop
            if self._insert_target == "right":
                idx = self._clamp_idx(self._insert_idx or 0, "right")
                self.assemble.insert(idx, self._drag)
            elif self._insert_target == "left":
                idx = self._clamp_idx(self._insert_idx or 0, "left")
                self.palette.insert(idx, self._drag)
            else:
                # cancel → put back where it came from, at original index
                if self._drag_from == "palette":
                    idx = self._drag_from_index if self._drag_from_index is not None else len(self.palette)
                    self.palette.insert(idx, self._drag)
                else:
                    idx = self._drag_from_index if self._drag_from_index is not None else len(self.assemble)
                    self.assemble.insert(idx, self._drag)

            # clear drag state
            self._drag.dragging = False
            self._drag = None
            self._insert_idx = None
            self._insert_target = None
            self._drag_from = None
            self._drag_from_index = None
            return

        if e.type == pygame.MOUSEMOTION and self._drag:
            mx, my = e.pos
            self._drag.rect.topleft = (mx - self._drag.offset[0], my - self._drag.offset[1])

            # compute tentative insert target + index based on cursor
            if self.right_rect.collidepoint(e.pos):
                y = my - self._right_list_top
                self._insert_target = "right"
                self._insert_idx = self._clamp_idx(y // self._row_h, "right")
            elif self.left_rect.collidepoint(e.pos):
                y = my - self._left_list_top
                self._insert_target = "left"
                self._insert_idx = self._clamp_idx(y // self._row_h, "left")
            else:
                self._insert_target = None
                self._insert_idx = None

    def draw(self, surf):
        # panels
        pygame.draw.rect(surf, (28, 28, 36), self.left_rect, border_radius=12)
        pygame.draw.rect(surf, (28, 28, 36), self.right_rect, border_radius=12)
        # headers
        surf.blit(self.big.render(self.title, True, FG), (self.left_rect.x + 12, self.left_rect.y + 10))
        surf.blit(self.big.render("Assemble", True, FG), (self.right_rect.x + 12, self.right_rect.y + 10))
        surf.blit(self.font.render(self.status, True, MUTED), (self.right_rect.x + 12, self.right_rect.y + 36))

        # palette (ordered lines)
        y_left = self._left_list_top
        for b in self.palette:
            y_left += b.draw(surf, self.left_rect.x + 12, y_left, self.left_rect.w - 24, self.mono, active=False)

        # assemble
        y_right = self._right_list_top
        for b in self.assemble:
            y_right += b.draw(surf, self.right_rect.x + 12, y_right, self.right_rect.w - 24, self.mono, active=False)

        # insertion guide line
        if self._insert_target == "right" and self._insert_idx is not None:
            y_line = self._right_list_top + self._insert_idx * self._row_h
            pygame.draw.line(surf, ACCENT, (self.right_rect.x + 10, y_line), (self.right_rect.right - 10, y_line), 2)
        elif self._insert_target == "left" and self._insert_idx is not None:
            y_line = self._left_list_top + self._insert_idx * self._row_h
            pygame.draw.line(surf, ACCENT, (self.left_rect.x + 10, y_line), (self.left_rect.right - 10, y_line), 2)

        # CHECK button
        pygame.draw.rect(surf, ACCENT, self.btn_rect, border_radius=8)
        surf.blit(self.big.render("CHECK", True, (10, 10, 15)), (self.btn_rect.x + 14, self.btn_rect.y + 4))

        # RESET button
        pygame.draw.rect(surf, (45, 45, 55), self.reset_rect, border_radius=8)
        pygame.draw.rect(surf, ERR, self.reset_rect, 2, border_radius=8)
        surf.blit(self.big.render("RESET", True, ERR), (self.reset_rect.x + 14, self.reset_rect.y + 4))

        # --- score HUD (only after submission) ---
        if self.show_score:
            hud_x = self.right_rect.right - 240
            hud_y = self.right_rect.y + 8

            def _bar(ypos, label, frac):
                frac = max(0.0, min(1.0, frac))
                w, h = 220, 10
                bg = pygame.Rect(hud_x, ypos, w, h)
                fg = pygame.Rect(hud_x, ypos, int(w * frac), h)
                pygame.draw.rect(surf, (60, 60, 75), bg, border_radius=6)
                pygame.draw.rect(surf, ACCENT, fg, border_radius=6)
                surf.blit(self.font.render(f"{label}: {int(frac*100)}%", True, MUTED), (hud_x, ypos - 16))

            _bar(hud_y + 20, "Build", self.last_build)
            _bar(hud_y + 44, "Run",   self.last_run)
            surf.blit(self.big.render(f"SCORE: {self.last_final}", True, FG), (hud_x, hud_y + 70))
        else:
            # subtle hint only; no percentages
            hint = "Press CHECK to see score  •  Press R or RESET to move all back"
            surf.blit(self.font.render(hint, True, MUTED), (self.right_rect.right - 360, self.right_rect.y + 8))

# ---------- scoring helpers ----------
def lcs_len(a, b):
    # a, b are lists of block ids (only canonical blocks)
    n, m = len(a), len(b)
    dp = [0] * (m + 1)
    for i in range(1, n + 1):
        prev = 0
        for j in range(1, m + 1):
            cur = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = cur
    return dp[m]

def build_score(player_ids, truth_ids, distractor_ids_in_assemble=0):
    truth_set = set(truth_ids)
    filtered = [x for x in player_ids if x in truth_set]  # ignore distractors
    L = lcs_len(filtered, truth_ids)
    base = (L / len(truth_ids)) if truth_ids else 0.0
    penalty = 0.05 * distractor_ids_in_assemble
    return max(0.0, min(1.0, base - penalty))

def run_score(tests_passed, total_tests):
    return 0.0 if total_tests == 0 else min(1.0, max(0.0), tests_passed / total_tests)

def time_bonus(elapsed_ms, round_ms):
    return max(0.0, 1.0 - (elapsed_ms / round_ms)) if round_ms > 0 else 0.0

def compute_final(build, run, tbonus, attempts=0, hints=0, err_runs=0, extra_distractors=0):
    penalties = 0.02 * attempts + 0.05 * hints + 0.01 * err_runs + 0.03 * extra_distractors
    val = 1000 * (0.40 * build + 0.50 * run + 0.10 * tbonus - penalties)
    return max(0, int(round(val)))

# ---------- main ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame x LeetCode — Blocks")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big = pygame.font.SysFont(None, 36)
    mono = pygame.font.SysFont("consolas", 18)

    # layout
    right_rect = pygame.Rect(LEFT_W + PADDING, 90, WIDTH - LEFT_W - PADDING * 2, HEIGHT - 120)
    left_panel_rect = pygame.Rect(32, 90, LEFT_W - PADDING * 2, HEIGHT - 120)

    board = SnippetBoard(left_panel_rect, right_rect, font, big, mono)

    # default slug so Blocks mode isn't empty at boot
    current_slug = "two-sum"
    board.load_puzzle(SNIPPET_PUZZLES.get(current_slug))

    last_verdict = ""
    loading = False
    last_action = "Snippet mode"
    last_meta = None
    last_error = None

    api = LCClient()
    q = queue.Queue()
    sample_slugs = [
        "two-sum",
        "add-two-numbers",
        "longest-substring-without-repeating-characters",
    ]
    slug_idx = 0
    mode = "blocks"

    def fetch_async(callable_, *args):
        nonlocal loading, last_error
        loading = True
        last_error = None
        threading.Thread(target=worker, args=(callable_, args, q), daemon=True).start()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_p:
                    slug = sample_slugs[slug_idx % len(sample_slugs)]
                    slug_idx += 1
                    last_action = f"Fetching /problem/{slug} …"
                    fetch_async(api.problem_meta, slug)
                elif e.key == pygame.K_b:
                    mode = "blocks"
                    if not board.palette:
                        board.load_puzzle(SNIPPET_PUZZLES.get(current_slug) or SNIPPET_PUZZLES.get("two-sum"))
                    last_action = "Snippet mode"

            # shared run callback (returns res dict)
            def _on_run(code_text: str):
                nonlocal last_verdict, current_slug, slug_idx
                slug = current_slug or (sample_slugs[(slug_idx - 1) % len(sample_slugs)] if slug_idx else "two-sum")
                if local_run:
                    res = local_run(slug, code_text)
                    if res.get("ok"):
                        last_verdict = f"✅ Passed {res.get('passed', 0)}/{res.get('total', 0)}"
                    else:
                        last_verdict = f"❌ {res.get('message') or 'Failed'}"
                    return res
                else:
                    # no judge available
                    return None

            # forward input
            board.handle_event(e, on_run=_on_run)

        # fetch results from LCClient
        try:
            status, payload_or_err = q.get_nowait()
            loading = False
            if status == "ok":
                last_meta = payload_or_err
                last_error = None
                title = last_meta.get("title") or "(no title)"
                diff = last_meta.get("difficulty") or "?"
                last_action = f"Loaded ✓  {title} [{diff}]"
                current_slug = last_meta.get("slug") or current_slug
                # Update blocks puzzle for this slug (fallback to two-sum)
                board.load_puzzle(SNIPPET_PUZZLES.get(current_slug) or SNIPPET_PUZZLES.get("two-sum"))
            else:
                last_error = payload_or_err
                last_meta = None
                last_action = "Error ✗  see message below"
        except queue.Empty:
            pass

        # ---- draw ----
        screen.fill(BG)
        screen.blit(big.render("Pygame + LeetCode API", True, FG), (PADDING, 20))
        mode_label = f"Mode: {mode == 'blocks'}"
        screen.blit(
            font.render("Controls: [P] Next • [B] Blocks • Ctrl/Cmd+Enter Run • [Esc] Quit", True, MUTED),
            (PADDING, 48),
        )
        top_status = f"{mode_label}   •   Status: {last_action}" + (
            f"   •   Judge: {last_verdict}" if last_verdict else ""
        )
        screen.blit(
            font.render(top_status, True, ACCENT if ("Loaded" in last_action or "✅" in last_verdict) else FG),
            (PADDING, 72),
        )
        board.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
