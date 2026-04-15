# Music System Quick Reference

## Play the Game with Music

```bash
python3 main.py
```

## Music Tracks

| Track | Duration | Triggers | Notes |
|-------|----------|----------|-------|
| **menu_music.wav** | 15s | Title screen | Atmospheric, loops |
| **battle_music.wav** | 30s | Levels 1-3 | Epic battle theme, loops |
| **boss_music.wav** | 60s | Level 4 | Intense boss battle, loops |

## Game Flow with Music

```
Start Game
    ↓
[Menu Music] ← Title Screen
    ↓
Press START
    ↓
[Battle Music] ← Level 1 begins
    ↓
Reach Level 2 exit
    ↓
[Battle Music] ← Level 2 begins (same track)
    ↓
Reach Level 3 exit
    ↓
[Battle Music] ← Level 3 begins (same track)
    ↓
Reach Level 4 (Boss Arena)
    ↓
[Boss Music] ← Boss Level begins (different track!)
    ↓
Defeat Boss
    ↓
[Music Stops] ← Victory screen shown
    ↓
R key or Button
    ↓
[Menu Music] ← Back to title screen
```

## Key Code Locations

**Music Integration Points in `main.py`:**

1. **Line ~960:** `self.current_music = None` - State tracking in `__init__()`
2. **Line ~1363:** `self.play_level_music()` - Called when starting game
3. **Line ~1378:** `play_level_music()` method - Selects correct track
4. **Line ~1435:** `self.play_level_music()` - Called in `load_next_level()`
5. **Line ~1830:** Title screen music in `draw()` method

## Regenerate Music

If you want to recreate the music files:

```bash
python3 generate_music.py
```

This will:
- ✅ Create `assets/menu_music.wav` (15s)
- ✅ Create `assets/battle_music.wav` (30s)
- ✅ Create `assets/boss_music.wav` (60s)

## Quick Customizations

### Change Battle Music Duration (30s → 60s)

**File:** `generate_music.py`, line ~244
```python
# BEFORE:
battle_music = generate_battle_music(duration=30, sample_rate=sample_rate)

# AFTER:
battle_music = generate_battle_music(duration=60, sample_rate=sample_rate)
```

Then run: `python3 generate_music.py`

### Make Bass Louder

**File:** `generate_music.py`, line ~77 in `generate_battle_music()`
```python
# BEFORE:
music += bass * bass_envelope

# AFTER (make 2x louder):
music += bass * bass_envelope * 2
```

Then regenerate: `python3 generate_music.py`

### Make Boss Music Even More Intense

**File:** `generate_music.py`, line ~145 in `generate_boss_music()`

Increase drum volume:
```python
# BEFORE:
music[start_sample:end_sample] += (drum[:drum_len] * drum_envelope[:drum_len] * 0.4)

# AFTER (increase to 0.6):
music[start_sample:end_sample] += (drum[:drum_len] * drum_envelope[:drum_len] * 0.6)
```

### Disable Music Temporarily

**Option 1:** Rename music files (game continues without music)
```bash
mv assets/menu_music.wav assets/menu_music.wav.bak
```

**Option 2:** In `main.py`, comment out in `play_level_music()`:
```python
def play_level_music(self):
    return  # Skip music loading
```

### Enable Music After Disabling

```bash
# Restore music files if renamed
mv assets/menu_music.wav.bak assets/menu_music.wav

# Or regenerate them:
python3 generate_music.py
```

## Audio File Details

**All files are located in:** `assets/` folder

```
assets/
├── menu_music.wav       646 KB   ← Title screen
├── battle_music.wav     1.3 MB   ← Levels 1-3
├── boss_music.wav       2.5 MB   ← Level 4
└── ... (other sound effects)
```

## Music System Behavior

| Scenario | Behavior |
|----------|----------|
| Title screen shown | Menu music loops |
| Player presses START | Music switches to battle |
| Player advances level (1→2, 2→3) | Battle music continues |
| Player reaches boss level (→4) | Music switches to boss |
| Boss defeated | Music stops |
| Player clicks RESTART | Stays on result screen, music silent |
| Player returns to title | Menu music resumes |

## Common Issues & Fixes

**Q: No music plays**
- A: Run `python3 generate_music.py`

**Q: Music only plays for 15 seconds**
- A: Verify `-1` loop flag in `play_level_music()` - should be: `pygame.mixer.music.play(-1)`

**Q: Music changes abruptly between levels**
- A: This is intentional! Boss level (4) has its own intense track

**Q: Can I add custom music?**
- A: Yes! Create new WAV file in `assets/`, then add function to `generate_music.py` or load your own file

**Q: How do I make music louder/quieter?**
- A: Regenerate with adjusted multipliers in `generate_music.py` (lines 77, 145, etc.), or adjust system volume

## Dependencies

Music system requires:
- `pygame.mixer` (included with Pygame)
- `numpy` (for generation)
- `scipy` (for generation)

Pygame version: 2.6.1+

## Files to Know

| File | Purpose |
|------|---------|
| `generate_music.py` | Creates WAV files from scratch |
| `main.py` | Plays music based on game state |
| `assets/menu_music.wav` | Title screen music |
| `assets/battle_music.wav` | Gameplay music |
| `assets/boss_music.wav` | Boss battle music |

## Next Steps

- 🎵 **Play the game:** `python3 main.py`
- 🎚️ **Customize music:** Edit `generate_music.py`, then regenerate
- 🎼 **Add new tracks:** Create generation function, add to `main()`, use in game
- 🔊 **Adjust volume:** Modify multipliers in generation functions

---

**Your game is now ready with epic background music!** 🎵⚔️
