# AI Coding Agent Instructions - Pygame Platformer

## Project Overview
Single-file Pygame platformer game with 2D physics, camera system, and multi-level progression. The entire game logic is in `main.py` with no external assets or configuration files.

## Architecture & Core Systems

### Game Loop & Structure
- **Main entry point:** `Game` class in `main.py` (lines 187-552)
- **Loop phases:** `handle_events()` → `update()` → `draw()` running at 60 FPS
- **Sprite groups pattern:** Separate sprite groups for entities (`self.platforms`, `self.enemies`, `self.collectibles`, `self.all_sprites`) to enable batch collision detection and rendering

### Physics & Collision System
- **Player gravity:** Applied each frame via `apply_gravity()` with terminal velocity capped at 20 units
- **Collision handling:** Separate horizontal and vertical collision passes in `Player.update()` to prevent clipping
  - Horizontal: Check collisions, push player out of platform
  - Vertical: Check collisions, stop falling, clear jump state
- **Fall-off reset:** Player respawns at (100, 100) when falling below screen height

### Camera System
- **Implementation:** `update_camera()` keeps player at horizontal third of screen (`SCREEN_WIDTH // 3`)
- **Rendering offset:** All sprites drawn with `sprite.rect.x - self.camera_x` for horizontal offset
- **Bounds clamping:** Camera never goes below x=0 to prevent negative scrolling

### Level System
- **Level data-driven:** `create_level_1()` and `create_level_2()` populate sprite groups with tuples
- **Level progression:** Trigger on `player.rect.x > level_end_x`
- **Reset sequence:** `load_next_level()` clears all groups, increments level counter, respawns player

### Cyberpunk Theme System
- **Theme toggle:** `USE_CYBERPUNK_THEME = True` (line 39) enables dark mode with neon colors
- **Color constants:** Lines 16-35 define all neon palette and dark backgrounds
- **Animation:** `frame_count` increments each frame for smooth effects (grid scanlines, HUD pulsing)
- **Rendering:** Conditional theme application in each sprite class; fallback to classic colors if disabled

## Key Patterns & Conventions

### Sprite Lifecycle
- All sprite types extend `pygame.sprite.Sprite` (Player, Enemy, Collectible, Platform)
- Sprites are added to relevant groups AND `self.all_sprites` for unified rendering
- Destructive actions use `.kill()` (enemies when jumped on, collectibles when collected)
- SRCALPHA transparency used for all themed sprites for smooth edges

### Constants at Module Level
- Physics constants grouped at top (GRAVITY=0.6, JUMP_STRENGTH=15, PLAYER_SPEED=5)
- Theme colors organized in sections (dark mode, neon colors) with comments
- Screen dimensions tied to camera and level design (800×600)
- Glow intensity and scanline settings easily adjustable

### Game State Tracking
- `self.score`, `self.level`, `self.camera_x`, `self.frame_count` in Game class
- Player velocity and jumping state in Player class (`vel_x`, `vel_y`, `is_jumping`, `glow_time`)
- Enemy patrol bounds passed in constructor to decouple enemy from global state
- Collectible animation state stored in `bob_offset` and `original_y`

### Enemy Behavior
- **Patrol pattern:** Enemies bounce between left/right bounds via `vel_x *= -1`
- **Kill condition:** Player must collide from above (check `self.player.vel_y > 0`) to eliminate
- **Side collision:** Side hits reset player to spawn point and zero score

### Visual Theming Pattern
- **Conditional rendering:** Each sprite class checks `USE_CYBERPUNK_THEME` flag
- **Layered drawing:** Main shape + glow border + detail accents (cyberpunk style)
- **Animation helpers:** `math.sin()` for bobbing, frame counter modulo for pulsing
- **Reusable UI:** `draw_ui_panel()` method for neon HUD elements

## Development Workflows

### Running the Game
```bash
python main.py
```
Launches at 60 FPS with Cyberpunk theme enabled. Use arrow keys to move, spacebar to jump.

### Adding Features
1. **New level:** Add `create_level_3()` method, update `create_level()` dispatcher
2. **New sprite types:** Extend `pygame.sprite.Sprite`, add to appropriate group in `__init__`, update `update()` logic
3. **New theme colors:** Add to constants section (lines 21-35), reference in sprite rendering

### Common Modifications
- **Adjust physics:** Tweak GRAVITY, JUMP_STRENGTH, PLAYER_SPEED, velocity cap
- **Platform layout:** Modify tuples in `platforms_data` lists (x, y, width, height)
- **Enemy density:** Change `enemies_data` tuples (x, y, left_bound, right_bound)
- **Collectible rewards:** Change multiplier (currently `* 10`)
- **Theme colors:** Edit neon color tuples (lines 21-27)
- **Grid appearance:** Adjust `grid_size` in `draw_grid_background()` (line 378) or scanline speed (line 380)

### Theme Toggling
```python
# Line 39: Set to False for classic rendering
USE_CYBERPUNK_THEME = False  # Classic white background
USE_CYBERPUNK_THEME = True   # Dark mode with neon glow
```

## Integration Points & Dependencies
- **pygame library:** Only external dependency; used for sprite, collision, event handling, rendering
- **math module:** For `sin()` function in collectible bobbing animation
- **sys module:** For exit handling
- **No file I/O:** No config files, asset loading, or persistence
- **No external data:** All level data hardcoded in `create_level_*` methods

## Common Pitfalls
- **Collision order matters:** Horizontal first, then vertical prevents clipping—don't reorder
- **Camera offset:** Apply only to x-coordinate; y is screen-relative
- **Jump gate logic:** `is_jumping` flag prevents mid-air double-jumps; set false only on platform collision
- **Level end trigger:** Check happens AFTER player movement; account for player width
- **Theme toggle:** Must affect both sprite rendering AND draw() method; check both locations
- **Animation frame count:** Remember to increment `self.frame_count` in `update()` method
- **Collectible update:** Call `self.collectibles.update()` to enable bobbing animation

## File Structure
```
main.py (552 lines)
├── Imports & Pygame init
├── Theme Constants (Lines 16-43)
├── Sprite Classes (Lines 45-185)
│   ├── Player (45-113)
│   ├── Enemy (103-128)
│   ├── Collectible (130-157)
│   └── Platform (159-185)
└── Game Class (187-552)
    ├── __init__() - Setup with fonts, sprites, theme
    ├── create_level() - Dispatch level creation
    ├── create_level_1/2() - Level data
    ├── update_camera() - Camera logic
    ├── handle_events() - Input
    ├── load_next_level() - Progression
    ├── update() - Game state + animations
    ├── draw_grid_background() - Grid overlay
    ├── draw_ui_panel() - Reusable UI
    ├── draw() - Rendering with theme
    └── run() - Main loop
```

## Documentation Files
- **CYBERPUNK_THEME_REFACTOR.md** - Full technical details of the theme refactor
- **CYBERPUNK_THEME_VISUAL_SUMMARY.md** - Design decisions and color choices
- **CYBERPUNK_THEME_QUICK_REFERENCE.md** - Quick lookup guide for customization
- **BEFORE_AFTER_CODE_EXAMPLES.md** - Side-by-side code comparisons
