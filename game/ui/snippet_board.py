# game/ui/snippet_board.py
import pygame
from ..config import FG, ACCENT, ERR

class _Block:
    def __init__(self, text, uid):
        self.text = text
        self.uid = uid
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.is_dragging = False

    def _wrap_text(self, font, text, max_w):
        words = text.split(' ')
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                # break long tokens if needed
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
    """Left panel that shows a palette of code lines and SUBMIT/RESET buttons."""
    def __init__(self, rect: pygame.Rect, fonts):
        self.left_rect = rect
        self.font, self.big, self.mono = fonts  # (regular, big, mono)

        self.title = "Snippet Palette"
        self.palette = []  # list[_Block]

        # Buttons (bottom-left)
        self.submit_rect = pygame.Rect(self.left_rect.x + 12, self.left_rect.bottom - 44, 120, 34)
        self.reset_rect  = pygame.Rect(self.submit_rect.right + 12, self.submit_rect.y, 120, 34)

        # scrolling for tall palettes
        self.scroll_y = 0
        self._max_scroll = 0
        self._content_h = 0

        self._list_top = self.left_rect.y + 50

        # drag state for reordering within the left list
        self._drag_block = None          # _Block currently being dragged
        self._drag_start_idx = None      # original index in self.palette
        self._drag_cursor_y = 0          # current mouse Y (for rendering)
        self._drag_offset_y = 0          # offset from block top to mouse
        self._insert_idx = None          # where the block would be inserted

    def set_lines(self, lines: list[str]):
        self.palette = [_Block(t, f"b{i}") for i, t in enumerate(lines, 1)]
        self.scroll_y = 0

    def _layout(self):
        """Compute layout for current palette given scroll and width.
        Returns a list of dicts: {'block': b, 'top': y, 'height': h, 'lines': lines}
        """
        inner_x = self.left_rect.x + 12
        inner_w = self.left_rect.w - 24
        y_left = self._list_top - self.scroll_y
        rows = []
        content_h = 0
        for b in self.palette:
            h, lines = b.measure_height(self.mono, inner_w, pad=8, line_gap=2)
            rows.append({'block': b, 'top': y_left, 'height': h, 'lines': lines, 'x': inner_x, 'w': inner_w})
            y_left += h + 6
            content_h += h + 6
        if rows:
            content_h -= 6
        self._content_h = content_h
        viewport_h = self.submit_rect.y - self._list_top - 6
        self._max_scroll = max(0, self._content_h - viewport_h)
        self.scroll_y = max(0, min(self.scroll_y, self._max_scroll))
        return rows

    def handle_event(self, e, on_submit=None, on_reset=None):
        # Scroll with wheel when cursor is inside the left panel
        if e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.left_rect.collidepoint((mx, my)) and self._max_scroll > 0:
                self.scroll_y = max(0, min(self._max_scroll, self.scroll_y - e.y * 40))
            return

        # Mouse down: check buttons first, then start drag if clicked on a block
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

            # Hit-test blocks for drag start
            for row in self._layout():
                b = row['block']
                rect = pygame.Rect(row['x'], row['top'], row['w'], row['height'])
                if rect.collidepoint(pos):
                    self._drag_block = b
                    self._drag_start_idx = self.palette.index(b)
                    self._drag_cursor_y = pos[1]
                    self._drag_offset_y = pos[1] - row['top']
                    self._insert_idx = self._drag_start_idx
                    b.is_dragging = True
                    return
            return

        # Mouse move: update drag cursor and compute tentative insertion index
        if e.type == pygame.MOUSEMOTION and self._drag_block:
            self._drag_cursor_y = e.pos[1]
            # compute insert index based on current cursor Y
            rows = self._layout()
            idx = 0
            for i, row in enumerate(rows):
                mid = row['top'] + row['height'] // 2
                if self._drag_cursor_y - self._drag_offset_y < mid:
                    idx = i
                    break
                idx = i + 1
            # when dragging, the list temporarily behaves as if the block was removed
            if self._drag_start_idx is not None and idx > self._drag_start_idx:
                idx -= 1
            self._insert_idx = max(0, min(len(self.palette) - 1, idx))
            return

        # Mouse up: perform reorder if dragging
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self._drag_block:
            b = self._drag_block
            old = self._drag_start_idx
            new = self._insert_idx if self._insert_idx is not None else old
            # remove and insert
            if old is not None:
                self.palette.pop(old)
                self.palette.insert(new, b)
            # clear drag state
            b.is_dragging = False
            self._drag_block = None
            self._drag_start_idx = None
            self._drag_cursor_y = 0
            self._drag_offset_y = 0
            self._insert_idx = None
            return

    def draw(self, surf):
        # panel and title
        pygame.draw.rect(surf, (28, 28, 36), self.left_rect, border_radius=12)
        surf.blit(self.big.render(self.title, True, FG), (self.left_rect.x + 12, self.left_rect.y + 10))

        rows = self._layout()

        viewport = pygame.Rect(self.left_rect.x + 6, self._list_top - 4, self.left_rect.w - 12, self.submit_rect.y - self._list_top)
        surf.set_clip(viewport)

        # draw static blocks (skip the one being dragged)
        for row in rows:
            b = row['block']
            if b is self._drag_block:
                continue
            y_left = row['top']
            inner_x = row['x']
            inner_w = row['w']
            # draw block using existing _Block API but with precomputed height/lines
            pad = 8
            line_gap = 2
            b.rect = pygame.Rect(inner_x, y_left, inner_w, row['height'])
            pygame.draw.rect(surf, (45, 45, 55), b.rect, border_radius=8)
            pygame.draw.rect(surf, (60, 60, 75), b.rect, 2, border_radius=8)
            ty = y_left + pad
            for line in row['lines']:
                txt = self.mono.render(line, True, FG)
                surf.blit(txt, (inner_x + pad, ty))
                ty += self.mono.get_height() + line_gap

        # insertion guide line
        if self._drag_block is not None and self._insert_idx is not None:
            # find Y for the insert line relative to rows (simulate position)
            if not rows:
                guide_y = self._list_top - self.scroll_y
            elif self._insert_idx <= 0:
                guide_y = rows[0]['top']
            elif self._insert_idx >= len(rows):
                last = rows[-1]
                guide_y = last['top'] + last['height'] + 3
            else:
                prev = rows[self._insert_idx - 1]
                guide_y = prev['top'] + prev['height'] + 3
            pygame.draw.line(surf, ACCENT, (self.left_rect.x + 10, guide_y), (self.left_rect.right - 10, guide_y), 2)

        # draw the dragged block following the cursor
        if self._drag_block is not None:
            b = self._drag_block
            inner_x = self.left_rect.x + 12
            inner_w = self.left_rect.w - 24
            # measure to get height and lines for this block
            h, lines = b.measure_height(self.mono, inner_w, pad=8, line_gap=2)
            y_top = self._drag_cursor_y - self._drag_offset_y
            b.rect = pygame.Rect(inner_x, y_top, inner_w, h)
            # semi-transparent look while dragging
            pygame.draw.rect(surf, (70, 70, 90), b.rect, border_radius=8)
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