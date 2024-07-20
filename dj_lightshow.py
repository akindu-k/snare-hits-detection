import numpy as np
from pydub import AudioSegment
from scipy.signal import find_peaks
import simpleaudio as sa
import tkinter as tk
import time

# Function to detect beats in the audio
def detect_beats(samples, sample_rate, threshold=0.7, distance=10000):
    # Normalize the audio samples
    normalized_samples = samples / np.max(np.abs(samples))
    
    # Find peaks in the normalized audio signal
    peaks, _ = find_peaks(normalized_samples, height=threshold, distance=distance)
    return peaks

# Function to play audio and change color
def play_audio_with_lightshow(audio_file):
    # Load the audio file
    song = AudioSegment.from_file(audio_file)
    song = song.set_channels(1)  # Convert to mono
    samples = np.array(song.get_array_of_samples())
    sample_rate = song.frame_rate

    # Detect beats in the audio
    beats = detect_beats(samples, sample_rate)

    # Initialize the audio playback
    audio = sa.WaveObject(samples.tobytes(), num_channels=1, bytes_per_sample=2, sample_rate=sample_rate)
    play_obj = audio.play()

    # Initialize the Tkinter window
    root = tk.Tk()
    root.geometry("800x800")
    canvas = tk.Canvas(root, width=800, height=800)
    canvas.pack()

    # Function to update the color
    def update_color(color):
        canvas.create_rectangle(0, 0, 800, 800, fill=color, outline=color)
        root.update_idletasks()

    # Colors for the light show
    colors = ["red", "green", "blue", "yellow", "purple", "orange", "white", "pink"]

    current_beat = 0
    start_time = time.time()
    
    while play_obj.is_playing():
        current_time = time.time()
        elapsed_time = current_time - start_time
        current_sample = int(elapsed_time * sample_rate)
        
        if current_beat < len(beats) and current_sample >= beats[current_beat]:
            color = colors[current_beat % len(colors)]
            update_color(color)
            current_beat += 1
        
        root.update()

    # Wait for the playback to finish
    play_obj.wait_done()
    root.destroy()

# Upload and play the audio file with light show
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Play audio and change screen color according to beat")
    parser.add_argument("audio_file", type=str, help="Path to the audio file")
    args = parser.parse_args()
    play_audio_with_lightshow(args.audio_file)
