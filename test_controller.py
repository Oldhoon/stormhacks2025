#!/usr/bin/env python
"""
Test the GameController integration.
"""
import sys
import os

# Suppress pygame output
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

def test_controller_integration():
    """Test the GameController-based integration."""
    import pygame
    pygame.init()
    
    print("Testing GameController Integration...")
    print("=" * 60)
    
    # Test 1: Controller creation
    print("\n1. Testing controller creation...")
    try:
        screen = pygame.display.set_mode((1280, 720))
        from game.controller import GameController
        controller = GameController(screen)
        print(f"   ✓ GameController created")
        print(f"   ✓ Initial state: {controller.state}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 2: Arena screen
    print("\n2. Testing arena screen...")
    try:
        assert controller.arena_screen is not None
        assert controller.arena_screen.knight is not None
        assert controller.arena_screen.samurai is not None
        print(f"   ✓ Arena screen initialized")
        print(f"   ✓ Knight HP: {controller.arena_screen.knight.hp}")
        print(f"   ✓ Knight alive: {controller.arena_screen.knight.alive}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 3: Knight death triggers LC screen
    print("\n3. Testing knight death → LC transition...")
    try:
        controller.arena_screen.knight.hp = 0
        controller.arena_screen.knight.alive = False
        controller.arena_screen.update(0.016)
        assert controller.state == "LC"
        assert controller.lc_screen is not None
        print(f"   ✓ State transitioned to LC")
        print(f"   ✓ LC screen created")
        if controller.lc_screen.current_problem:
            print(f"   ✓ Problem loaded: {controller.lc_screen.current_problem.title}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 4: LC timeout revives knight
    print("\n4. Testing LC timeout → Arena transition...")
    try:
        controller._on_lc_timeout()
        assert controller.state == "ARENA"
        assert controller.arena_screen.knight.alive == True
        assert controller.arena_screen.knight.hp == 50
        print(f"   ✓ State transitioned back to ARENA")
        print(f"   ✓ Knight revived with HP: {controller.arena_screen.knight.hp}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 5: Second knight death
    print("\n5. Testing second knight death...")
    try:
        controller.arena_screen.knight.hp = 0
        controller.arena_screen.knight.alive = False
        controller.arena_screen.update(0.016)
        assert controller.state == "LC"
        print(f"   ✓ State transitioned to LC again")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 6: Victory condition
    print("\n6. Testing victory condition...")
    try:
        controller.lc_screen.on_victory()
        assert controller.state == "ENDED"
        assert controller.ended_victory == True
        print(f"   ✓ State transitioned to ENDED")
        print(f"   ✓ Victory flag set")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("\nGame Flow Summary:")
    print("━" * 60)
    print("1. Start in Arena (Samurai vs Knight combat)")
    print("2. Knight dies → Switch to LeetCode problem screen")
    print("3. Player has 120 seconds to solve problem")
    print("4. Option A: Solve correctly → VICTORY!")
    print("5. Option B: Timer expires → Return to Arena, Knight at 50% HP")
    print("━" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_controller_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
