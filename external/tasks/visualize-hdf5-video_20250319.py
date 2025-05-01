import h5py
import numpy as np
import cv2

# Open the HDF5 file
with h5py.File('C:/Users/bijanadmin/Documents/Dmitrijs/thalamus_data/test_20250319.h5', 'r') as f:
    # Assuming the dataset containing video frames is named 'video_data'
    video_data = f['image']['cam1_eye']['data'][:]
    # You can also read other non-video variables if needed
    # non_video_variable = f['non_video_variable'][:]

# Check the shape of the video data
print(video_data.shape)  # Should be (num_frames, height, width)

# Loop through the frames and display them using OpenCV
num_frames = video_data.shape[0]
for frame_number, frame in enumerate(video_data):
    # Convert the frame to a format suitable for displaying
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    
    # Add the frame number text to the frame
    text = f"Frame {frame_number + 1}/{num_frames}"
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Display the frame
    cv2.imshow('Video', frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Release the OpenCV window
cv2.destroyAllWindows()