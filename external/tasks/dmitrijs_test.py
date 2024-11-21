# region -- Testing sound playback using PsychoPy
import os

from psychopy import visual, core, monitors, sound, prefs

prefs.hardware['audioLib'] = 'PTB'  # Set PTB as the audio backend

# Get the current working directory
current_directory = os.getcwd()
# Define a relative path (e.g., accessing a file in a subdirectory)
relative_path = os.path.join(current_directory, 'thalamus\\task_controller', 'failure_clip.wav')

# Load the .wav file (replace with your file path)
my_sound = sound.Sound(relative_path)
# my_sound = sound.Sound(r"C:\Thalamus\thalamus\task_controller\failure_clip.wav")

# Play the sound
my_sound.play()

# Allow time for the sound to finish playing before the program exits
core.wait(my_sound.getDuration())  # Wait for the sound's duration to finish

# endregion 

trial_failed = []
print(trial_failed != 1)