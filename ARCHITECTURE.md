# Architecture Overview

## New Controller Pattern (main.py + game/controller.py)

The game now uses a clean MVC-style architecture with a central GameController managing state transitions.

### State Flow Diagram

```
┌─────────┐
│  START  │
└────┬────┘
     │
     v
┌─────────────────────────────────────────┐
│          ARENA State                     │
│  - Samurai vs Knight combat             │
│  - Player controls: A/D move, SPACE atk │
│  - 3-minute timer                        │
└────────────┬────────────────────────────┘
             │
             │ Knight HP → 0
             v
┌─────────────────────────────────────────┐
│        LEETCODE State                    │
│  - Display problem UI                    │
│  - 120-second timer                      │
│  - Drag & drop code snippets            │
└────┬─────────────────────┬──────────────┘
     │                     │
     │ Correct             │ Timeout
     │ Solution            │
     v                     v
┌──────────┐         ┌────────────────┐
│  ENDED   │         │  Back to ARENA │
│ Victory! │         │ Knight @ 50% HP│
└──────────┘         └────────────────┘
```

### Component Structure

```
main.py
  └─> GameController (game/controller.py)
       ├─> ArenaScreen
       │    ├─> Samurai (samurai.py)
       │    ├─> Knight (knight.py)
       │    └─> Callback: on_knight_dead() → start_leetcode()
       │
       ├─> LCScreen
       │    ├─> ProblemPanel (game/ui/problem_panel.py)
       │    ├─> SnippetBoard (game/ui/snippet_board.py)
       │    ├─> LCClient API (game/api.py) + YAML fallback
       │    ├─> Callback: on_victory() → end_game(True)
       │    └─> Callback: on_timeout() → revive knight, resume arena
       │
       └─> State: "ARENA" | "LC" | "ENDED"
```

### Key Classes

#### GameController
- **Responsibility**: Manage global game state and transitions
- **States**: ARENA, LC, ENDED
- **Methods**:
  - `start_arena()`: Initialize or resume arena combat
  - `start_leetcode()`: Load and display LeetCode problem
  - `end_game(victory)`: Show end screen
  - `run()`: Main game loop

#### ArenaScreen
- **Responsibility**: Wrap Arena logic with callback support
- **Features**:
  - Manages Samurai and Knight entities
  - Detects knight death and fires callback
  - Handles arena-specific input (A/D/SPACE)
- **Callback**: `on_knight_dead()` → triggers LC screen

#### LCScreen
- **Responsibility**: Display and manage LeetCode problem UI
- **Features**:
  - Fetch problem from API or YAML bank
  - Display timer countdown
  - Handle snippet drag-and-drop
  - Grade submissions
- **Callbacks**:
  - `on_victory()` → game ends in victory
  - `on_timeout()` → return to arena, revive knight

### API Integration

The LCScreen attempts to fetch problems from the LeetCode API:

```python
try:
    client = LCClient(timeout=3)
    meta = client.problem_meta("two-sum")
    # Use API problem
except:
    # Fallback to YAML bank
    problem = random_problem()
```

### Running the Game

**New controller-based entry point:**
```bash
python main.py
```

**Legacy arena (backward compatible):**
```bash
python arena.py
```

### Testing

```bash
# Test state transitions
python test_controller.py

# Legacy test (redirects to controller test)
python test_integration.py
```

### Future Improvements

- [ ] Add multiple difficulty levels
- [ ] Track score/time metrics
- [ ] Knight AI that gets smarter on revival
- [ ] More problem variety from API
- [ ] Leaderboard/persistence
