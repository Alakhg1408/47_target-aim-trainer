import os
import math
import wave
import struct
import pygame

def ensure_sound_assets(sounds_dir):
    os.makedirs(sounds_dir, exist_ok=True)
    hit_path = os.path.join(sounds_dir, "hit.wav")
    miss_path = os.path.join(sounds_dir, "miss.wav")
    game_over_path = os.path.join(sounds_dir, "game_over.wav")

    if not os.path.exists(hit_path):
        _generate_hit_wav(hit_path)
    if not os.path.exists(miss_path):
        _generate_miss_wav(miss_path)
    if not os.path.exists(game_over_path):
        _generate_game_over_wav(game_over_path)

def _generate_hit_wav(path):
    sample_rate = 44100
    duration = 0.12
    n_samples = int(sample_rate * duration)
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            env = math.exp(-25 * t)
            sample = 0.7 * math.sin(2 * math.pi * 950 * t) + 0.3 * math.sin(2 * math.pi * 1425 * t)
            val = int(sample * env * 32767 * 0.7)
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wav.writeframes(frames)

def _generate_miss_wav(path):
    sample_rate = 44100
    duration = 0.16
    n_samples = int(sample_rate * duration)
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            freq = 220 - 140 * (t / duration)
            env = math.exp(-15 * t)
            sample = math.sin(2 * math.pi * freq * t)
            val = int(sample * env * 32767 * 0.6)
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wav.writeframes(frames)

def _generate_game_over_wav(path):
    sample_rate = 44100
    notes = [523.25, 659.25, 783.99, 1046.50]
    note_duration = 0.14
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for note_idx, freq in enumerate(notes):
            n_samples = int(sample_rate * note_duration)
            for i in range(n_samples):
                t = i / sample_rate
                decay = 6 if note_idx == len(notes) - 1 else 14
                env = math.exp(-decay * t)
                sample = 0.75 * math.sin(2 * math.pi * freq * t) + 0.25 * math.sin(2 * math.pi * freq * 2 * t)
                val = int(sample * env * 32767 * 0.65)
                frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wav.writeframes(frames)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sounds_dir = os.path.join(base_dir, "assets", "sounds")
            ensure_sound_assets(sounds_dir)

            for name in ("hit", "miss", "game_over"):
                path = os.path.join(sounds_dir, f"{name}.wav")
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Warning: SoundManager initialization skipped/failed: {e}")

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass
