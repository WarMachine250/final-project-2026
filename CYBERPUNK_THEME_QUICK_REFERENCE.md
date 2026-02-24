# Cyberpunk Theme - Quick Reference

## 🎮 Run the Game
```bash
python main.py
```

## 🎨 Theme Control (Line 39)
```python
USE_CYBERPUNK_THEME = True   # ← Toggle between themes
```

## 🌈 Color Constants (Lines 16-35)

### Dark Mode
```python
BG_DARK = (5, 5, 15)           # Background
GRID_LINE_COLOR = (20, 25, 50) # Grid lines
```

### Neon Colors
```python
NEON_CYAN = (0, 255, 255)      # Player, platforms, score HUD
NEON_MAGENTA = (255, 0, 255)   # Enemies, level HUD
NEON_PURPLE = (180, 0, 255)    # Accents, borders
NEON_BLUE = (0, 150, 255)      # Platform alternates
NEON_GREEN = (0, 255, 100)     # Reserved
NEON_PINK = (255, 0, 127)      # Reserved
```

## 🎯 Visual Components

### Player (Lines 45-71)
- **Color**: Cyan body + magenta outline + purple lines
- **Size**: 40×60 px (unchanged)
- **Animation**: Frame tracking ready

### Enemy (Lines 103-128)
- **Color**: Magenta circle + purple outline + cyan detail
- **Size**: 35×35 px (circle shape)
- **Behavior**: Patrol (unchanged)

### Collectible (Lines 130-157)
- **Color**: Cyan star + purple outline
- **Size**: 15×15 px
- **Animation**: Bobbing ±3px using sin() wave

### Platform (Lines 159-185)
- **Color**: Neon blue + cyan border
- **Details**: Vertical grid lines every 40px
- **Size**: Variable (width, height)

### HUD (Lines 409-460)
- **Score**: Cyan text, top-right, glowing panel
- **Level**: Magenta text, top-left, glowing panel
- **Animation**: Color shifts cyan↔blue every 10 frames

## ⚙️ Key Methods

### `draw_grid_background()` (Lines 360-383)
- Renders 50px grid with animated scanlines
- Called before sprites in `draw()`

### `draw_ui_panel()` (Lines 385-407)
- Reusable function for neon HUD elements
- Draws background, border, text with glow

### `update()` (Lines 320-352)
- Added `self.collectibles.update()` for animations
- Increments `self.frame_count` for effects

### `draw()` (Lines 409-460)
- **New**: Grid background, glow effects
- **Updated**: Dark background, neon HUD panels

## 🎬 Animations

### Collectible Bobbing (Line 156)
```python
self.bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
```
- Speed: `0.003` (lower = faster)
- Distance: `3` (higher = larger motion)

### HUD Color Pulsing (Line 416)
```python
glow_color = NEON_CYAN if (self.frame_count // 10) % 2 == 0 else NEON_BLUE
```
- Speed: `10` (divide by this, higher = slower)
- Colors: Edit to customize

### Scanline Animation (Line 380)
```python
scanline_y = (self.frame_count * 2) % SCREEN_HEIGHT
```
- Speed: `2` (pixels per frame)

## 🔧 Common Edits

### Change Player Color
```python
# Line 54-55 in __init__
pygame.draw.rect(self.image, NEON_CYAN, (10, 10, 20, 40))      # Main color
pygame.draw.rect(self.image, NEON_MAGENTA, (8, 8, 24, 44), 2)  # Border color
```

### Change Platform Color
```python
# Line 169 in __init__
if USE_CYBERPUNK_THEME:
    if color is None:
        color = NEON_BLUE  # ← Change here
```

### Change Grid Size
```python
# Line 378 in draw_grid_background()
grid_size = 50  # ← Adjust spacing
```

### Change Glow Border Thickness
```python
# Lines 421, 430 in draw()
pygame.draw.rect(self.screen, NEON_CYAN, glow_rect, 2)  # ← 2 = thickness
```

### Disable Scanlines
```python
# Line 379-381 in draw_grid_background()
# Comment out or remove:
# for y in range(0, SCREEN_HEIGHT, 4):
#     opacity_color = tuple(int(c * 0.1) for c in GRID_LINE_COLOR)
```

## 📊 Component Locations

| Component | Lines | Method |
|-----------|-------|--------|
| Player class | 45-113 | `__init__`, `handle_input()`, `apply_gravity()`, `update()` |
| Enemy class | 103-128 | `__init__`, `update()` |
| Collectible class | 130-157 | `__init__`, `update()` |
| Platform class | 159-185 | `__init__` |
| Game `__init__()` | 187-242 | Setup, fonts, sprite groups |
| Game `create_level()` | 244-248 | Level dispatcher |
| Game `update()` | 320-352 | Game logic (UPDATED) |
| Game `draw_grid_background()` | 360-383 | Grid + scanlines (NEW) |
| Game `draw_ui_panel()` | 385-407 | Reusable UI (NEW) |
| Game `draw()` | 409-460 | Rendering (UPDATED) |

## 🎯 For Quick Tweaking

1. **Want classic look?** → Line 39: `USE_CYBERPUNK_THEME = False`
2. **Want different colors?** → Lines 21-27: Edit RGB tuples
3. **Want faster grid?** → Line 378: Change `50` to lower number
4. **Want slower animations?** → Line 416: Change `10` to higher number
5. **Want less glow?** → Lines 421, 430: Change `2` to `1`

## 📁 Files

- **main.py** - Game (552 lines, refactored)
- **CYBERPUNK_THEME_REFACTOR.md** - Full technical documentation
- **CYBERPUNK_THEME_VISUAL_SUMMARY.md** - Design details & justification
- **CYBERPUNK_THEME_QUICK_REFERENCE.md** - This file

## ✅ Verified

✓ Syntax: No errors  
✓ Structure: All methods present  
✓ Constants: All theme vars defined  
✓ Backwards compatible: Can toggle theme  
✓ Gameplay: 100% unchanged  

## 🚀 Ready to Play!

```bash
python main.py
```

Arrow keys to move, spacebar to jump. Enjoy the cyberpunk aesthetic! 🌆✨
