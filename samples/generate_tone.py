from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

output = Path(__file__).with_name("demo-tone.wav")
sample_rate = 16_000
seconds = 3
frequency = 440.0
amplitude = 0.35

with wave.open(str(output), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)

    frames = bytearray()
    for index in range(sample_rate * seconds):
        value = int(
            amplitude
            * 32767
            * math.sin(2 * math.pi * frequency * index / sample_rate)
        )
        frames.extend(struct.pack("<h", value))

    wav.writeframes(frames)

print(f"Created {output}")
