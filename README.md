# Stormhacks 2025 - LeetCode Arena

## Gameplay Loop
Defeat the evil Knight in arena combat, then solve a LeetCode problem by dragging and dropping code blocks into the correct position! Time is of the essence.

### How to Play
1. **Arena Mode**: Control the Samurai to battle the Knight
   - Move: A/D keys
   - Attack: SPACE key
2. **Knight Defeat**: When you defeat the Knight, the game transitions to LeetCode mode
3. **LeetCode Challenge**: 
   - You have 120 seconds to solve the problem
   - Drag and drop code snippets to arrange them correctly
   - Click "SUBMIT" to check your solution
4. **Victory or Continue**:
   - ✓ Solve correctly → **You Win!**
   - ✗ Time expires → Knight revives with 50% HP, battle continues

## Running the Game

### Quick Start
```bash
# Install dependencies
pip install pygame pyyaml requests beautifulsoup4

# Run the game
python main.py
```

### Alternative: Run original arena (without controller)
```bash
python arena.py
```

## Project Structure
- `main.py` - New entry point using GameController
- `game/controller.py` - State management (Arena, LeetCode, End states)
- `arena.py` - Original arena game (can run standalone)
- `game/` - LeetCode UI components and problem bank
- `assets/` - Sprites and graphics

## Testing
```bash
# Test the controller integration
python test_controller.py
```

## Goal
Get speedier at LeetCode problems and get practice in a roguelike experience!

# Art Credits:

- Samurai: https://xzany.itch.io/samurai-2d-pixel-art
- Knight: https://xzany.itch.io/free-knight-2d-pixel-art
- Background: https://ansimuz.itch.io/cyberpunk-street-environment
- Health bar: https://bdragon1727.itch.io/basic-pixel-health-bar-and-scroll-bar
