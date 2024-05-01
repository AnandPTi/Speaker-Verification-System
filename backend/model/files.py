from pydub import AudioSegment
import wave
import os

# Input .wav file
input_file = "model/prakash.wav"

# Output folder to save the segments
output_folder = "samples/prakash"
os.makedirs(output_folder, exist_ok=True)

# Load the audio file
audio = AudioSegment.from_wav(input_file)

# Duration of each segment in milliseconds (0.01 seconds)
segment_duration = 2000

# Total duration of the audio in milliseconds
total_duration = len(audio)

# Calculate the number of segments
num_segments = total_duration // segment_duration

# Split the audio into segments
for i in range(num_segments):
    # Calculate the start and end time of the segment
    start_time = i * segment_duration
    end_time = (i + 1) * segment_duration

    # Extract the segment
    segment = audio[start_time:end_time]

    # Save the segment to a new .wav file
    output_file = os.path.join(output_folder, f"{i}.wav")
    segment.export(output_file, format="wav")

print(f"Split {input_file} into {num_segments} segments in {output_folder}.")