# game/main.py
import pygame, threading, queue, json
from api import LCClient

WIDTH, HEIGHT = 900, 600
BG = (18, 18, 20)
FG = (230, 230, 235)
MUTED = (170, 170, 180)
ACCENT = (120, 180, 255)

def shorten(obj, n=300):
    s = json.dumps(obj, ensure_ascii=False)
    return s[:n] + ("…" if len(s) > n else "")

def try_get_title(payload):
    # Best-effort extraction across different shapes
    for key in ("title", "questionTitle", "question"):
        cur = payload.get(key) if isinstance(payload, dict) else None
        if isinstance(cur, dict) and "title" in cur:
            return cur.get("title")
        if isinstance(cur, str):
            return cur
    # sometimes payload has 'data' wrapper
    if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict):
        return try_get_title(payload["data"])
    return None

def worker(fn, args, outq):
    try:
        result = fn(*args)
        outq.put(("ok", result))
    except Exception as e:
        outq.put(("err", str(e)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame x LeetCode API demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big  = pygame.font.SysFont(None, 36)
    mono = pygame.font.SysFont("consolas", 18)

    api = LCClient()  # uses http://localhost:8000 by default
    q = queue.Queue()
    loading = False
    last_action = "Press D for Daily, P for Problem, U for User"
    last_payload = None
    last_error = None
    sample_slugs = ["two-sum", "add-two-numbers", "longest-substring-without-repeating-characters"]
    slug_idx = 0
    username = "lee215"  # change to your LC username if you want

    def fetch_async(callable_, *args):
        nonlocal loading, last_error, last_action
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
                elif e.key == pygame.K_d:
                    last_action = "Fetching /daily …"
                    fetch_async(api.get_daily)
                elif e.key == pygame.K_p:
                    slug = sample_slugs[slug_idx % len(sample_slugs)]
                    slug_idx += 1
                    last_action = f"Fetching /problem/{slug} …"
                    fetch_async(api.get_problem, slug)
                elif e.key == pygame.K_u:
                    last_action = f"Fetching /user/{username} …"
                    fetch_async(api.get_user, username)

        # collect results without blocking render
        try:
            status, payload_or_err = q.get_nowait()
            loading = False
            if status == "ok":
                last_payload = payload_or_err
                last_error = None
                title = try_get_title(last_payload) or "(no title field)"
                last_action = f"Loaded ✓  {title}"
            else:
                last_error = payload_or_err
                last_payload = None
                last_action = "Error ✗  see message below"
        except queue.Empty:
            pass

        # draw
        screen.fill(BG)
        screen.blit(big.render("Pygame + LeetCode API", True, FG), (24, 20))
        screen.blit(font.render("Controls: [D] Daily   [P] Problem   [U] User   [Esc] Quit", True, MUTED), (24, 66))
        screen.blit(font.render(f"Status: {last_action}", True, ACCENT if "Loaded" in last_action else FG), (24, 100))

        y = 140
        if loading:
            screen.blit(font.render("Loading…", True, FG), (24, y))
            y += 30

        if last_error:
            for line in [last_error[i:i+90] for i in range(0, len(last_error), 90)]:
                screen.blit(font.render(line, True, (255, 120, 120)), (24, y))
                y += 24

        if last_payload:
            # show a compact JSON preview
            preview = shorten(last_payload, 1200)
            for line in [preview[i:i+110] for i in range(0, len(preview), 110)]:
                screen.blit(mono.render(line, True, FG), (24, y))
                y += 20

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
