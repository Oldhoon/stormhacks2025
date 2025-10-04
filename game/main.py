import pygame, threading, queue
try:
    from .api import LCClient
    from .editor import Editor
except ImportError:
    # allow running as a script from inside game/
    from api import LCClient
    from editor import Editor
try:
    from local_cli.judge_cli import run_local as local_run
except Exception:
    local_run = None  # optional local judge

WIDTH, HEIGHT = 900, 600
BG = (18, 18, 20)
FG = (230, 230, 235)
MUTED = (170, 170, 180)
ACCENT = (120, 180, 255)
ERR = (255, 120, 120)
PADDING = 16
LEFT_W = int(WIDTH * 0.52)

def worker(fn, args, outq):
    try:
        result = fn(*args)
        outq.put(("ok", result))
    except Exception as e:
        outq.put(("err", str(e)))

def draw_wrapped(surface, text, font, color, x, y, max_w, line_h=None):
    if not text: return y
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

STARTERS = {
    "two-sum": """def twoSum(nums, target):
    # Your code here
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame x LeetCode API demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big  = pygame.font.SysFont(None, 36)
    mono = pygame.font.SysFont("consolas", 18)

    # layout for split view
    left_max_w = LEFT_W - PADDING * 2
    left_x = PADDING
    left_y0 = 120  # left column starts a bit lower
    right_rect = pygame.Rect(LEFT_W + PADDING, 70, WIDTH - LEFT_W - PADDING * 2, HEIGHT - 86)

    editor = Editor(right_rect, font, mono, title="Editor")
    current_slug = None
    last_verdict = ""

    api = LCClient()  # http://localhost:8000 by default
    q = queue.Queue()
    loading = False
    last_action = "Controls:  [P] Problem   [Esc] Quit"
    last_meta = None
    last_error = None
    sample_slugs = [
        "two-sum",
        "add-two-numbers",
        "longest-substring-without-repeating-characters",
    ]
    slug_idx = 0

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
                    # use parsed helper
                    fetch_async(api.problem_meta, slug)
            # ---- Editor: run callback + event forwarding ----
            if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.MOUSEMOTION:
                def _on_run(code_text: str):
                    nonlocal last_verdict, current_slug, slug_idx
                    # use current slug if known, else fall back to last selected sample or two-sum
                    slug = current_slug or (sample_slugs[(slug_idx-1) % len(sample_slugs)] if slug_idx else "two-sum")
                    if local_run:
                        res = local_run(slug, code_text)
                        if res.get("ok"):
                            last_verdict = f"✅ Passed {res.get('passed',0)}/{res.get('total',0)}"
                        else:
                            last_verdict = f"❌ {res.get('message') or 'Failed'}"
                    else:
                        print("RUN (no local judge wired) — first 500 chars:\n", code_text[:500])

                editor.handle_event(e, on_run=_on_run)

        # collect results (non-blocking)
        try:
            status, payload_or_err = q.get_nowait()
            loading = False
            if status == "ok":
                last_meta = payload_or_err  # already parsed
                last_error = None
                title = last_meta.get("title") or "(no title)"
                diff = last_meta.get("difficulty") or "?"
                last_action = f"Loaded ✓  {title} [{diff}]"
                current_slug = last_meta.get("slug") or current_slug
                editor.set_title(f"Editor — {title}")
                editor.set_text(starter_for(current_slug or ""))
            else:
                last_error = payload_or_err
                last_meta = None
                last_action = "Error ✗  see message below"
        except queue.Empty:
            pass

        # draw UI
        screen.fill(BG)
        screen.blit(big.render("Pygame + LeetCode API", True, FG), (PADDING, 20))
        screen.blit(font.render("Controls: [P] Next Problem • Click editor to focus • Ctrl/Cmd+Enter to Run • [Esc] Quit", True, MUTED), (PADDING, 48))
        top_status = f"Status: {last_action}" + (f"   •   Judge: {last_verdict}" if last_verdict else "")
        screen.blit(font.render(top_status, True, ACCENT if ("Loaded" in last_action or "✅" in last_verdict) else FG), (PADDING, 72))

        y = left_y0
        x0 = left_x
        max_w = left_max_w
        if loading:
            screen.blit(font.render("Loading…", True, FG), (x0, y))
            y += 30

        if last_error:
            y = draw_wrapped(screen, str(last_error), font, (255,120,120), x0, y, max_w)

        if last_meta:
            title = last_meta.get("title") or ""
            diff  = last_meta.get("difficulty") or ""
            tags  = ", ".join(last_meta.get("tags", [])) or "-"
            url   = last_meta.get("url") or ""

            screen.blit(big.render(title, True, FG), (x0, y)); y += 40
            y = draw_wrapped(screen, f"Difficulty: {diff}", font, MUTED, x0, y, max_w)
            y = draw_wrapped(screen, f"Tags: {tags}", font, MUTED, x0, y, max_w)
            y = draw_wrapped(screen, f"URL: {url}", font, MUTED, x0, y, max_w)
            y += 10

            text = (last_meta.get("text") or "")[:2000]  # show first ~2k chars
            if text:
                y = draw_wrapped(screen, text, mono, FG, x0, y, max_w, line_h=mono.get_height()+2)

        # draw editor panel on the right
        editor.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
