import numpy as np
import scipy.fftpack
import pygame
import sys
from pydub import AudioSegment
from pydub.utils import get_array_type
from pygame import mixer
import time

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Audio Visualization')

mixer.init()

audio_file = '/home/akindu/Documents/Academic Projects/light-show/audiofile.mp3'
audio = AudioSegment.from_mp3(audio_file)

channels = audio.channels
sample_width = audio.sample_width
frame_rate = audio.frame_rate
frame_count = len(audio)

raw_data = audio.raw_data

chunk_size = 1024

SNARE_MIN = 1500
SNARE_MAX = 3000

array_type = get_array_type(audio.sample_width * 8)
samples = np.frombuffer(raw_data, dtype=array_type)

if channels == 2:
    samples = samples.reshape((-1, 2))
    samples = samples.mean(axis=1)

def detect_snare(audio_chunk):
    fft_data = np.abs(scipy.fftpack.fft(audio_chunk))[:chunk_size // 2]
    freqs = np.fft.fftfreq(len(fft_data), 1.0/frame_rate)[:chunk_size // 2]
    snare_freqs = (freqs >= SNARE_MIN) & (freqs <= SNARE_MAX)
    snare_energy = np.sum(fft_data[snare_freqs])
    threshold = 1e7
    return snare_energy > threshold

mixer.music.load(audio_file)
mixer.music.play()

flicker_duration = 0.1
last_flicker_time = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
current_color = 0

font = pygame.font.Font(None, 100)
text = font.render('AK', True, (255, 255, 255))
text_rect = text.get_rect(center=(400, 300))

chunk_start_time = time.time()

try:
    while mixer.music.get_busy():
        for i in range(0, len(samples), chunk_size):
            audio_chunk = samples[i:i + chunk_size]
            if len(audio_chunk) < chunk_size:
                break
            
            if detect_snare(audio_chunk):
                current_time = time.time()
                if current_time - last_flicker_time > flicker_duration:
                    screen.fill(colors[current_color])
                    screen.blit(text, text_rect)
                    pygame.display.flip()
                    time.sleep(flicker_duration / 2)
                    screen.fill((0, 0, 0))
                    screen.blit(text, text_rect)
                    pygame.display.flip()
                    last_flicker_time = current_time
                    current_color = (current_color + 1) % len(colors)
            
            while time.time() - chunk_start_time < chunk_size / frame_rate:
                time.sleep(0.001)
            chunk_start_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mixer.music.stop()
                    pygame.quit()
                    sys.exit()

except KeyboardInterrupt:
    mixer.music.stop()
    pygame.quit()
