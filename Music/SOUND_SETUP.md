# Sound System Setup Guide

Your game now has a complete sound system integrated! Here's how to add audio files:

## Quick Start

1. Create an `assets` folder in the project root if you don't already have one
2. Add sound files (`.wav` or `.mp3` format) with these names:
   - `laser.wav` - Laser firing sound
   - `bullet.wav` - Bullet firing sound
   - `explosion.wav` - Enemy explosion sound
   - `enemy_hit.wav` - When player shoots enemy
   - `boss_hit.wav` - When player hits boss
   - `boss_defeated.wav` - When boss is defeated
   - `game_over.wav` - Game over sound
   - `victory.wav` - Victory fanfare
   - `jump.wav` - Player jump sound (ready to use)
   - `collect.wav` - Collectible pickup sound

## Where to Get Free Sounds

### Free Sound Resources:
- **Freesound.org** - https://freesound.org (search for sci-fi, laser, explosion, etc.)
- **OpenGameArt.org** - https://opengameart.org/art-search?keys=sfx
- **Zapsplat** - https://www.zapsplat.com (free sound effects)
- **Pixabay** - https://pixabay.com/sound-effects/ (royalty-free)
- **YouTube Audio Library** - Free background music and SFX

### Recommended Searches:
- **Laser**: "laser gun", "sci-fi laser", "blaster"
- **Explosion**: "explosion", "boom", "impact"
- **Victory**: "victory fanfare", "success", "cheer"
- **Game Over**: "fail", "game over", "defeat"
- **Boss Hit**: "impact", "hit", "damage"

## Sound System Features

### Automatic Features:
✅ Sounds trigger on:
- Laser firing (Ctrl key or left mouse)
- Bullet firing (E key or right mouse)
- Enemy hit by laser/bullet
- Boss hit by laser/bullet
- Boss defeated
- Collectible collected
- Player death (game over)
- Victory achieved

### Volume Control:
The sound manager includes functions for:
- `set_volume(0.0 to 1.0)` - Adjust overall volume
- `toggle_sound()` - Turn sound effects on/off
- `toggle_music()` - Turn music on/off
- `play_music(file_path)` - Play background music

### Note:
- Sounds are optional - the game works fine without them
- If a sound file is missing, the game silently continues
- Only `.wav` and `.mp3` files are supported

## Example: Adding Background Music

To add background music, add this to the `run()` method:

```python
# In the run method, after game starts
self.sound_manager.play_music('assets/battle_music.mp3')
```

Or add it to `start_game()` method in the Game class:

```python
def start_game(self):
    # ... existing code ...
    self.sound_manager.play_music('assets/battle_music.mp3', loops=-1)
```

## File Format Requirements

- **Supported formats**: `.wav`, `.mp3`
- **Sample rate**: 22050 Hz or higher recommended
- **File size**: Keep under 1MB for best performance
- **Channels**: Mono or Stereo

## Troubleshooting

**Q: Game runs but no sound plays**
- Check that sound files are in the `assets` folder
- Verify filenames match exactly (case-sensitive on macOS)
- Check file format is `.wav` or `.mp3`

**Q: How do I test if sounds are working?**
- In Python REPL:
```python
import pygame
pygame.mixer.init()
sound = pygame.mixer.Sound('assets/laser.wav')
sound.play()
```

**Q: Can I use different sound effects for different actions?**
- Yes! Add custom sounds by modifying the `SoundManager.load_sounds()` method
- Update the `sound_files` dictionary with new sounds
- Call `self.sound_manager.play_sound('custom_sound_name')` where needed

## Epic Battle Music Recommendations

For that authentic sci-fi war atmosphere, search for:
- "Intense Space Battle Music"
- "Cyberpunk Action Music"
- "Sci-Fi Electronic Battle Theme"
- "Epic Space War Soundtrack"

Licensed free options:
- Epidemic Sound (free trial)
- Artlist (free trial)
- AudioJungle (premium, but has free packs)

---

**Your game is ready for epic audio!** 🎵⚔️
