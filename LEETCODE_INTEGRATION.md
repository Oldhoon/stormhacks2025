# LeetCode Problem Integration with Arena Game

## Overview

The Arena game now includes an integrated LeetCode problem challenge that appears when the player defeats the Knight enemy.

## Game Flow

1. **Arena Combat**: Start in the arena and fight the Knight using standard controls
   - Move: A/D keys
   - Attack: SPACE key

2. **Knight Defeat**: When the player successfully kills the Knight, the game pauses and transitions to LeetCode problem mode

3. **LeetCode Challenge**: 
   - A random LeetCode problem is displayed from the problem bank
   - Players must rearrange scrambled code snippets into the correct order
   - Players have 60 seconds to solve the problem
   - Use mouse to drag and drop code snippets
   - Click "SUBMIT" to check your solution
   - Click "RESET" to scramble the snippets again

4. **Victory Condition**: 
   - If the player solves the problem correctly within 60 seconds → **VICTORY!**
   - The game ends with a victory message

5. **Timeout Condition**:
   - If 60 seconds expire without solving the problem → Return to Arena
   - The Knight revives with 50% health
   - The battle continues

## Technical Implementation

### Modified Files
- `arena.py`: Main integration logic added

### Key Components
- **Problem UI**: Reuses `game/ui/problem_panel.py` and `game/ui/snippet_board.py`
- **Problem Loading**: Uses `game/problems/loader.py` to fetch random problems
- **Grading**: Uses `game/main.py`'s `grade_submission()` function

### New Arena Class Features
- `problem_mode`: Boolean flag to track if in problem-solving mode
- `problem_start_time`: Tracks when problem mode started (for 60s timer)
- `current_problem`: Stores the current problem being solved
- `problem_panel`: UI component for displaying problem description
- `snippet_board`: UI component for code snippet drag-and-drop
- `victory`: Boolean flag to track if player won

### New Methods
- `start_problem_mode()`: Triggered when Knight dies
- `end_problem_mode_victory()`: Called when problem is solved correctly
- `end_problem_mode_timeout()`: Called when 60 seconds expire
- `get_problem_remaining_time()`: Returns remaining seconds for problem

## Problem Bank

Problems are loaded from `game/problems/bank/*.yaml` files. Each problem contains:
- Problem metadata (title, difficulty, tags)
- Problem description
- Code snippets that need to be arranged in correct order

## Controls

### Arena Mode
- **A/D**: Move left/right
- **SPACE**: Attack
- **ESC**: Quit game
- **R**: Restart game (when game over)

### Problem Mode
- **Mouse**: Drag and drop code snippets
- **Click SUBMIT**: Submit solution for grading
- **Click RESET**: Scramble snippets again

## Future Enhancements

Potential improvements:
- Multiple rounds (defeat Knight → solve problem → Knight revives stronger)
- Problem difficulty scaling based on Knight's level
- Score/points system based on solution time
- Hint system for harder problems
