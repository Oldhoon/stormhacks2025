import pygame

try:
    from .config import WIDTH, HEIGHT
    from .leetcode_app import LeetCodeGame
except ImportError:  # pragma: no cover
    from config import WIDTH, HEIGHT
    from leetcode_app import LeetCodeGame


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
    pygame.display.set_caption("Pygame - Problems")
    clock = pygame.time.Clock()
    game = LeetCodeGame(screen, strict_mode=False)

    running = True
    while running:
        dt = clock.tick(120) / 1000.0
        for event in pygame.event.get():
            game.process_event(event)
            if game.get_result() == "quit":
                running = False
                break
        if not running:
            break
        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
