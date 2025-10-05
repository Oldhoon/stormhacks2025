#!/usr/bin/env python3
"""
Simulated game flow test - verifies complete game cycle
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from controller import GameController

def simulate_game_flow():
    """Simulate a complete game flow from start to finish"""
    print("="*60)
    print("Simulating Complete Game Flow")
    print("="*60)
    
    gc = GameController()
    
    # Step 1: Start in ARENA mode
    print("\n1. Game starts in ARENA mode")
    assert gc.state == "ARENA", "Should start in ARENA"
    print(f"   State: {gc.state} ✓")
    print(f"   Knight alive: {gc.arena.knight.alive} ✓")
    print(f"   Knight HP: {gc.arena.knight.hp}")
    
    # Step 2: Simulate some arena gameplay
    print("\n2. Simulating arena gameplay...")
    for i in range(3):
        gc.update()
    print("   Arena updated successfully ✓")
    
    # Step 3: Knight takes damage
    print("\n3. Knight takes damage...")
    initial_hp = gc.arena.knight.hp
    gc.arena.knight.hp -= 50
    print(f"   HP: {initial_hp} -> {gc.arena.knight.hp}")
    
    # Step 4: Knight dies
    print("\n4. Knight dies...")
    gc.arena.knight.alive = False
    gc.arena.knight.hp = 0
    gc.check_knight_death()
    print(f"   State changed: ARENA -> {gc.state}")
    assert gc.state == "LC", "Should transition to LC mode"
    print("   ✓ Transitioned to LeetCode mode")
    
    # Step 5: LeetCode timer active
    print("\n5. LeetCode problem loaded...")
    assert gc.lc_screen.timer_active, "Timer should be active"
    remaining = gc.lc_screen.get_remaining_time()
    print(f"   Timer: {remaining/1000:.1f} seconds remaining ✓")
    print(f"   Problem loaded: {gc.lc_screen.current_problem is not None} ✓")
    
    # Scenario A: Timer expires
    print("\n6. Scenario A: Timer expires...")
    gc.lc_screen.timer_start = pygame.time.get_ticks() - 40000
    gc.update()
    print(f"   State after timer expiry: {gc.state}")
    assert gc.state == "ARENA", "Should return to ARENA"
    assert gc.arena.knight.alive, "Knight should be revived"
    print(f"   Knight revived: HP = {gc.arena.knight.hp} ✓")
    print("   ✓ Returned to ARENA mode")
    
    # Reset for scenario B
    gc.state = "LC"
    gc.lc_screen.timer_active = True
    gc.lc_screen.timer_start = pygame.time.get_ticks()
    gc.lc_screen.problem_solved = False
    
    # Scenario B: Problem solved
    print("\n7. Scenario B: Problem solved...")
    gc.lc_screen.problem_solved = True
    gc.update()
    print(f"   State after solving: {gc.state}")
    assert gc.state == "ENDED", "Should go to ENDED/Victory"
    print("   ✓ Victory achieved!")
    
    # Test victory screen rendering
    print("\n8. Testing victory screen...")
    gc.draw()
    print("   ✓ Victory screen renders successfully")
    
    pygame.quit()
    
    print("\n" + "="*60)
    print("✓ All game flow scenarios completed successfully!")
    print("="*60)
    return True

def test_input_handling():
    """Test that input is handled correctly in each state"""
    print("\n" + "="*60)
    print("Testing Input Handling")
    print("="*60)
    
    gc = GameController()
    
    # Test ARENA input
    print("\n1. Testing ARENA input...")
    gc.state = "ARENA"
    keys = pygame.key.get_pressed()
    print("   ✓ Arena key state can be read")
    
    # Test LC input
    print("\n2. Testing LC input...")
    gc.state = "LC"
    gc.lc_screen.load_problem()
    # Simulate mouse event (doesn't need actual mouse)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100), 'button': 1})
    gc.lc_screen.handle_event(event)
    print("   ✓ LC screen handles events")
    
    pygame.quit()
    print("\n✓ Input handling works correctly")
    return True

def main():
    """Run all simulation tests"""
    try:
        simulate_game_flow()
        test_input_handling()
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        return True
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
