"""
Integration test for Arena-LeetCode game.
This test has been superseded by test_controller.py which tests the new
GameController-based architecture.

For backward compatibility, this script now runs the new test.
"""
import sys
import subprocess

def test_arena_integration():
    """Run the new controller-based test."""
    print("=" * 70)
    print("NOTE: Arena has been refactored to use GameController architecture.")
    print("Running test_controller.py instead...")
    print("=" * 70)
    print()
    
    result = subprocess.run([sys.executable, 'test_controller.py'])
    return result.returncode == 0

if __name__ == "__main__":
    success = test_arena_integration()
    sys.exit(0 if success else 1)

