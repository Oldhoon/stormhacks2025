#!/usr/bin/env python3
"""
Visual verification script - captures screenshots of each game state
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from controller import GameController

def capture_screenshots():
    """Capture screenshots of each game state"""
    print("Capturing screenshots of game states...")
    
    gc = GameController()
    
    # 1. Capture ARENA state
    print("1. Capturing ARENA state...")
    gc.state = "ARENA"
    gc.arena.draw()
    pygame.image.save(gc.arena_surface, "/tmp/arena_state.png")
    print("   Saved: /tmp/arena_state.png")
    
    # 2. Capture LC state
    print("2. Capturing LC state...")
    gc.state = "LC"
    gc.lc_screen.load_problem()
    gc.lc_screen.start_timer()
    gc.lc_screen.draw()
    pygame.image.save(gc.leetcode_surface, "/tmp/lc_state.png")
    print("   Saved: /tmp/lc_state.png")
    
    # 3. Capture ENDED state
    print("3. Capturing ENDED/Victory state...")
    gc.state = "ENDED"
    gc.draw()
    pygame.image.save(gc.display, "/tmp/victory_state.png")
    print("   Saved: /tmp/victory_state.png")
    
    pygame.quit()
    print("\nAll screenshots captured successfully!")
    print("Screenshots saved in /tmp/")

if __name__ == "__main__":
    capture_screenshots()
