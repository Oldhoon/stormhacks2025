import pygame
from .utils import measure_wrapped
from ..config import FG, MUTED, ACCENT

def split_problem_text(text: str):
    if not text:
        return {"desc": "", "examples": "", "constraints": ""}

    t = text.replace("\r", "")
    low = t.lower()
    cons_i = low.find("constraints:")
    ex_i = low.find("example") 

    desc = t
    examples = ""
    constraints = ""

    if cons_i != -1:
        constraints = t[cons_i:].strip()
        desc = t[:cons_i].rstrip()

    if ex_i != -1:
        end = cons_i if cons_i != -1 else len(t)
        examples = t[ex_i:end].strip()
        desc = t[:ex_i].rstrip()

    return {"desc": desc, "examples": examples, "constraints": constraints}

class ProblemPanel:
    """Scrollable problem view rendered inside a rect."""
    def __init__(self, rect: pygame.Rect, fonts):
        self.rect = rect
        self.big, self.font, self.mono = fonts 
        self.meta = None
        self.scroll_y = 0
        self._content_h = 0 

    def set_meta(self, meta: dict | None):
        self.meta = meta
        self.scroll_y = 0

    def handle_event(self, e):
        if e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint((mx, my)):
                view_h = self.rect.h - 20
                max_scroll = max(0, self._content_h - view_h)
                self.scroll_y = max(0, min(max_scroll, self.scroll_y - e.y * 40))

    def _draw_text_block(self, surface, text, font, inner_w, cy):
        words = text.split()
        line = ""
        lh = font.get_height() + 2
        for w in words:
            test = f"{line} {w}".strip()
            if font.size(test)[0] <= inner_w:
                line = test
            else:
                surface.blit(font.render(line, True, FG), (0, cy))
                cy += lh
                line = w
        if line:
            surface.blit(font.render(line, True, FG), (0, cy))
            cy += lh
        return cy

    def draw(self, surface: pygame.Surface):
        # background panel
        pygame.draw.rect(surface, (28, 28, 36), self.rect, border_radius=12)

        x = self.rect.x + 12
        y0 = self.rect.y + 10
        inner_w = self.rect.w - 24
        viewport_h = self.rect.h - 20

        if not self.meta:
            surface.blit(self.big.render("Load a problem with [P]", True, (200, 200, 210)), (x, y0))
            self._content_h = viewport_h
            return

        title = self.meta.get("title") or "Problem"
        diff  = self.meta.get("difficulty") or ""
        sections = split_problem_text(self.meta.get("text") or "")

        # --- measure total content
        h = 0
        h += self.big.get_height()
        h += (self.font.get_height() + 2)
        h += 8
        if sections["desc"]:
            h += measure_wrapped(sections["desc"], self.mono, inner_w, line_h=self.mono.get_height()+2)
        if sections["examples"]:
            h += 12 + self.font.get_height()
            h += measure_wrapped(sections["examples"], self.mono, inner_w, line_h=self.mono.get_height()+2)
        if sections["constraints"]:
            h += 12 + self.font.get_height()
            h += measure_wrapped(sections["constraints"], self.mono, inner_w, line_h=self.mono.get_height()+2)

        content_h = max(h, viewport_h)
        self._content_h = content_h
        max_scroll = max(0, content_h - viewport_h)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

        # --- draw into content surface
        content = pygame.Surface((inner_w, content_h), pygame.SRCALPHA)
        cy = 0
        content.blit(self.big.render(title, True, FG), (0, cy)); cy += self.big.get_height()
        content.blit(self.font.render(f"Difficulty: {diff}", True, MUTED), (0, cy)); cy += self.font.get_height()+2
        cy += 8

        if sections["desc"]:
            cy = self._draw_text_block(content, sections["desc"], self.mono, inner_w, cy)

        if sections["examples"]:
            cy += 12
            content.blit(self.font.render("Examples", True, ACCENT), (0, cy)); cy += self.font.get_height()
            cy = self._draw_text_block(content, sections["examples"], self.mono, inner_w, cy)

        if sections["constraints"]:
            cy += 12
            content.blit(self.font.render("Constraints", True, ACCENT), (0, cy)); cy += self.font.get_height()
            cy = self._draw_text_block(content, sections["constraints"], self.mono, inner_w, cy)

        # blit clipped viewport
        view = pygame.Rect(0, self.scroll_y, inner_w, viewport_h)
        surface.blit(content, (x, y0), area=view)

        # scrollbar
        if max_scroll > 0:
            track = pygame.Rect(self.rect.right - 8 - 4, y0, 4, viewport_h)
            pygame.draw.rect(surface, (60, 60, 75), track, border_radius=2)
            frac = viewport_h / content_h
            thumb_h = max(24, int(track.h * frac))
            thumb_y = int(track.y + (track.h - thumb_h) * (self.scroll_y / max_scroll))
            thumb = pygame.Rect(track.x, thumb_y, track.w, thumb_h)
            pygame.draw.rect(surface, ACCENT, thumb, border_radius=2)