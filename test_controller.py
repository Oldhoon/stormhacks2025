#!/usr/bin/env python3
"""
Test script to verify controller logic without running the full game loop
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for testing

import pygame
from controller import GameController

def test_initialization():
    """Test that controller initializes correctly"""
    print("Test 1: Initialization...")
    gc = GameController()
    assert gc.state == "ARENA", f"Expected initial state ARENA, got {gc.state}"
    assert gc.arena is not None, "Arena should be initialized"
    assert gc.lc_screen is not None, "LC screen should be initialized"
    print("✓ Initialization successful")
    pygame.quit()
    return True

def test_knight_death_detection():
    """Test that knight death is detected"""
    print("\nTest 2: Knight death detection...")
    gc = GameController()
    
    # Simulate knight death
    gc.arena.knight.alive = False
    gc.arena.knight.hp = 0
    
    # Should detect death and switch state
    gc.check_knight_death()
    assert gc.state == "LC", f"Expected state LC after knight death, got {gc.state}"
    print("✓ Knight death detection works")
    pygame.quit()
    return True

def test_lc_timer():
    """Test LC timer functionality"""
    print("\nTest 3: LC Timer...")
    gc = GameController()
    
    # Load a problem and start timer
    gc.lc_screen.load_problem()
    gc.lc_screen.start_timer()
    
    assert gc.lc_screen.timer_active, "Timer should be active"
    remaining = gc.lc_screen.get_remaining_time()
    assert remaining > 0, f"Should have time remaining, got {remaining}"
    print(f"✓ Timer started with {remaining}ms remaining")
    
    # Simulate timer expiry
    gc.lc_screen.timer_start = pygame.time.get_ticks() - 40000  # 40 seconds ago
    assert gc.lc_screen.is_timer_expired(), "Timer should be expired"
    print("✓ Timer expiry detection works")
    pygame.quit()
    return True

def test_state_transitions():
    """Test full state transition flow"""
    print("\nTest 4: State transitions...")
    gc = GameController()
    
    # Start in ARENA
    assert gc.state == "ARENA", "Should start in ARENA"
    
    # Transition to LC on knight death
    gc.arena.knight.alive = False
    gc.check_knight_death()
    assert gc.state == "LC", "Should transition to LC"
    
    # Timer expiry should return to ARENA
    gc.state = "LC"
    gc.lc_screen.timer_active = True
    gc.lc_screen.timer_start = pygame.time.get_ticks() - 40000
    gc.update()  # This should detect timer expiry
    assert gc.state == "ARENA", f"Should return to ARENA, got {gc.state}"
    
    # Problem solved should go to ENDED
    gc.state = "LC"
    gc.lc_screen.problem_solved = True
    gc.update()
    assert gc.state == "ENDED", f"Should go to ENDED, got {gc.state}"
    
    print("✓ All state transitions work correctly")
    pygame.quit()
    return True

def test_surfaces():
    """Test that surfaces are created and can be drawn to"""
    print("\nTest 5: Surface rendering...")
    gc = GameController()
    
    # Check surfaces exist and have correct dimensions
    assert gc.arena_surface.get_width() == 1280, "Arena surface width should be 1280"
    assert gc.arena_surface.get_height() == 720, "Arena surface height should be 720"
    assert gc.leetcode_surface.get_width() == 1280, "LC surface width should be 1280"
    assert gc.leetcode_surface.get_height() == 720, "LC surface height should be 720"
    
    # Test drawing doesn't crash
    try:
        gc.arena.draw()
        print("✓ Arena can draw to surface")
    except Exception as e:
        print(f"✗ Arena draw failed: {e}")
        return False
    
    try:
        gc.lc_screen.load_problem()
        gc.lc_screen.draw()
        print("✓ LC screen can draw to surface")
    except Exception as e:
        print(f"✗ LC screen draw failed: {e}")
        return False
    
    pygame.quit()
    return True

def main():
    """Run all tests"""
    print("="*60)
    print("Running Controller Integration Tests")
    print("="*60)
    
    tests = [
        test_initialization,
        test_knight_death_detection,
        test_lc_timer,
        test_state_transitions,
        test_surfaces,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
