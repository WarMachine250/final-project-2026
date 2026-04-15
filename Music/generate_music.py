#!/usr/bin/env python3
"""
Alien vs Robots - Background Music Generator
Procedurally generates epic sci-fi battle music using numpy and scipy
"""

import numpy as np
from scipy.io import wavfile
import os

def generate_sine_wave(frequency, duration, sample_rate=22050):
    """Generate a sine wave at given frequency"""
    samples = int(duration * sample_rate)
    t = np.arange(samples) / sample_rate
    return np.sin(2 * np.pi * frequency * t)

def generate_square_wave(frequency, duration, sample_rate=22050):
    """Generate a square wave at given frequency"""
    samples = int(duration * sample_rate)
    t = np.arange(samples) / sample_rate
    return np.sign(np.sin(2 * np.pi * frequency * t))

def generate_sawtooth_wave(frequency, duration, sample_rate=22050):
    """Generate a sawtooth wave at given frequency"""
    samples = int(duration * sample_rate)
    t = np.arange(samples) / sample_rate
    phase = (2 * frequency * t) % 2
    return 2 * phase - 1

def create_adsr_envelope(duration, attack=0.05, decay=0.1, sustain=0.7, release=0.15, sample_rate=22050):
    """Create an ADSR envelope"""
    samples = int(duration * sample_rate)
    if samples <= 0:
        return np.array([])
    
    envelope = np.ones(samples)
    
    attack_samples = max(1, int(attack * sample_rate))
    decay_samples = max(1, int(decay * sample_rate))
    release_samples = max(1, int(release * sample_rate))
    
    # Attack phase
    attack_end = min(attack_samples, samples)
    if attack_end > 0:
        envelope[:attack_end] = np.linspace(0, 1, attack_end)
    
    # Decay phase
    decay_start = attack_end
    decay_end = min(decay_start + decay_samples, samples)
    if decay_end > decay_start:
        decay_len = decay_end - decay_start
        envelope[decay_start:decay_end] = np.linspace(1, 0.7, decay_len)
    
    # Release phase (fade to 0 at end)
    release_start = max(samples - release_samples, 0)
    if release_start < samples:
        release_len = samples - release_start
        envelope[release_start:] = np.linspace(0.7, 0, release_len)
    
    return envelope

def generate_battle_music(duration=30, sample_rate=22050):
    """Generate epic sci-fi battle music"""
    samples = int(duration * sample_rate)
    music = np.zeros(samples)
    
    # Main bass line - low frequency drone
    bass_freq = 55  # A1
    bass = generate_sine_wave(bass_freq, duration, sample_rate) * 0.3
    bass_envelope = create_adsr_envelope(duration, attack=0.1, decay=0.2, sustain=0.8, release=0.2)
    music += bass * bass_envelope
    
    # Pulsing mid-range (creates tension)
    mid_freq = 110  # A2
    mid_envelope = create_adsr_envelope(duration, attack=0.05, decay=0.15, sustain=0.6, release=0.1)
    
    # Create pulsing effect (8 pulses per 30 seconds = 3.75s per pulse)
    pulse_length = int(3.75 * sample_rate)
    for i in range(0, samples, pulse_length):
        pulse_end = min(i + pulse_length, samples)
        pulse_samples = pulse_end - i
        pulse = generate_square_wave(mid_freq, pulse_samples / sample_rate, sample_rate)
        pulse_env = create_adsr_envelope(pulse_samples / sample_rate, attack=0.1, decay=0.2, sustain=0.5, release=0.15)
        music[i:pulse_end] += (pulse[:pulse_samples] * pulse_env * 0.25)
    
    # High-frequency arpeggios (heroic melody)
    high_frequencies = [220, 264, 330, 440]  # A3, C#4, E4, A4
    arpeggio_time = 0
    arpeggio_duration = 0.5  # Each note duration
    arpeggio_samples = int(arpeggio_duration * sample_rate)
    
    for t in np.arange(0, duration, arpeggio_duration):
        freq_idx = int((t / arpeggio_duration) % len(high_frequencies))
        freq = high_frequencies[freq_idx]
        start_sample = int(t * sample_rate)
        end_sample = min(start_sample + arpeggio_samples, samples)
        
        if end_sample > start_sample:
            note_duration = (end_sample - start_sample) / sample_rate
            note = generate_sine_wave(freq, note_duration, sample_rate)
            note_envelope = create_adsr_envelope(note_duration, attack=0.02, decay=0.3, sustain=0.4, release=0.15)
            music[start_sample:end_sample] += (note[:end_sample-start_sample] * note_envelope[:end_sample-start_sample] * 0.2)
    
    # Synthesizer swells for dramatic effect
    swell_times = [5, 10, 15, 20, 25]  # Dramatic moments
    for swell_time in swell_times:
        swell_start = int(swell_time * sample_rate)
        swell_duration = 2
        swell_samples = int(swell_duration * sample_rate)
        swell_end = min(swell_start + swell_samples, samples)
        
        if swell_end > swell_start:
            swell_freq = 165  # E3
            swell_len = swell_end - swell_start
            swell = generate_sawtooth_wave(swell_freq, swell_len / sample_rate, sample_rate)
            swell_envelope = create_adsr_envelope(swell_len / sample_rate, attack=0.2, decay=0.5, sustain=0.3, release=0.3)
            music[swell_start:swell_end] += (swell[:swell_len] * swell_envelope[:swell_len] * 0.15)
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(music))
    if max_val > 1:
        music = music / max_val * 0.95
    
    # Convert to 16-bit PCM
    music_int16 = (music * 32767).astype(np.int16)
    
    return music_int16

def generate_menu_music(duration=15, sample_rate=22050):
    """Generate atmospheric menu music"""
    samples = int(duration * sample_rate)
    music = np.zeros(samples)
    
    # Ambient pad - low frequency
    bass_freq = 55  # A1
    bass = generate_sine_wave(bass_freq, duration, sample_rate) * 0.2
    bass_envelope = create_adsr_envelope(duration, attack=0.5, decay=0.5, sustain=0.8, release=1)
    music += bass * bass_envelope
    
    # Melodic pads (slower, atmospheric)
    pad_frequencies = [220, 264, 330]  # A3, C#4, E4
    pad_duration = 3
    pad_samples = int(pad_duration * sample_rate)
    
    for i in range(0, int(duration / pad_duration)):
        start_time = i * pad_duration
        freq = pad_frequencies[i % len(pad_frequencies)]
        start_sample = int(start_time * sample_rate)
        end_sample = min(start_sample + pad_samples, samples)
        
        if end_sample > start_sample:
            note_len = end_sample - start_sample
            note = generate_sine_wave(freq, note_len / sample_rate, sample_rate)
            note_envelope = create_adsr_envelope(note_len / sample_rate, attack=0.3, decay=0.2, sustain=0.8, release=0.5)
            music[start_sample:end_sample] += (note[:note_len] * note_envelope[:note_len] * 0.15)
    
    # Add some shimmer with high frequencies
    shimmer_freq = 880  # A5
    shimmer_samples = int(0.2 * sample_rate)
    shimmer_interval = int(1.5 * sample_rate)
    
    for start in range(0, samples, shimmer_interval):
        end = min(start + shimmer_samples, samples)
        if end > start:
            shimmer_len = end - start
            shimmer = generate_sine_wave(shimmer_freq, shimmer_len / sample_rate, sample_rate)
            shimmer_envelope = create_adsr_envelope(shimmer_len / sample_rate, attack=0.02, decay=0.8, sustain=0, release=0.1)
            music[start:end] += (shimmer[:shimmer_len] * shimmer_envelope[:shimmer_len] * 0.1)
    
    # Normalize
    max_val = np.max(np.abs(music))
    if max_val > 1:
        music = music / max_val * 0.95
    
    music_int16 = (music * 32767).astype(np.int16)
    return music_int16

def generate_boss_music(duration=60, sample_rate=22050):
    """Generate intense boss battle music"""
    samples = int(duration * sample_rate)
    music = np.zeros(samples)
    
    # Heavy bass drum pattern
    drum_pattern = [0.5, 2, 3.5, 4, 6, 7.5, 8, 9.5, 11, 12, 13.5, 14, 15.5, 17, 18, 19.5]
    drum_pattern = drum_pattern + [t + 20 for t in drum_pattern]
    
    for drum_time in drum_pattern:
        if drum_time < duration:
            start_sample = int(drum_time * sample_rate)
            drum_duration = 0.4
            drum_samples = int(drum_duration * sample_rate)
            end_sample = min(start_sample + drum_samples, samples)
            
            if end_sample > start_sample:
                drum_len = end_sample - start_sample
                drum = generate_sine_wave(80, drum_len / sample_rate, sample_rate)
                drum_envelope = create_adsr_envelope(drum_len / sample_rate, attack=0.02, decay=0.35, sustain=0, release=0.03)
                music[start_sample:end_sample] += (drum[:drum_len] * drum_envelope[:drum_len] * 0.4)
    
    # Intense bass line
    bass_freq = 110  # A2
    bass = generate_square_wave(bass_freq, duration, sample_rate) * 0.25
    bass_envelope = create_adsr_envelope(duration, attack=0.05, decay=0.1, sustain=0.8, release=0.2)
    music += bass * bass_envelope
    
    # Stabs - aggressive mid-high notes
    stab_times = np.arange(0.5, duration, 0.75)
    for stab_time in stab_times:
        start_sample = int(stab_time * sample_rate)
        stab_duration = 0.3
        stab_samples = int(stab_duration * sample_rate)
        end_sample = min(start_sample + stab_samples, samples)
        
        if end_sample > start_sample:
            freq = 330 if int(stab_time * 2) % 2 == 0 else 440
            stab_len = end_sample - start_sample
            stab = generate_sine_wave(freq, stab_len / sample_rate, sample_rate)
            stab_envelope = create_adsr_envelope(stab_len / sample_rate, attack=0.05, decay=0.2, sustain=0.3, release=0.05)
            music[start_sample:end_sample] += (stab[:stab_len] * stab_envelope[:stab_len] * 0.3)
    
    # Normalize
    max_val = np.max(np.abs(music))
    if max_val > 1:
        music = music / max_val * 0.95
    
    music_int16 = (music * 32767).astype(np.int16)
    return music_int16

def main():
    print("=" * 50)
    print("Alien vs Robots - Music Generator")
    print("=" * 50)
    print()
    
    # Create assets directory if it doesn't exist
    os.makedirs('assets', exist_ok=True)
    
    sample_rate = 22050
    
    # Generate menu music
    print("Generating assets/menu_music.wav...")
    menu_music = generate_menu_music(duration=15, sample_rate=sample_rate)
    wavfile.write('assets/menu_music.wav', sample_rate, menu_music)
    print("✓ Created assets/menu_music.wav (15 seconds)")
    
    # Generate battle music
    print("Generating assets/battle_music.wav...")
    battle_music = generate_battle_music(duration=30, sample_rate=sample_rate)
    wavfile.write('assets/battle_music.wav', sample_rate, battle_music)
    print("✓ Created assets/battle_music.wav (30 seconds)")
    
    # Generate boss music
    print("Generating assets/boss_music.wav...")
    boss_music = generate_boss_music(duration=60, sample_rate=sample_rate)
    wavfile.write('assets/boss_music.wav', sample_rate, boss_music)
    print("✓ Created assets/boss_music.wav (60 seconds)")
    
    print()
    print("=" * 50)
    print("✓ All music files generated successfully!")
    print("=" * 50)
    print()
    print("Music tracks created in assets/ folder:")
    print("  - menu_music.wav (15s) - Atmospheric title screen")
    print("  - battle_music.wav (30s) - Main gameplay music")
    print("  - boss_music.wav (60s) - Boss battle theme")
    print()
    print("You can now play the game with epic background music!")
    print("Run: python3 main.py")

if __name__ == "__main__":
    main()
