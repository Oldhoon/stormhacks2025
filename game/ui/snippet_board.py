# game/ui/snippet_board.py
import pygame
import random
from ..config import FG, ACCENT, ERR


class _Block:
    def __init__(self, text, uid):
        self.text = text
        self.uid = uid
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.is_dragging = False

    def _wrap_text(self, font, text, max_w):
        words = text.split(" ")
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                # break very long tokens
                while font.size(w)[0] > max_w and len(w) > 1:
                    lo, hi = 1, len(w)
                    cut = 1
                    while lo <= hi:
                        mid = (lo + hi) // 2
                        if font.size(w[:mid])[0] <= max_w:
                            cut = mid
                            lo = mid + 1
                        else:
                            hi = mid - 1
                    lines.append(w[:cut])
                    w = w[cut:]
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def measure_height(self, font, w, pad=8, line_gap=2):
        text_w = max(0, w - pad * 2)
        lines = self._wrap_text(font, self.text, text_w)
        h = pad * 2 + len(lines) * font.get_height() + (len(lines) - 1) * line_gap
        return h, lines

    def draw(self, surf, x, y, w, font):
        pad = 8
        line_gap = 2
        h, lines = self.measure_height(font, w, pad, line_gap)
        self.rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, (45, 45, 55), self.rect, border_radius=8)
        pygame.draw.rect(surf, (60, 60, 75), self.rect, 2, border_radius=8)
        ty = y + pad
        for line in lines:
            txt = font.render(line, True, FG)
            surf.blit(txt, (x + pad, ty))
            ty += font.get_height() + line_gap
        return h + 6


class SnippetBoard:
    """Left panel that shows a palette of code lines and SUBMIT/RESET buttons (vertical reordering)."""

    def __init__(self, rect: pygame.Rect, fonts):
        self.left_rect = rect
        self.font, self.big, self.mono = fonts  # (regular, big, mono)

        self.title = "Snippet Palette"
        self.palette: list[_Block] = []

        # Buttons (bottom-left)
        self.submit_rect = pygame.Rect(self.left_rect.x + 12, self.left_rect.bottom - 44, 120, 34)
        self.reset_rect = pygame.Rect(self.submit_rect.right + 12, self.submit_rect.y, 120, 34)

        # scrolling
        self.scroll_y = 0
        self._max_scroll = 0
        self._content_h = 0
        self._list_top = self.left_rect.y + 50

        # drag state
        self._drag_block: _Block | None = None
        self._drag_cursor_y = 0
        self._drag_offset_y = 0
        self._smooth_top: float | None = None

        # insertion preview (slot index among "others" and its Y line)
        self._insert_slot: int | None = None  # 0..len(others)
        self._slot_line_y: int | None = None
        self._last_slot: int | None = None
        self._slot_hysteresis_px = 8  # px to move past a boundary before switching slots

    # ---------------- layout helpers ----------------

    def set_lines(self, lines: list[str], scramble: bool = False, seed: int | None = None):
        """Load blocks; optionally scramble right away (use seed for deterministic per-question order)."""
        blocks = [_Block(t, f"b{i}") for i, t in enumerate(lines, 1)]
        if scramble:
            rnd = random.Random(seed)
            rnd.shuffle(blocks)
        self.palette = blocks
        self.scroll_y = 0
        # clear any drag state
        self._drag_block = None
        self._drag_cursor_y = 0
        self._drag_offset_y = 0
        self._smooth_top = None
        self._insert_slot = None
        self._slot_line_y = None
        self._last_slot = None

    def _layout(self):
        """Compute per-block layout (screen coords), honoring scroll."""
        inner_x = self.left_rect.x + 12
        inner_w = self.left_rect.w - 24
        y_left = self._list_top - self.scroll_y
        rows = []
        content_h = 0
        for b in self.palette:
            h, lines = b.measure_height(self.mono, inner_w, pad=8, line_gap=2)
            rows.append({"block": b, "top": y_left, "height": h, "lines": lines, "x": inner_x, "w": inner_w})
            y_left += h + 6
            content_h += h + 6
        if rows:
            content_h -= 6
        self._content_h = content_h
        viewport_h = self.submit_rect.y - self._list_top - 6
        self._max_scroll = max(0, self._content_h - viewport_h)
        self.scroll_y = max(0, min(self.scroll_y, self._max_scroll))
        return rows

    def _compute_slots(self, rows, exclude_block: _Block | None):
        """Compute insertion slot Y positions based on all OTHER rows (screen coords)."""
        others = [r for r in rows if r["block"] is not exclude_block]
        slots_y: list[int] = []
        if not others:
            # single slot: top of list area
            slots_y.append(self._list_top - self.scroll_y)
            return slots_y, others
        # before first
        slots_y.append(others[0]["top"])
        # between each pair (midpoint between bottom of a and top of b)
        for a, b in zip(others, others[1:]):
            a_bottom = a["top"] + a["height"]
            mid = (a_bottom + b["top"]) // 2
            slots_y.append(mid)
        # after last
        last = others[-1]
        slots_y.append(last["top"] + last["height"])
        return slots_y, others

    # ---------------- event handling ----------------

    def handle_event(self, e, on_submit=None, on_reset=None):
        if e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.left_rect.collidepoint((mx, my)) and self._max_scroll > 0:
                self.scroll_y = max(0, min(self._max_scroll, self.scroll_y - e.y * 40))
            return

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = e.pos
            if self.submit_rect.collidepoint(pos):
                code = "\n".join(b.text for b in self.palette) + "\n"
                if on_submit:
                    on_submit(code)
                return
            if self.reset_rect.collidepoint(pos):
                if on_reset:
                    on_reset()
                return

            # start drag on a block
            for row in self._layout():
                rect = pygame.Rect(row["x"], row["top"], row["w"], row["height"])
                if rect.collidepoint(pos):
                    b = row["block"]
                    self._drag_block = b
                    self._drag_cursor_y = pos[1]
                    self._drag_offset_y = pos[1] - row["top"]
                    self._smooth_top = float(row["top"])  # seed smoother
                    b.is_dragging = True
                    # prime insertion slot
                    self._insert_slot = None
                    self._slot_line_y = None
                    self._last_slot = None
                    return
            return

        if e.type == pygame.MOUSEMOTION and self._drag_block:
            self._drag_cursor_y = e.pos[1]
            return

        if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self._drag_block:
            b = self._drag_block
            # finalize: remove b, insert at computed slot among others
            if self._insert_slot is not None:
                others = [x for x in self.palette if x is not b]
                self.palette = others
                slot = max(0, min(self._insert_slot, len(self.palette)))
                self.palette.insert(slot, b)
            # clear drag state
            b.is_dragging = False
            self._drag_block = None
            self._drag_cursor_y = 0
            self._drag_offset_y = 0
            self._smooth_top = None
            self._insert_slot = None
            self._slot_line_y = None
            self._last_slot = None
            return

    # ---------------- per-frame update & draw ----------------

    def update(self, dt: float):
        """Per-frame drag follow + smoothing + stable insert-slot computation."""
        if not self._drag_block:
            return

        # follow mouse every frame
        self._drag_cursor_y = pygame.mouse.get_pos()[1]
        target_top = self._drag_cursor_y - self._drag_offset_y
        if self._smooth_top is None:
            self._smooth_top = float(target_top)
        else:
            self._smooth_top += (target_top - self._smooth_top) * 0.35  # 0.2–0.5 feels good

        rows = self._layout()

        # compute slots among OTHERS (exclude the dragged block)
        slots_y, _others = self._compute_slots(rows, exclude_block=self._drag_block)

        # decide which slot the ghost's CENTER belongs to
        inner_w = self.left_rect.w - 24
        h, _ = self._drag_block.measure_height(self.mono, inner_w, pad=8, line_gap=2)
        ghost_center_y = int(self._smooth_top) + h // 2

        # find first slot boundary strictly below the center
        slot_idx = 0
        while slot_idx < len(slots_y) and ghost_center_y > slots_y[slot_idx]:
            slot_idx += 1
        slot_idx = max(0, min(slot_idx, len(slots_y) - 1))
        boundary_y = slots_y[slot_idx]

        # hysteresis: only switch if we're sufficiently past the boundary
        if self._last_slot is None:
            self._last_slot = slot_idx
        else:
            if slot_idx != self._last_slot:
                if abs(ghost_center_y - boundary_y) <= self._slot_hysteresis_px:
                    slot_idx = self._last_slot  # hold previous slot near the line
                else:
                    self._last_slot = slot_idx

        self._insert_slot = slot_idx            # 0..len(others)
        self._slot_line_y = int(boundary_y)     # screen Y for guide line

        # optional: auto-scroll when dragging near edges
        EDGE = 32
        my = pygame.mouse.get_pos()[1]
        if my < self._list_top + EDGE and self.scroll_y > 0:
            self.scroll_y = max(0, self.scroll_y - 12)
        elif my > self.submit_rect.y - EDGE and self.scroll_y < self._max_scroll:
            self.scroll_y = min(self._max_scroll, self.scroll_y + 12)

    def draw(self, surf):
        # panel background & title
        pygame.draw.rect(surf, (28, 28, 36), self.left_rect, border_radius=12)
        surf.blit(self.big.render(self.title, True, FG), (self.left_rect.x + 12, self.left_rect.y + 10))

        rows = self._layout()

        # clip palette viewport
        viewport = pygame.Rect(
            self.left_rect.x + 6, self._list_top - 4, self.left_rect.w - 12, self.submit_rect.y - self._list_top
        )
        surf.set_clip(viewport)

        # draw static blocks (not the one being dragged)
        for row in rows:
            b = row["block"]
            if b is self._drag_block:
                continue
            y_left = row["top"]
            inner_x = row["x"]
            inner_w = row["w"]
            pad = 8
            line_gap = 2
            b.rect = pygame.Rect(inner_x, y_left, inner_w, row["height"])
            pygame.draw.rect(surf, (45, 45, 55), b.rect, border_radius=8)
            pygame.draw.rect(surf, (60, 60, 75), b.rect, 2, border_radius=8)
            ty = y_left + pad
            for line in row["lines"]:
                txt = self.mono.render(line, True, FG)
                surf.blit(txt, (inner_x + pad, ty))
                ty += self.mono.get_height() + line_gap

        # insertion guide line (stable, thick)
        if self._drag_block is not None and self._slot_line_y is not None:
            y = int(self._slot_line_y)
            pygame.draw.line(
                surf, ACCENT,
                (self.left_rect.x + 10, y),
                (self.left_rect.right - 10, y),
                width=3
            )

        # draw the dragged block following the smoothed top
        if self._drag_block is not None:
            b = self._drag_block
            inner_x = self.left_rect.x + 12
            inner_w = self.left_rect.w - 24
            h, lines = b.measure_height(self.mono, inner_w, pad=8, line_gap=2)
            y_top = int(self._smooth_top if self._smooth_top is not None else (self._drag_cursor_y - self._drag_offset_y))
            b.rect = pygame.Rect(inner_x, y_top, inner_w, h)
            pygame.draw.rect(surf, (70, 70, 90), b.rect, border_radius=8)  # slightly darker while dragging
            pygame.draw.rect(surf, ACCENT, b.rect, 2, border_radius=8)
            pad = 8
            ty = y_top + pad
            for line in lines:
                txt = self.mono.render(line, True, FG)
                surf.blit(txt, (inner_x + pad, ty))
                ty += self.mono.get_height() + 2

        surf.set_clip(None)

        # buttons
        pygame.draw.rect(surf, ACCENT, self.submit_rect, border_radius=8)
        surf.blit(self.big.render("SUBMIT", True, (10, 10, 15)), (self.submit_rect.x + 10, self.submit_rect.y + 4))

        pygame.draw.rect(surf, (45, 45, 55), self.reset_rect, border_radius=8)
        pygame.draw.rect(surf, ERR, self.reset_rect, 2, border_radius=8)
        surf.blit(self.big.render("RESET", True, ERR), (self.reset_rect.x + 16, self.reset_rect.y + 4))
