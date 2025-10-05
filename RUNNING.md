# Running the Game

## Quick Start

Run the game using:
```bash
python3 main.py
```

Or directly:
```bash
python3 controller.py
```

## Game Flow

1. **Arena Mode**: Start by fighting the Knight as the Samurai
   - Use A/D to move left/right
   - Use SPACE to attack
   
2. **Knight Death**: When the Knight's health reaches 0, the game switches to LeetCode mode

3. **LeetCode Mode**: Solve a coding problem by arranging code snippets
   - Drag and drop code lines into the correct order
   - Click SUBMIT when ready
   - You have 30 seconds
   
4. **Timer Expiry**: If time runs out, the Knight revives and you return to Arena mode

5. **Victory**: If you solve the problem correctly before time runs out, you win!

## Controls

**Arena Mode:**
- A: Move left
- D: Move right  
- SPACE: Attack

**LeetCode Mode:**
- Mouse: Drag code snippets
- SUBMIT button: Check your answer
- RESET button: Shuffle snippets again

**General:**
- ESC: Quit
- R: Restart (when in ENDED state)

## Architecture

The game uses a compositor pattern:
- `controller.py`: Main game controller managing state transitions
- `arena.py`: Arena fighting game rendering to a surface
- `lc_screen.py`: LeetCode problem UI rendering to a surface
- Surfaces are composited and displayed by the controller
