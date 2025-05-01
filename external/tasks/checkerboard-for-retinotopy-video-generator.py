import cv2
import numpy as np
import random

# Video parameters
frame_width = 640
frame_height = 480
fps = 30
duration = 10  # seconds
output_file = "checkerboard_video.mp4"

# Checkerboard parameters
checkerboard_size = 3  # 3x3 checkerboard
square_size = 50  # Size of each square in pixels
checkerboard_width = checkerboard_size * square_size
checkerboard_height = checkerboard_size * square_size

# Calculate total frames
total_frames = fps * duration

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

def generate_checkerboard():
    """Generate a 3x3 checkerboard pattern."""
    checkerboard = np.zeros((checkerboard_height, checkerboard_width, 3), dtype=np.uint8)
    for i in range(checkerboard_size):
        for j in range(checkerboard_size):
            if (i + j) % 2 == 0:
                x_start = j * square_size
                y_start = i * square_size
                x_end = x_start + square_size
                y_end = y_start + square_size
                checkerboard[y_start:y_end, x_start:x_end] = (255, 255, 255)  # White square
    return checkerboard

# Generate checkerboard pattern
checkerboard = generate_checkerboard()

for frame_idx in range(total_frames):
    # Create a blank frame
    frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    # Randomly decide whether to display the checkerboard
    if random.random() > 0.5:
        # Randomly choose a location for the checkerboard
        x_offset = random.randint(0, frame_width - checkerboard_width)
        y_offset = random.randint(0, frame_height - checkerboard_height)

        # Overlay the checkerboard onto the frame
        frame[y_offset:y_offset + checkerboard_height, x_offset:x_offset + checkerboard_width] = checkerboard

    # Write the frame to the video
    video_writer.write(frame)

# Release the video writer
video_writer.release()

print(f"Video saved as {output_file}")