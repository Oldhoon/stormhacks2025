# game/editor.py
import pygame

FG = (230, 230, 235)
BG_PANEL = (24, 26, 32)
BG_CONTENT = (20, 22, 28)
HDR_BG = (28, 30, 36)
ACCENT = (120, 180, 255)
LN_NUM = (110, 120, 135)
CARET = (255, 220, 120)
BORDER = (60, 66, 80)
FOCUS_RING = (80, 180, 255)

class Editor:
    """
    - Click to focus
    - Typing, Enter, Backspace, Delete
    - Arrow keys, Home/End
    - Tab = 4 spaces, Shift+Tab = outdent up to 4
    - Mouse wheel scroll
    - Ctrl/Cmd + Enter triggers on_run(code_text) callback (if provided)
    """
    def __init__(self, rect: pygame.Rect, ui_font: pygame.font.Font, mono_font: pygame.font.Font, title="Editor"):
        self.rect = rect
        self.ui_font = ui_font
        self.mono = mono_font
        self.title = title

        self.lines = ["# Write your solution here"]
        self.caret_row = 0
        self.caret_col = len(self.lines[0])
        self.line_h = self.mono.get_height() + 4
        self.scroll_y = 0
        self.focus = False
        self.tab = "    "  # 4 spaces

    # ---------- external API ----------
    def set_title(self, s: str):
        self.title = s

    def set_text(self, s: str):
        self.lines = s.splitlines() or [""]
        self.caret_row = len(self.lines) - 1
        self.caret_col = len(self.lines[-1])
        self.scroll_y = 0

    def get_text(self) -> str:
        return "\n".join(self.lines)

    # ---------- internals: editing ops ----------
    def _insert(self, s: str):
        line = self.lines[self.caret_row]
        self.lines[self.caret_row] = line[:self.caret_col] + s + line[self.caret_col:]
        self.caret_col += len(s)

    def _newline(self):
        line = self.lines[self.caret_row]
        left, right = line[:self.caret_col], line[self.caret_col:]
        base_indent = len(left) - len(left.lstrip(" "))
        extra = 4 if left.rstrip().endswith(":") else 0  # tiny Python-aware indent
        self.lines[self.caret_row] = left
        self.lines.insert(self.caret_row + 1, " " * (base_indent + extra) + right)
        self.caret_row += 1
        self.caret_col = base_indent + extra

    def _backspace(self):
        if self.caret_col > 0:
            line = self.lines[self.caret_row]
            self.lines[self.caret_row] = line[:self.caret_col - 1] + line[self.caret_col:]
            self.caret_col -= 1
        elif self.caret_row > 0:
            prev_len = len(self.lines[self.caret_row - 1])
            self.lines[self.caret_row - 1] += self.lines[self.caret_row]
            del self.lines[self.caret_row]
            self.caret_row -= 1
            self.caret_col = prev_len

    def _delete(self):
        line = self.lines[self.caret_row]
        if self.caret_col < len(line):
            self.lines[self.caret_row] = line[:self.caret_col] + line[self.caret_col + 1:]
        elif self.caret_row < len(self.lines) - 1:
            self.lines[self.caret_row] += self.lines[self.caret_row + 1]
            del self.lines[self.caret_row + 1]

    def _move_to(self, row: int, col: int):
        self.caret_row = max(0, min(len(self.lines) - 1, row))
        self.caret_col = max(0, min(len(self.lines[self.caret_row]), col))

    def _ensure_visible(self):
        content_h = self.rect.h - 46  # header + padding
        row_top = self.caret_row * self.line_h
        row_bot = row_top + self.line_h
        if row_top < self.scroll_y:
            self.scroll_y = row_top
        elif row_bot > self.scroll_y + content_h:
            self.scroll_y = row_bot - content_h
        self.scroll_y = max(0, self.scroll_y)

    def _mouse_to_caret(self, pos):
        x, y = pos
        content_x = self.rect.x + 6 + 10 + 36  # panel pad + text pad + line# gutter
        content_y = self.rect.y + 36 + 4
        rel_y = y - content_y + self.scroll_y
        row = int(max(0, min(len(self.lines) - 1, rel_y // self.line_h)))

        rel_x = x - content_x
        col, acc = 0, 0
        s = self.lines[row]
        for i, ch in enumerate(s):
            w = self.mono.size(ch)[0]
            if acc + w / 2 >= rel_x:
                col = i
                break
            acc += w
            col = i + 1
        self._move_to(row, col)
        self._ensure_visible()

    # ---------- events ----------
    def handle_event(self, e: pygame.event.Event, on_run=None):
        if e.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(e.pos):
                self.focus = True
                self._mouse_to_caret(e.pos)
            else:
                self.focus = False
            return

        if not self.focus:
            return

        if e.type == pygame.MOUSEWHEEL:
            max_scroll = max(0, len(self.lines) * self.line_h - (self.rect.h - 46))
            self.scroll_y = max(0, min(max_scroll, self.scroll_y - e.y * 40))
            return

        if e.type == pygame.KEYDOWN:
            mod = pygame.key.get_mods()

            # Run: Ctrl/Cmd + Enter
            if (mod & (pygame.KMOD_CTRL | pygame.KMOD_META)) and e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if on_run:
                    on_run(self.get_text())
                return

            if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._newline()
            elif e.key == pygame.K_BACKSPACE:
                self._backspace()
            elif e.key == pygame.K_DELETE:
                self._delete()
            elif e.key == pygame.K_TAB:
                if mod & pygame.KMOD_SHIFT:
                    # outdent current line up to 4 spaces
                    line = self.lines[self.caret_row]
                    leading = len(line) - len(line.lstrip(" "))
                    rm = min(4, leading, self.caret_col)
                    if rm:
                        self.lines[self.caret_row] = line[:self.caret_col - rm] + line[self.caret_col:]
                        self.caret_col -= rm
                else:
                    self._insert(self.tab)
            elif e.key == pygame.K_LEFT:
                if self.caret_col > 0:
                    self._move_to(self.caret_row, self.caret_col - 1)
                elif self.caret_row > 0:
                    self._move_to(self.caret_row - 1, len(self.lines[self.caret_row - 1]))
            elif e.key == pygame.K_RIGHT:
                if self.caret_col < len(self.lines[self.caret_row]):
                    self._move_to(self.caret_row, self.caret_col + 1)
                elif self.caret_row < len(self.lines) - 1:
                    self._move_to(self.caret_row + 1, 0)
            elif e.key == pygame.K_UP:
                self._move_to(self.caret_row - 1, min(self.caret_col, len(self.lines[max(0, self.caret_row - 1)])))
            elif e.key == pygame.K_DOWN:
                self._move_to(self.caret_row + 1, min(self.caret_col, len(self.lines[min(len(self.lines) - 1, self.caret_row + 1)])))
            elif e.key == pygame.K_HOME:
                self._move_to(self.caret_row, 0)
            elif e.key == pygame.K_END:
                self._move_to(self.caret_row, len(self.lines[self.caret_row]))
            else:
                if e.unicode and e.unicode.isprintable():
                    self._insert(e.unicode)

            self._ensure_visible()

    # ---------- drawing ----------
    def draw(self, screen: pygame.Surface):
        # panel & header
        pygame.draw.rect(screen, BG_PANEL, self.rect, border_radius=8)
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 32)
        pygame.draw.rect(screen, HDR_BG, header, border_radius=8)
        screen.blit(self.ui_font.render(self.title + "  (Ctrl/Cmd+Enter to Run)", True, ACCENT),
                    (self.rect.x + 10, self.rect.y + 7))

        # content box
        content = pygame.Rect(self.rect.x + 6, self.rect.y + 36, self.rect.w - 12, self.rect.h - 42)
        pygame.draw.rect(screen, BG_CONTENT, content, border_radius=6)

        y = content.y - self.scroll_y
        x_text = content.x + 10 + 36  # + line number gutter

        # visible lines range
        first = max(0, self.scroll_y // self.line_h)
        last = min(len(self.lines), first + (content.h // self.line_h) + 2)

        for i in range(first, last):
            ln = self.lines[i]
            # line numbers
            ln_surf = self.ui_font.render(str(i + 1).rjust(3), True, LN_NUM)
            screen.blit(ln_surf, (content.x + 6, y))
            # text
            screen.blit(self.mono.render(ln, True, FG), (x_text, y))
            y += self.line_h

        # caret
        caret_x = x_text + self.mono.size(self.lines[self.caret_row][:self.caret_col])[0]
        caret_y = content.y + (self.caret_row * self.line_h) - self.scroll_y
        if self.focus and content.y <= caret_y <= content.bottom - self.line_h + 2:
            pygame.draw.line(screen, CARET, (caret_x, caret_y), (caret_x, caret_y + self.line_h - 3), 2)

        # borders
        pygame.draw.rect(screen, BORDER, self.rect, width=2, border_radius=8)
        if self.focus:
            pygame.draw.rect(screen, FOCUS_RING, self.rect.inflate(6, 6), width=2, border_radius=10)