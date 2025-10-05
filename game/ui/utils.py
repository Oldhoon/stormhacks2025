import threading

def worker(fn, args, outq):
    """Run blocking fn(*args) in a background thread and push ('ok'| 'err', payload) into outq."""
    def _run():
        try:
            result = fn(*args)
            outq.put(("ok", result))
        except Exception as e:
            outq.put(("err", str(e)))
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t

def measure_wrapped(text, font, max_w, line_h=None):
    if not text:
        return 0
    words = text.split()
    line = ""
    h = 0
    lh = line_h or (font.get_height() + 2)
    for w in words:
        test = f"{line} {w}".strip()
        if font.size(test)[0] <= max_w:
            line = test
        else:
            h += lh
            line = w
    if line:
        h += lh
    return h

def draw_wrapped(surface, text, font, color, x, y, max_w, line_h=None):
    """Render wrapped text; return the next y."""
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