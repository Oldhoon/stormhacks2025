import pygame, threading, queue
from api import LCClient

WIDTH, HEIGHT = 900, 600
BG = (18, 18, 20)
FG = (230, 230, 235)
MUTED = (170, 170, 180)
ACCENT = (120, 180, 255)

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame x LeetCode API demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big  = pygame.font.SysFont(None, 36)
    mono = pygame.font.SysFont("consolas", 18)

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
            else:
                last_error = payload_or_err
                last_meta = None
                last_action = "Error ✗  see message below"
        except queue.Empty:
            pass

        # draw UI
        screen.fill(BG)
        screen.blit(big.render("Pygame + LeetCode API", True, FG), (24, 20))
        screen.blit(font.render("Controls: [P] Problem   [Esc] Quit", True, MUTED), (24, 66))
        screen.blit(font.render(f"Status: {last_action}", True, ACCENT if "Loaded" in last_action else FG), (24, 100))

        y = 140
        if loading:
            screen.blit(font.render("Loading…", True, FG), (24, y))
            y += 30

        if last_error:
            y = draw_wrapped(screen, str(last_error), font, (255,120,120), 24, y, WIDTH-48)

        if last_meta:
            title = last_meta.get("title") or ""
            diff  = last_meta.get("difficulty") or ""
            tags  = ", ".join(last_meta.get("tags", [])) or "-"
            url   = last_meta.get("url") or ""

            screen.blit(big.render(title, True, FG), (24, y)); y += 40
            y = draw_wrapped(screen, f"Difficulty: {diff}", font, MUTED, 24, y, WIDTH-48)
            y = draw_wrapped(screen, f"Tags: {tags}", font, MUTED, 24, y, WIDTH-48)
            y = draw_wrapped(screen, f"URL: {url}", font, MUTED, 24, y, WIDTH-48)
            y += 10

            text = (last_meta.get("text") or "")[:2000]  # show first ~2k chars
            if text:
                y = draw_wrapped(screen, text, mono, FG, 24, y, WIDTH-48, line_h=mono.get_height()+2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
