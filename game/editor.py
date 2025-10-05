# import pygame
# import pygame.freetype
# import threading
# import queue
# import time
# import os
#
# from game.ui.snippet_board import SnippetBoard
# from game.ui.utils import worker, draw_wrapped
# from game.config import *
#
# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((WIDTH, HEIGHT))
#     pygame.display.set_caption("Code Snippet Game")
#
#     ui_font = pygame.freetype.SysFont("Arial", 16)
#     mono_font = pygame.freetype.SysFont("Courier New", 16)
#
#     clock = pygame.time.Clock()
#
#     snippet_board = SnippetBoard(pygame.Rect(LEFT_W + PADDING, PADDING, WIDTH - LEFT_W - 2 * PADDING, HEIGHT - 2 * PADDING), ui_font, mono_font)
#
#     running = True
#     while running:
#         for e in pygame.event.get():
#             if e.type == pygame.QUIT:
#                 running = False
#             snippet_board.handle_event(e)
#
#         screen.fill(BG)
#         snippet_board.draw(screen)
#         pygame.display.flip()
#         clock.tick(60)
#
#     pygame.quit()
#
# if __name__ == "__main__":
#     main()