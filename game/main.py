# main.py
import pygame
import threading
import queue
import random

# ---------- optional integrations you already have ----------
try:
    from .api import LCClient
    from .editor import Editor
except ImportError:
    from api import LCClient
    from editor import Editor

try:
    from local_cli.judge_cli import run_local as local_run
except Exception:
    local_run = None  # optional local judge
# ------------------------------------------------------------

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

# ---------- starter templates for Editor mode ----------
STARTERS = {
    "two-sum": """from typing import List

def twoSum(nums: List[int], target: int):
    # Your code here
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []
""",
    "add-two-numbers": """# Adjust signature to your judge
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
def addTwoNumbers(l1, l2):
    carry = 0
    dummy = ListNode()
    tail = dummy
    while l1 or l2 or carry:
        v = (l1.val if l1 else 0) + (l2.val if l2 else 0) + carry
        carry, d = divmod(v, 10)
        tail.next = ListNode(d); tail = tail.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    return dummy.next
""",
}
def starter_for(slug: str) -> str:
    return STARTERS.get(slug, "# Write your solution here\n")

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
            "    nums.sort()  # red herring",
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
    """Left panel = palette (ordered lines). Dragging from palette removes it there.
       Drop into the right panel to insert; dropping elsewhere cancels and returns it."""
    def __init__(self, left_rect: pygame.Rect, right_rect: pygame.Rect, font, big, mono):
        self.left_rect = left_rect
        self.right_rect = right_rect
        self.font, self.big, self.mono = font, big, mono
        self.btn_rect = pygame.Rect(self.right_rect.left, self.right_rect.bottom - 44, 130, 34)

        self.palette = []
        self.assemble = []
        self.title = "Snippet Puzzle"
        self.template_preamble = ""
        self.entrypoint = ""
        self.status = "Drag lines to the right. Press CHECK."

        # drag state
        self._drag = None
        self._insert_idx = None
        self._drag_from = None              # 'palette' or 'assemble'
        self._drag_from_index = None        # original index in its source list

        # truth / scoring
        self.truth_ids = []
        self.distractor_ids = set()
        self.attempts = 0
        self.err_runs = 0
        self.tests_passed = 0
        self.tests_total = 0
        self.round_ms = 120_000
        self.start_ticks = pygame.time.get_ticks()

        # reveal score only after a successful submission
        self.show_score = False
        self.last_build = 0.0
        self.last_run = 0.0
        self.last_final = 0
        self.last_tbon = 0.0
        self.last_distractors = 0

    def load_puzzle(self, puzzle: dict | None):
        self.palette, self.assemble = [], []
        self.status = "Drag lines to the right. Press CHECK."
        if not puzzle:
            self.title = "No puzzle available for this problem"
            self.template_preamble = ""
            self.entrypoint = ""
            self.truth_ids = []
            self.distractor_ids = set()
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

    def handle_event(self, e, on_run=None):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = e.pos
            # hit-test palette first, then assemble
            for src_name, lst in (("palette", self.palette), ("assemble", self.assemble)):
                for i, b in enumerate(lst):
                    if b.rect.collidepoint(pos):
                        self._drag = b
                        b.dragging = True
                        b.offset = (pos[0] - b.rect.x, pos[1] - b.rect.y)
                        self._drag_from = src_name
                        self._drag_from_index = i
                        # ONE-WAY MOVE: remove immediately from its source list
                        lst.pop(i)
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
                    if isinstance(res, dict):
                        if not res.get("ok"):
                            self.err_runs += 1
                            self.status = res.get("message") or "Run failed."
                            self.show_score = False  # don't reveal on failed runs
                        else:
                            self.tests_passed = res.get("passed", 0)
                            self.tests_total = res.get("total", 0)

                            # compute & cache score ONLY NOW (after a real run)
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

                            if self.tests_total and self.tests_passed == self.tests_total:
                                self.status = "All tests passed! 🎉"
                            else:
                                self.status = f"Passed {self.tests_passed}/{self.tests_total} tests"
                    else:
                        self.status = "Submitted."
                        self.show_score = False
                return

        if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self._drag:
            pos = e.pos
            # drop into assemble
            if self.right_rect.collidepoint(pos):
                y = pos[1] - (self.right_rect.y + 56)
                idx = max(0, min(len(self.assemble), y // 36))
                self.assemble.insert(int(idx), self._drag)
            else:
                # cancel → put back where it came from
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
            self._drag_from = None
            self._drag_from_index = None
            return

        if e.type == pygame.MOUSEMOTION and self._drag:
            mx, my = e.pos
            self._drag.rect.topleft = (mx - self._drag.offset[0], my - self._drag.offset[1])
            if self.right_rect.collidepoint(e.pos):
                y = my - (self.right_rect.y + 56)
                self._insert_idx = max(0, min(len(self.assemble), y // 36))
            else:
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
        y = self.left_rect.y + 50
        for b in self.palette:
            y += b.draw(surf, self.left_rect.x + 12, y, self.left_rect.w - 24, self.mono, active=False)

        # assemble
        y2 = self.right_rect.y + 56
        if self._insert_idx is not None:
            y_line = y2 + self._insert_idx * 36
            pygame.draw.line(surf, ACCENT, (self.right_rect.x + 10, y_line), (self.right_rect.right - 10, y_line), 2)
        for b in self.assemble:
            y2 += b.draw(surf, self.right_rect.x + 12, y2, self.right_rect.w - 24, self.mono, active=False)

        # dragging on top
        if self._drag:
            self._drag.draw(surf, self._drag.rect.x, self._drag.rect.y, self._drag.rect.w, self.mono, active=True)

        # check button
        pygame.draw.rect(surf, ACCENT, self.btn_rect, border_radius=8)
        surf.blit(self.big.render("CHECK", True, (10, 10, 15)), (self.btn_rect.x + 14, self.btn_rect.y + 4))

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
            hint = "Press CHECK to see score"
            surf.blit(self.font.render(hint, True, MUTED), (self.right_rect.right - 240, self.right_rect.y + 8))

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
    return 0.0 if total_tests == 0 else min(1.0, max(0.0, tests_passed / total_tests))

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
    pygame.display.set_caption("Pygame x LeetCode — Editor & Blocks")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big = pygame.font.SysFont(None, 36)
    mono = pygame.font.SysFont("consolas", 18)

    # layout
    right_rect = pygame.Rect(LEFT_W + PADDING, 70, WIDTH - LEFT_W - PADDING * 2, HEIGHT - 86)
    left_panel_rect = pygame.Rect(PADDING, 70, LEFT_W - PADDING * 2, HEIGHT - 86)

    editor = Editor(right_rect, font, mono, title="Editor")
    board = SnippetBoard(left_panel_rect, right_rect, font, big, mono)

    # default slug so Blocks mode isn't empty at boot
    current_slug = "two-sum"
    editor.set_text(starter_for(current_slug))
    board.load_puzzle(SNIPPET_PUZZLES.get(current_slug))

    last_verdict = ""
    loading = False
    last_action = "Controls: [P] Next • [B] Blocks • [E] Editor • Esc Quit"
    last_meta = None
    last_error = None

    api = LCClient()  # your backend; defaults as you implemented
    q = queue.Queue()
    sample_slugs = [
        "two-sum",
        "add-two-numbers",
        "longest-substring-without-repeating-characters",
    ]
    slug_idx = 0
    mode = "editor"  # or "blocks"

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
                elif e.key == pygame.K_e:
                    mode = "editor"
                    last_action = "Editor mode"

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
                    print("RUN (no local judge wired) — first 500 chars:\n", code_text[:500])
                    return None

            # forward input
            if mode == "editor":
                editor.handle_event(e, on_run=_on_run)
            else:
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
                editor.set_title(f"Editor — {title}")
                editor.set_text(starter_for(current_slug or ""))

                # load a blocks puzzle for this slug (if exists)
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
        mode_label = f"Mode: {'Blocks' if mode == 'blocks' else 'Editor'}"
        screen.blit(
            font.render("Controls: [P] Next • [B] Blocks • [E] Editor • Ctrl/Cmd+Enter Run • [Esc] Quit", True, MUTED),
            (PADDING, 48),
        )
        top_status = f"{mode_label}   •   Status: {last_action}" + (
            f"   •   Judge: {last_verdict}" if last_verdict else ""
        )
        screen.blit(
            font.render(top_status, True, ACCENT if ("Loaded" in last_action or "✅" in last_verdict) else FG),
            (PADDING, 72),
        )

        if mode == "editor":
            # left metadata panel
            y = 120
            x0 = PADDING
            max_w = LEFT_W - PADDING * 2
            if loading:
                screen.blit(font.render("Loading…", True, FG), (x0, y))
                y += 30
            if last_error:
                y = draw_wrapped(screen, str(last_error), font, ERR, x0, y, max_w)
            if last_meta:
                title = last_meta.get("title") or ""
                diff = last_meta.get("difficulty") or ""
                tags = ", ".join(last_meta.get("tags", [])) or "-"
                url = last_meta.get("url") or ""
                screen.blit(big.render(title, True, FG), (x0, y)); y += 40
                y = draw_wrapped(screen, f"Difficulty: {diff}", font, MUTED, x0, y, max_w)
                y = draw_wrapped(screen, f"Tags: {tags}", font, MUTED, x0, y, max_w)
                y = draw_wrapped(screen, f"URL: {url}", font, MUTED, x0, y, max_w)
                y += 10
                text = (last_meta.get("text") or "")[:2000]
                if text:
                    y = draw_wrapped(screen, text, mono, FG, x0, y, max_w, line_h=mono.get_height() + 2)
            # right: code editor
            editor.draw(screen)
        else:
            # Blocks mode draws both panels internally
            board.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
