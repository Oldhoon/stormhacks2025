#!/usr/bin/env python
"""
Main entry point for the Arena + LeetCode integrated game.
Uses GameController to manage state transitions.
"""
import pygame
import sys
import os

# Add game module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'game'))

from game.controller import GameController

def main():
    """Initialize and run the game."""
    pygame.init()
    
    # Create window with arena dimensions
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Leetcode Arena")
    
    # Create and run controller
    controller = GameController(screen)
    controller.run()

if __name__ == "__main__":
    main()
