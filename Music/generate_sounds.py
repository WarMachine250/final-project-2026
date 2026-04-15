"""
Generate sound effects procedurally for Alien vs Robots game.
Run this script to create all necessary sound files in the assets folder.
"""

import numpy as np
import os
from scipy.io import wavfile

# Create assets folder if it doesn't exist
os.makedirs('assets', exist_ok=True)

def save_wav_file(audio_data, filename, sample_rate=22050):
    """Save audio data as WAV file."""
    wavfile.write(filename, sample_rate, audio_data)

def generate_sine_wave(frequency, duration, sample_rate=22050):
    """Generate a sine wave at given frequency for given duration."""
    samples = np.arange(int(sample_rate * duration))
    waveform = np.sin(2 * np.pi * frequency * samples / sample_rate)
    return waveform.astype(np.float32)

def generate_square_wave(frequency, duration, sample_rate=22050):
    """Generate a square wave at given frequency for given duration."""
    samples = np.arange(int(sample_rate * duration))
    waveform = np.sign(np.sin(2 * np.pi * frequency * samples / sample_rate))
    return waveform.astype(np.float32)

def create_laser_sound(filename='assets/laser.wav'):
    """Create a sci-fi laser sound effect."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 0.3
    samples = np.arange(int(sample_rate * duration))
    
    frequencies = np.linspace(800, 400, len(samples))
    phase = 2 * np.pi * np.cumsum(frequencies) / sample_rate
    waveform = np.sin(phase)
    envelope = np.linspace(1, 0, len(waveform))
    waveform = waveform * envelope * 0.7
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_bullet_sound(filename='assets/bullet.wav'):
    """Create a bullet/pew sound effect."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 0.15
    waveform = generate_sine_wave(1200, duration, sample_rate)
    envelope = np.linspace(1, 0, int(sample_rate * duration))
    waveform = waveform * envelope * 0.6
    waveform += generate_sine_wave(2400, duration, sample_rate) * 0.3 * envelope
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_explosion_sound(filename='assets/explosion.wav'):
    """Create an explosion sound effect."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 0.8
    samples = np.arange(int(sample_rate * duration))
    waveform = np.zeros_like(samples, dtype=np.float32)
    
    waveform += generate_sine_wave(150, duration, sample_rate) * 0.5
    waveform += generate_sine_wave(80, duration, sample_rate) * 0.3
    waveform += generate_square_wave(400, duration, sample_rate) * 0.2
    noise = np.random.randn(len(samples)).astype(np.float32) * 0.15
    waveform += noise
    
    envelope = np.exp(-3 * samples / (sample_rate * duration))
    waveform = waveform * envelope
    waveform = waveform / np.max(np.abs(waveform)) * 0.8
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_hit_sound(filename='assets/enemy_hit.wav', pitch=600):
    """Create a hit/impact sound effect."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 0.2
    samples = np.arange(int(sample_rate * duration))
    waveform = generate_square_wave(pitch, duration, sample_rate) * 0.6
    envelope = np.exp(-8 * samples / (sample_rate * duration))
    waveform = waveform * envelope
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_victory_sound(filename='assets/victory.wav'):
    """Create a victory fanfare sound."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 1.5
    samples = np.arange(int(sample_rate * duration))
    waveform = np.zeros_like(samples, dtype=np.float32)
    
    part1_len = int(sample_rate * 0.3)
    waveform[:part1_len] += generate_sine_wave(262, 0.3, sample_rate) * 0.4
    waveform[:part1_len] += generate_sine_wave(330, 0.3, sample_rate) * 0.3
    waveform[:part1_len] += generate_sine_wave(392, 0.3, sample_rate) * 0.3
    
    part2_start = part1_len
    part2_len = int(sample_rate * 0.3)
    waveform[part2_start:part2_start+part2_len] += generate_sine_wave(330, 0.3, sample_rate) * 0.4
    waveform[part2_start:part2_start+part2_len] += generate_sine_wave(392, 0.3, sample_rate) * 0.3
    waveform[part2_start:part2_start+part2_len] += generate_sine_wave(494, 0.3, sample_rate) * 0.3
    
    part3_start = part2_start + part2_len
    part3_len = int(sample_rate * 0.3)
    waveform[part3_start:part3_start+part3_len] += generate_sine_wave(392, 0.3, sample_rate) * 0.4
    waveform[part3_start:part3_start+part3_len] += generate_sine_wave(494, 0.3, sample_rate) * 0.3
    waveform[part3_start:part3_start+part3_len] += generate_sine_wave(587, 0.3, sample_rate) * 0.3
    
    part4_start = part3_start + part3_len
    part4_len = int(sample_rate * 0.6)
    waveform[part4_start:part4_start+part4_len] += generate_sine_wave(523, 0.6, sample_rate) * 0.5
    waveform[part4_start:part4_start+part4_len] += generate_sine_wave(659, 0.6, sample_rate) * 0.4
    waveform[part4_start:part4_start+part4_len] += generate_sine_wave(784, 0.6, sample_rate) * 0.4
    
    envelope = np.linspace(1, 0, len(waveform))
    waveform = waveform * envelope
    waveform = waveform / np.max(np.abs(waveform)) * 0.7
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_game_over_sound(filename='assets/game_over.wav'):
    """Create a game over sound effect."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 1.0
    samples = np.arange(int(sample_rate * duration))
    frequencies = np.linspace(500, 200, len(samples))
    phase = 2 * np.pi * np.cumsum(frequencies) / sample_rate
    waveform = np.sin(phase)
    envelope = np.exp(-2 * samples / (sample_rate * duration))
    waveform = waveform * envelope * 0.6
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_boss_hit_sound(filename='assets/boss_hit.wav'):
    """Create a heavy impact sound for boss hits."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 0.4
    samples = np.arange(int(sample_rate * duration))
    waveform = generate_sine_wave(200, duration, sample_rate) * 0.6
    waveform += generate_sine_wave(100, duration, sample_rate) * 0.4
    noise = np.random.randn(len(samples)).astype(np.float32) * 0.1
    waveform += noise
    envelope = np.exp(-6 * samples / (sample_rate * duration))
    waveform = waveform * envelope
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_boss_defeated_sound(filename='assets/boss_defeated.wav'):
    """Create a boss defeated fanfare sound."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 1.2
    samples = np.arange(int(sample_rate * duration))
    waveform = np.zeros_like(samples, dtype=np.float32)
    
    part1_len = int(sample_rate * 0.3)
    waveform[:part1_len] += generate_sine_wave(220, 0.3, sample_rate) * 0.4
    waveform[:part1_len] += generate_sine_wave(262, 0.3, sample_rate) * 0.4
    waveform[:part1_len] += generate_sine_wave(330, 0.3, sample_rate) * 0.3
    
    part2_start = part1_len
    part2_len = int(sample_rate * 0.3)
    waveform[part2_start:part2_start+part2_len] += generate_sine_wave(262, 0.3, sample_rate) * 0.4
    waveform[part2_start:part2_start+part2_len] += generate_sine_wave(330, 0.3, sample_rate) * 0.4
    waveform[part2_start:part2_start+part2_len] += generate_sine_wave(392, 0.3, sample_rate) * 0.3
    
    part3_start = part2_start + part2_len
    part3_len = int(sample_rate * 0.6)
    waveform[part3_start:part3_start+part3_len] += generate_sine_wave(392, 0.6, sample_rate) * 0.4
    waveform[part3_start:part3_start+part3_len] += generate_sine_wave(523, 0.6, sample_rate) * 0.4
    waveform[part3_start:part3_start+part3_len] += generate_sine_wave(659, 0.6, sample_rate) * 0.3
    
    envelope = np.linspace(1, 0, len(waveform))
    waveform = waveform * envelope
    waveform = waveform / np.max(np.abs(waveform)) * 0.7
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def create_collect_sound(filename='assets/collect.wav'):
    """Create a collectible pickup sound effect."""
    print(f"Generating {filename}...")
    
    sample_rate = 22050
    duration = 0.3
    samples = np.arange(int(sample_rate * duration))
    waveform = np.zeros_like(samples, dtype=np.float32)
    
    part1_len = int(sample_rate * 0.1)
    waveform[:part1_len] += generate_sine_wave(523, 0.1, sample_rate)
    
    part2_start = part1_len
    part2_len = int(sample_rate * 0.1)
    waveform[part2_start:part2_start+part2_len] += generate_sine_wave(659, 0.1, sample_rate)
    
    part3_start = part2_start + part2_len
    part3_len = int(sample_rate * 0.1)
    waveform[part3_start:part3_start+part3_len] += generate_sine_wave(784, 0.1, sample_rate)
    
    envelope = np.linspace(1, 0, len(waveform))
    waveform = waveform * envelope * 0.6
    
    audio_data = np.int16(waveform * 32767)
    stereo = np.zeros((len(audio_data), 2), dtype=np.int16)
    stereo[:, 0] = audio_data
    stereo[:, 1] = audio_data
    
    save_wav_file(stereo, filename)
    print(f"✓ Created {filename}")

def main():
    print("=" * 50)
    print("Alien vs Robots - Sound Generator")
    print("=" * 50)
    print()
    
    create_laser_sound()
    create_bullet_sound()
    create_explosion_sound()
    create_hit_sound('assets/enemy_hit.wav', pitch=600)
    create_boss_hit_sound()
    create_boss_defeated_sound()
    create_victory_sound()
    create_game_over_sound()
    create_collect_sound()
    
    print()
    print("=" * 50)
    print("✓ All sounds generated successfully!")
    print("=" * 50)
    print()
    print("Sounds created in assets/ folder:")
    print("  - laser.wav")
    print("  - bullet.wav")
    print("  - explosion.wav")
    print("  - enemy_hit.wav")
    print("  - boss_hit.wav")
    print("  - boss_defeated.wav")
    print("  - victory.wav")
    print("  - game_over.wav")
    print("  - collect.wav")
    print()
    print("You can now play the game with full sound effects!")
    print("Run: python3 main.py")

if __name__ == '__main__':
    main()
