# Background Music System - Alien vs Robots

## Overview

Your game now includes a complete epic sci-fi background music system with three contextual music tracks that automatically play based on game state.

## Music Tracks

### 1. **Menu Music** (`menu_music.wav`) - 15 seconds
- **Purpose:** Plays on title screen
- **Style:** Atmospheric ambient pad with ethereal shimmer
- **Composition:**
  - Low frequency bass drone (A1 - 55Hz)
  - Slow melodic pad progression (A3, C#4, E4)
  - High-frequency shimmer effects
  - Loops seamlessly for title screen atmosphere

### 2. **Battle Music** (`battle_music.wav`) - 30 seconds
- **Purpose:** Plays for Levels 1-3 (main gameplay)
- **Style:** Epic sci-fi battle theme with heroic elements
- **Composition:**
  - Steady bass foundation (A1 drone)
  - Pulsing mid-range tension layer (A2 square wave)
  - Heroic arpeggio melody (A3, C#4, E4, A4)
  - Dramatic synthesizer swells for peak moments
  - Loops for extended gameplay sessions

### 3. **Boss Music** (`boss_music.wav`) - 60 seconds
- **Purpose:** Plays for Level 4 (boss arena)
- **Style:** Intense, aggressive, epic boss battle theme
- **Composition:**
  - Heavy drum pattern (80Hz kicks at key moments)
  - Aggressive square wave bass line (A2)
  - Rapid melodic stabs (alternating E4 and A4)
  - Builds intense tension throughout the 60 seconds
  - Loops for extended boss battle

## How It Works

### Automatic Music Switching

The game automatically plays the appropriate music based on game state:

```
Title Screen
    ↓
[Menu Music Plays]
    ↓
Player Clicks START
    ↓
[Battle Music Plays] ← Levels 1-3
    ↓
Reach Level 4 (Boss)
    ↓
[Boss Music Plays] ← Level 4 only
    ↓
Victory/Game Over
    ↓
[Music Stops, Returns to Menu]
```

### Implementation Details

**Core Music Methods:**

1. **`play_level_music()`**
   - Called whenever player enters a new level
   - Checks `self.level` to determine which track to play
   - Levels 1-3 → Battle Music
   - Level 4 → Boss Music
   - Automatically loops with `-1` flag

2. **`start_game()`**
   - Stops menu music
   - Calls `play_level_music()` to start battle music for Level 1

3. **`load_next_level()`**
   - Called when player reaches level end
   - Calls `play_level_music()` to play appropriate track for new level

4. **`draw()`**
   - On title screen: Loads and plays menu music if not already playing
   - Tracks current music state in `self.current_music` to avoid reloading

### State Tracking

```python
# In Game.__init__():
self.music_playing = False      # Whether music is active
self.current_music = None       # Current playing track: "menu", "battle", "boss"
```

## Technical Details

### Audio Specifications
- **Format:** WAV (uncompressed)
- **Sample Rate:** 22050 Hz (Pygame standard)
- **Bit Depth:** 16-bit PCM
- **Channels:** Mono
- **File Sizes:**
  - Menu: 646 KB (15s)
  - Battle: 1.3 MB (30s)
  - Boss: 2.5 MB (60s)

### Procedural Generation

All music is generated using NumPy and SciPy waveform synthesis:

**Waveform Types Used:**
- `generate_sine_wave()` - Smooth tones, bass foundations
- `generate_square_wave()` - Aggressive, mechanical sounds
- `generate_sawtooth_wave()` - Bright, cutting sounds
- `create_adsr_envelope()` - Dynamic sound shaping

**Generation Script:** `generate_music.py`
```bash
python3 generate_music.py
```

## Customization

### Adjust Music Duration

Edit `generate_music.py`:
```python
# Change duration in main():
menu_music = generate_music(duration=20)    # 20 seconds instead of 15
battle_music = generate_battle_music(duration=45)  # 45 seconds instead of 30
```

### Modify Music Style

Each generation function has tweakable parameters:

```python
def generate_battle_music(duration=30, sample_rate=22050):
    # Adjust bass frequency
    bass_freq = 110  # Change this for higher/lower bass
    
    # Adjust pulse tempo
    pulse_length = int(3.75 * sample_rate)  # Slower = larger number
    
    # Adjust volume levels
    music += bass * bass_envelope * 0.3  # Change multiplier
```

### Add New Music Tracks

1. Create a new generation function in `generate_music.py`:
```python
def generate_victory_music(duration=15, sample_rate=22050):
    # Create celebratory fanfare
    pass
```

2. Call it in `main()`:
```python
victory_music = generate_victory_music(duration=15, sample_rate=sample_rate)
wavfile.write('assets/victory_music.wav', sample_rate, victory_music)
```

3. Use it in `main.py`:
```python
def play_victory_music(self):
    pygame.mixer.music.load('assets/victory_music.wav')
    pygame.mixer.music.play(0)  # Play once (no loop)
```

## Muting Music

To temporarily disable music without removing the system:

```python
# In Game.__init__() or anywhere:
self.music_enabled = False

# In play_level_music():
if self.music_enabled:
    pygame.mixer.music.load(...)
    pygame.mixer.music.play(-1)
```

Or stop music entirely:
```python
pygame.mixer.music.stop()
```

## Troubleshooting

### "Could not load music" Error
- Check that `assets/` folder exists
- Verify `.wav` files are in the assets folder
- Ensure filenames are exactly: `menu_music.wav`, `battle_music.wav`, `boss_music.wav`
- Run `python3 generate_music.py` to regenerate files

### Music Not Looping
- Ensure `-1` flag is used: `pygame.mixer.music.play(-1)`
- Use `0` for single play, `-1` for infinite loop

### Music Plays Too Quietly
- Adjust volume in `generate_music.py` generation functions
- Multiply envelope values by larger numbers (e.g., 0.3 → 0.5)
- Regenerate and test

### Music Doesn't Switch Between Levels
- Check that `play_level_music()` is called in `load_next_level()`
- Verify `self.level` is being incremented correctly
- Check `self.current_music` tracking (should show "battle" or "boss")

## Future Enhancements

### Planned Features
- [ ] Music volume slider in settings menu
- [ ] Victory fanfare track for game completion
- [ ] Dynamic music that changes based on player health
- [ ] Music crossfading between tracks
- [ ] Different difficulty music variations

### Extended Soundtrack Possibilities
- **Alien Ship Background Themes** - One for each alien faction
- **Leitmotif System** - Boss theme variations for each boss type
- **Dynamic Events** - Music intensifies when player takes damage
- **Level-Specific Themes** - Custom tracks for each level

## File Structure

```
assets/
├── menu_music.wav           (15s, title screen)
├── battle_music.wav         (30s, levels 1-3)
├── boss_music.wav           (60s, level 4)
├── laser.wav                (sound effect)
├── bullet.wav               (sound effect)
├── explosion.wav            (sound effect)
├── enemy_hit.wav            (sound effect)
├── boss_hit.wav             (sound effect)
├── boss_defeated.wav        (sound effect)
├── victory.wav              (sound effect)
├── game_over.wav            (sound effect)
└── collect.wav              (sound effect)

generate_music.py           (Music generation script)
main.py                     (Integrated with music system)
```

## Credits

All music tracks are procedurally generated using:
- **NumPy** - Waveform synthesis and signal processing
- **SciPy** - WAV file I/O and audio writing
- **Pygame Mixer** - Audio playback in-game

## Summary

Your game now has an epic, fully integrated music system that:
✅ Automatically adapts to game state
✅ Loops seamlessly for uninterrupted gameplay
✅ Features three distinct contextual tracks
✅ Uses procedurally generated sci-fi sounds
✅ Integrates perfectly with existing sound effects
✅ Completely customizable through `generate_music.py`

**Ready to play with epic background music!** 🎵⚔️

Run the game:
```bash
python3 main.py
```
