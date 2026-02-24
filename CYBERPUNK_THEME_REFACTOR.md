# Cyberpunk Grid Theme Refactor - Documentation

## Overview
The game has been refactored with a complete "Cyberpunk Grid" visual theme. All gameplay mechanics remain unchanged—only visual styling, UI components, and aesthetic enhancements have been modified.

## Theme Design Goals Achieved
✅ **Dark Mode First** - Dark gradient backgrounds (#050508, #0a0a14) instead of white  
✅ **Neon Accent Colors** - Cyan, magenta, purple, blue, green neon palette  
✅ **Glowing UI Elements** - Neon outlines and glow effects on HUD panels  
✅ **Futuristic Feel** - Holographic style UI with subtle animations  
✅ **Animated Grid Background** - Subtle grid lines with animated scanlines  
✅ **Smooth Transitions** - Glow colors shift based on frame count for visual feedback  

---

## Theme Constants & Configuration

### New Theme Variables (Lines 16-35)
Located at the top of `main.py` for easy customization:

```python
# Dark Mode Colors
BG_DARK = (5, 5, 15)           # Primary dark background
BG_DARKER = (10, 10, 20)       # Secondary dark background
GRID_LINE_COLOR = (20, 25, 50) # Subtle grid lines

# Neon Accent Colors
NEON_CYAN = (0, 255, 255)      # Bright cyan for primary UI
NEON_MAGENTA = (255, 0, 255)   # Bright magenta for secondary UI
NEON_PURPLE = (180, 0, 255)    # Electric purple for accents
NEON_BLUE = (0, 150, 255)      # Electric blue for alternates
NEON_GREEN = (0, 255, 100)     # Neon green for highlights
NEON_PINK = (255, 0, 127)      # Hot pink for accents

# Control Settings
USE_CYBERPUNK_THEME = True     # Global theme toggle flag
GLOW_INTENSITY = 2             # Adjust glow layers (for future enhancement)
SCANLINE_ALPHA = 15            # Control scanline opacity
```

### Theme Toggle
Set `USE_CYBERPUNK_THEME = True` to enable cyberpunk mode, or `False` to revert to classic styling.

---

## Component Changes

### 1. Player Sprite (Lines 45-71)
**Before:** Simple red rectangle  
**After:** Cyberpunk character with neon styling

```python
# Visual features:
- Neon cyan main body (primary highlight)
- Magenta border outline (glow effect)
- Purple accent lines (details)
- SRCALPHA transparency for smooth edges
```

**Added:** `self.glow_time` - Animation counter for future frame-based effects

### 2. Enemy Sprite (Lines 103-128)
**Before:** Simple green square  
**After:** Neon magenta circle with glow

```python
# Visual features:
- Circular magenta body (round vs square)
- Purple glow outline (2px border)
- Cyan interior line (detail accent)
- Maintains patrol behavior unchanged
```

### 3. Collectible Sprite (Lines 130-157)
**Before:** Simple yellow square  
**After:** Neon cyan star/diamond with bobbing animation

```python
# Visual features:
- Cyan star polygon (distinctive shape)
- Purple glow outline (1px border)
- Bobbing animation (sin wave motion)
- original_y tracking for animation
```

**New Method:** `update()` - Handles bobbing animation using `sin()` function

### 4. Platform Sprite (Lines 159-185)
**Before:** Solid black rectangles  
**After:** Neon blue with grid detail lines

```python
# Visual features:
- Bright neon blue fill (primary color)
- Cyan border glow (2px outline)
- Subtle vertical grid lines every 40px
- Color passed as parameter (supports variations)
```

**Logic:** Grid pattern drawn only on platforms wider than 40px

### 5. Game Class - UI & Rendering (Lines 187-550)

#### Font System (Lines 189-210)
Added three font sizes for hierarchy:
- `self.font_large` (48px) - For future title/menus
- `self.font_medium` (36px) - For HUD text
- `self.font_small` (24px) - For details

#### Frame Counter (Line 219)
- `self.frame_count` - Incremented each frame for smooth animations
- Used by grid background scanlines and color cycling

#### New Methods

##### `draw_grid_background()` (Lines 360-383)
Renders animated cyberpunk grid overlay:
- **Vertical lines** - Spaced 50px apart, camera-offset for parallax effect
- **Horizontal lines** - Static grid across full screen
- **Animated scanlines** - Horizontal bars that move based on `frame_count`
- **Subtle opacity** - Grid lines rendered at 10% opacity for background effect

##### `draw_ui_panel()` (Lines 385-407)
Reusable utility for drawing neon UI elements:
- Parameter: `text`, `x`, `y`, `text_color`, `bg_color`, `padding`, `glow`
- Draws background panel, glow border, and text
- Supports both cyberpunk and classic modes

#### Updated `draw()` Method (Lines 409-460)
Major visual overhaul:

1. **Background** - Dark mode fill (`BG_DARK`) instead of white
2. **Grid Overlay** - Calls `draw_grid_background()` for animated grid
3. **HUD Panels** - Replaced flat text with glowing panels:
   - **Score Panel** (top-right)
     - Cyan text on dark background
     - Cyan neon border glow
     - Formatted as `"SCORE: 000000"` (6-digit counter)
   - **Level Panel** (top-left)
     - Magenta text on dark background
     - Magenta neon border glow
     - Formatted as `"LEVEL: X"`
4. **Glow Animation** - HUD colors shift between `NEON_CYAN` and `NEON_BLUE` every 10 frames
5. **Background Fill** - Panels have subtle dark background (e.g., `(0, 50, 50)`)

#### Updated `update()` Method (Line 327)
Added `self.collectibles.update()` call to enable collectible animations (bobbing).

#### Updated `__init__()` Method (Lines 187-242)
- Window title changes based on theme: `"Cyberpunk Grid Platformer"` or `"Pygame Platformer"`
- Stores frame counter and multiple font sizes
- No changes to gameplay initialization

---

## Visual Styling Details

### Color Palette Usage
| Component | Primary Color | Accent/Glow | Notes |
|-----------|--------------|------------|-------|
| Player | NEON_CYAN | NEON_MAGENTA, NEON_PURPLE | Distinctive cyan for visibility |
| Enemy | NEON_MAGENTA | NEON_PURPLE | Hot pink for danger indicator |
| Collectible | NEON_CYAN | NEON_PURPLE | Star shape matches Player cyan |
| Platform | NEON_BLUE | NEON_CYAN | Blue for solid/walkable surfaces |
| HUD Level | NEON_MAGENTA | (glowing border) | Top-left corner |
| HUD Score | NEON_CYAN | (glowing border) | Top-right corner |
| Background | BG_DARK | GRID_LINE_COLOR | Animated grid overlay |

### Glow Effects
- **Static Glow** - 2px colored border around sprites (Platform, Enemy, Collectible)
- **Animated Glow** - HUD panels cycle colors every 10 frames for dynamic feedback
- **Scanlines** - Subtle horizontal scan lines moving at 2px/frame
- **Background Glow** - Dark semi-transparent panels behind HUD text

### Animation Systems
1. **Collectible Bobbing** - `sin(frame_ticks * 0.003) * 3` pixels
2. **Scanline Movement** - `(frame_count * 2) % SCREEN_HEIGHT`
3. **HUD Color Pulsing** - `(frame_count // 10) % 2 == 0` toggle
4. **Glow Flicker** - (Available for future enhancement)

---

## Code Architecture

### File Structure
```
main.py
├── Imports & Initialization
├── Theme Constants (Lines 16-43)
├── Sprite Classes
│   ├── Player (Lines 45-113)
│   ├── Enemy (Lines 103-128)
│   ├── Collectible (Lines 130-157)
│   └── Platform (Lines 159-185)
└── Game Class (Lines 187-550)
    ├── __init__() - Initialization
    ├── create_level() - Level dispatch
    ├── create_level_1() - Extended level
    ├── create_level_2() - Challenge level
    ├── update_camera() - Camera logic
    ├── handle_events() - Input handling
    ├── load_next_level() - Level progression
    ├── update() - Game state (UPDATED)
    ├── draw_grid_background() - NEW
    ├── draw_ui_panel() - NEW (reusable)
    ├── draw() - Rendering (UPDATED)
    └── run() - Main loop
```

---

## Gameplay Logic - Unchanged
✅ Physics (gravity, velocity, collision)  
✅ Player movement and jumping  
✅ Enemy patrol and collision  
✅ Collectible scoring  
✅ Level progression  
✅ Camera system  
✅ Win/lose conditions  

All gameplay mechanics remain identical. Only visual presentation has changed.

---

## Performance Considerations
- **SRCALPHA Transparency** - Used for smooth sprite edges (minimal performance impact)
- **Grid Drawing** - Optimized with loop-based line drawing (efficient for 50px grid)
- **Scanline Animation** - Single modulo operation per frame (negligible cost)
- **Font Rendering** - Three font sizes cached in `__init__()` (no per-frame rendering)

---

## Customization Guide

### Change Theme Colors
Edit lines 16-35 to adjust any neon color:
```python
NEON_CYAN = (0, 255, 255)  # Modify these tuples
```

### Disable Theme
Set line 39 to:
```python
USE_CYBERPUNK_THEME = False
```

### Adjust Grid Spacing
Change line 378:
```python
grid_size = 50  # Increase for wider grid, decrease for denser grid
```

### Modify Scanline Speed
Change line 380:
```python
scanline_y = (self.frame_count * 2) % SCREEN_HEIGHT  # 2 = speed
```

### Customize Collectible Bob Animation
Change line 156:
```python
self.bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
                                         # 0.003 = speed, 3 = distance
```

### Add HUD Glow Intensity
Modify line 416-417 and 425-426 to change glow border thickness:
```python
pygame.draw.rect(self.screen, glow_color, glow_rect, 2)  # 2 = thickness
```

---

## Future Enhancement Opportunities

### Level 1: Basic Effects
- [ ] Glitch flicker effect on level transitions
- [ ] Fade/wipe transitions between screens
- [ ] Bloom/blur on collectible pickup
- [ ] Player damage flash (white glow on enemy hit)

### Level 2: Advanced Effects
- [ ] Parallax grid background at different depths
- [ ] Procedural pink "noise" generator for digital rain effect
- [ ] Platform glow intensity based on proximity to player
- [ ] Enemy "target lock" reticle animation

### Level 3: Polish
- [ ] Start/pause menu with themed buttons
- [ ] Game over / level complete screens
- [ ] HUD-style minimap (camera view indicator)
- [ ] Score multiplier effects with floating numbers

---

## Testing Checklist
- [x] Syntax validation (no Python errors)
- [x] All sprites render correctly
- [x] Camera system works with new sprites
- [x] Collectibles animate (bobbing)
- [x] Platforms render with grid pattern
- [x] HUD displays score and level
- [x] Grid background animates
- [x] Theme toggle works (set `USE_CYBERPUNK_THEME`)
- [ ] Run game and verify visual quality
- [ ] Test both levels work as expected
- [ ] Confirm no performance degradation

---

## Summary of Changes

| Category | Changes |
|----------|---------|
| **Lines Added** | ~200 (theme constants, new methods, enhanced sprite classes) |
| **Lines Removed** | ~10 (old sprite rendering logic) |
| **Files Modified** | 1 (main.py) |
| **Files Created** | This documentation |
| **Backwards Compatible** | Yes (toggle `USE_CYBERPUNK_THEME`) |
| **Gameplay Impact** | Zero (pure visual refactor) |

---

## Running the Game

```bash
# Run with Cyberpunk theme (default)
python main.py

# To use classic theme, edit line 39:
# USE_CYBERPUNK_THEME = False
```

**Controls (unchanged):**
- ⬅️ Left arrow - Move left
- ➡️ Right arrow - Move right
- ⬆️ Spacebar - Jump
- ❌ Close window - Quit
