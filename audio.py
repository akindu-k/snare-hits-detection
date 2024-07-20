import numpy as np
import scipy.fftpack
import pygame
import sys
from pydub import AudioSegment
from pydub.utils import get_array_type
from pygame import mixer
import time

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Audio Visualization')

# Initialize Pygame mixer
mixer.init()

# Open the audio file
audio_file = '/home/akindu/Documents/Academic Projects/light-show/audiofile1.mp3'
audio = AudioSegment.from_mp3(audio_file)

# Audio file parameters
channels = audio.channels
sample_width = audio.sample_width
frame_rate = audio.frame_rate
frame_count = len(audio)

# Convert audio to raw data
raw_data = audio.raw_data

# Parameters for processing
chunk_size = 1024

# Frequency range for snare hits (typically 1500-3000 Hz)
SNARE_MIN = 1500
SNARE_MAX = 3000

# Frequency range for bass (typically 20-250 Hz)
BASS_MIN = 20
BASS_MAX = 250

# Determine the array type for the audio samples
array_type = get_array_type(audio.sample_width * 8)
samples = np.frombuffer(raw_data, dtype=array_type)

# Normalize the samples if stereo
if channels == 2:
    samples = samples.reshape((-1, 2))
    samples = samples.mean(axis=1)  # Convert to mono by averaging channels

def detect_frequency(audio_chunk, freq_min, freq_max):
    # Apply Fourier Transform
    fft_data = np.abs(scipy.fftpack.fft(audio_chunk))[:chunk_size // 2]
    
    # Frequency bins
    freqs = np.fft.fftfreq(len(fft_data), 1.0/frame_rate)[:chunk_size // 2]
    
    # Find frequencies in the specified range
    freq_range = (freqs >= freq_min) & (freqs <= freq_max)
    
    # Calculate energy in the specified frequency range
    energy = np.sum(fft_data[freq_range])
    
    # Threshold for detecting frequency hit
    threshold = 1e7
    
    return energy > threshold

# Load the audio file into the mixer
mixer.music.load(audio_file)

# Start playing the audio
mixer.music.play()

# Variables to manage flicker timing and color changes
flicker_duration = 0.1  # Duration for flickering (seconds)
last_snare_flicker_time = 0
last_bass_flicker_time = 0

# Use blue for treble (snare) and red for bass
snare_color = (0, 0, 255)  # Blue
bass_color = (255, 0, 0)  # Red

# Initialize Pygame font
font = pygame.font.Font(None, 100)  # None uses default font, 100 is font size
snare_text = font.render('TREBLE', True, (255, 255, 255))  # White color text
snare_text_rect = snare_text.get_rect(center=(200, 300))  # Center the text in left half
bass_text = font.render('BASS', True, (255, 255, 255))  # White color text
bass_text_rect = bass_text.get_rect(center=(600, 300))  # Center the text in right half

chunk_start_time = time.time()

try:
    # Loop until the music stops playing
    while mixer.music.get_busy():
        for i in range(0, len(samples), chunk_size):
            # Get the current chunk of audio data
            audio_chunk = samples[i:i + chunk_size]
            if len(audio_chunk) < chunk_size:
                break  # If the chunk is smaller than chunk_size, break the loop
            
            # Check for snare hit
            if detect_frequency(audio_chunk, SNARE_MIN, SNARE_MAX):
                current_time = time.time()
                if current_time - last_snare_flicker_time > flicker_duration:
                    # Flicker the snare section with blue color
                    screen.fill(snare_color, rect=[0, 0, 400, 600])
                    screen.blit(snare_text, snare_text_rect)  # Draw the text in snare section
                    pygame.display.flip()
                    time.sleep(flicker_duration / 2)  # Brief pause for flicker effect
                    screen.fill((0, 0, 0), rect=[0, 0, 400, 600])  # Black color in snare section
                    screen.blit(snare_text, snare_text_rect)  # Draw the text again in snare section
                    pygame.display.flip()
                    last_snare_flicker_time = current_time
            
            # Check for bass hit
            if detect_frequency(audio_chunk, BASS_MIN, BASS_MAX):
                current_time = time.time()
                if current_time - last_bass_flicker_time > flicker_duration:
                    # Flicker the bass section with red color
                    screen.fill(bass_color, rect=[400, 0, 400, 600])
                    screen.blit(bass_text, bass_text_rect)  # Draw the text in bass section
                    pygame.display.flip()
                    time.sleep(flicker_duration / 2)  # Brief pause for flicker effect
                    screen.fill((0, 0, 0), rect=[400, 0, 400, 600])  # Black color in bass section
                    screen.blit(bass_text, bass_text_rect)  # Draw the text again in bass section
                    pygame.display.flip()
                    last_bass_flicker_time = current_time

            # Sync with audio playback
            while time.time() - chunk_start_time < chunk_size / frame_rate:
                time.sleep(0.0001)
            chunk_start_time = time.time()

            # Event handling to allow quitting the program
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mixer.music.stop()
                    pygame.quit()
                    sys.exit()

except KeyboardInterrupt:
    # Gracefully close everything on keyboard interrupt
    mixer.music.stop()
    pygame.quit()
